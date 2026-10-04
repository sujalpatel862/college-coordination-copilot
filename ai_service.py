"""Gemma 4 analysis service.

Handles prompt construction, API calls, JSON parsing, and validation.
"""

import json
import re
from typing import Tuple

from google import genai
from google.genai import errors as genai_errors

from config import (
    GEMINI_API_KEY,
    MODEL_NAME,
    FALLBACK_MODEL,
    ENABLE_FALLBACK,
    validate_api_key,
)
from models import (
    AnalysisResult,
    Commitment,
    ClarificationItem,
    VALID_STATUSES,
)

validate_api_key()

_client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """You are College Coordination Copilot, an assistant that analyzes college group-chat conversations and extracts structured commitments.

STRICT RULES:
1. NEVER invent a person. Only use names that appear in the conversation.
2. NEVER invent a task. Only extract tasks that were explicitly stated.
3. NEVER invent a deadline. If no deadline is stated, use "unclear".
4. NEVER invent a status. Use "pending", "completed", or "unclear".
5. If information is missing, use "unclear".
6. Questions are NOT commitments. A question like "Does anyone have the circuit diagram?" must go under needs_clarification, NOT commitments.
7. Preserve the exact original source message for every item.
8. If a person changes their commitment, prefer their LATEST clear commitment and ignore the earlier one.
9. Identify unresolved questions under needs_clarification.
10. Identify ambiguous responsibilities under needs_clarification.
11. Identify conflicting commitments under needs_clarification.
12. Conditional commitments (e.g. "if X then I'll do Y") go under needs_clarification unless the condition is clearly met.
13. Return ONLY valid JSON. No markdown, no code fences, no explanations.

OUTPUT FORMAT (return exactly this JSON structure):
{
  "commitments": [
    {
      "person": "name",
      "task": "task description",
      "deadline": "deadline or unclear",
      "status": "pending, completed, or unclear",
      "source": "exact source message"
    }
  ],
  "needs_clarification": [
    {
      "issue": "what needs clarification",
      "source": "exact source message"
    }
  ]
}"""


def _strip_code_fences(text: str) -> str:
    """Remove markdown code fences if Gemma accidentally adds them."""
    text = text.strip()
    fence_pattern = r"^```(?:json)?\s*\n(.*?)\n```$"
    match = re.match(fence_pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


def _extract_json(text: str) -> dict:
    """Parse the JSON from the model response, tolerating code fences."""
    cleaned = _strip_code_fences(text)
    # Try direct parse first.
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    # Fall back: find the first { ... } block.
    json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    raise ValueError("The model did not return valid JSON. Please try again.")


def _validate_structure(raw: dict) -> AnalysisResult:
    """Validate and convert the parsed JSON into an AnalysisResult."""
    result = AnalysisResult()

    commitments_raw = raw.get("commitments", [])
    if isinstance(commitments_raw, list):
        for item in commitments_raw:
            if not isinstance(item, dict):
                continue
            status = str(item.get("status", "unclear")).lower().strip()
            if status not in VALID_STATUSES:
                status = "unclear"
            result.commitments.append(
                Commitment(
                    person=str(item.get("person", "unclear")).strip() or "unclear",
                    task=str(item.get("task", "unclear")).strip() or "unclear",
                    deadline=str(item.get("deadline", "unclear")).strip() or "unclear",
                    status=status,
                    source=str(item.get("source", "")).strip(),
                )
            )

    clarifications_raw = raw.get("needs_clarification", [])
    if isinstance(clarifications_raw, list):
        for item in clarifications_raw:
            if not isinstance(item, dict):
                continue
            result.needs_clarification.append(
                ClarificationItem(
                    issue=str(item.get("issue", "")).strip(),
                    source=str(item.get("source", "")).strip(),
                )
            )

    return result


def _call_model(model_name: str, conversation: str) -> str:
    """Send the prompt to the given model and return raw text."""
    full_prompt = f"{SYSTEM_PROMPT}\n\nConversation:\n{conversation}"
    response = _client.models.generate_content(
        model=model_name,
        contents=full_prompt,
    )
    return response.text


def analyze_conversation(conversation: str) -> Tuple[AnalysisResult, str]:
    """Analyze a conversation and return (result, error_message).

    On success error_message is an empty string. On failure result is an
    empty AnalysisResult and error_message contains a user-friendly message.
    """
    conversation = conversation.strip()
    if not conversation:
        return AnalysisResult(), "Please paste a conversation to analyze."

    models_to_try = [MODEL_NAME]
    if ENABLE_FALLBACK and FALLBACK_MODEL:
        models_to_try.append(FALLBACK_MODEL)

    last_error = ""
    for idx, model_name in enumerate(models_to_try):
        try:
            raw_text = _call_model(model_name, conversation)
            parsed = _extract_json(raw_text)
            result = _validate_structure(parsed)
            result.model_used = model_name
            return result, ""
        except ValueError as exc:
            last_error = str(exc)
            # JSON parse errors are not retryable with a different model.
            break
        except genai_errors.ClientError as exc:
            last_error = _friendly_api_error(exc, model_name)
            if idx < len(models_to_try) - 1:
                continue
        except genai_errors.ServerError as exc:
            last_error = _friendly_api_error(exc, model_name)
            if idx < len(models_to_try) - 1:
                continue
        except Exception as exc:
            last_error = _friendly_api_error(exc, model_name)
            if idx < len(models_to_try) - 1:
                continue

    return AnalysisResult(), last_error


def _friendly_api_error(exc: Exception, model_name: str) -> str:
    """Convert API exceptions into a user-friendly message without secrets."""
    msg = str(exc).lower()
    if "api key" in msg or "unauthorized" in msg or "401" in msg or "403" in msg:
        return "The API key is invalid or unauthorized. Please check your GEMINI_API_KEY."
    if "quota" in msg or "rate" in msg or "429" in msg or "resource" in msg:
        return f"The model '{model_name}' is currently rate-limited or over quota. Please try again in a moment."
    if "not found" in msg or "404" in msg or "model" in msg:
        return f"The model '{model_name}' is unavailable. Check GEMINI_MODEL in your configuration."
    if "timeout" in msg or "deadline" in msg:
        return "The request timed out. Please try again."
    if "network" in msg or "connection" in msg:
        return "A network error occurred. Please check your connection and try again."
    return f"An unexpected error occurred while contacting the AI service. Please try again."
