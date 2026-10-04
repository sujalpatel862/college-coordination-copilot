"""Quick test for the Gemma 4 API integration.

Run with:  python test_gemma.py
"""

import sys

from config import MODEL_NAME, GEMINI_API_KEY
from ai_service import analyze_conversation

SAMPLE_CONVERSATION = """Rahul: I'll make the PPT tonight.
Sujal: I'll ask sir about the submission tomorrow.
Aman: Does anyone have the circuit diagram?
Priya: I'll bring the HDMI cable.
Rahul: Actually I can't finish tonight. I'll do it tomorrow morning."""


def main():
    if not GEMINI_API_KEY:
        print("FAIL: GEMINI_API_KEY is not set.")
        sys.exit(1)

    print(f"Model: {MODEL_NAME}")
    print("Sending sample conversation to Gemma 4...\n")

    result, error = analyze_conversation(SAMPLE_CONVERSATION)

    if error:
        print(f"FAIL: {error}")
        sys.exit(1)

    print(f"Model used: {result.model_used}")
    print(f"\nCommitments ({len(result.commitments)}):")
    for c in result.commitments:
        print(f"  - {c.person} | {c.task} | {c.deadline} | {c.status}")
        print(f"    Source: \"{c.source}\"")

    print(f"\nNeeds Clarification ({len(result.needs_clarification)}):")
    for item in result.needs_clarification:
        print(f"  - {item.issue}")
        print(f"    Source: \"{item.source}\"")

    if not result.has_commitments and not result.has_clarifications:
        print("\nWARN: No commitments or clarifications extracted.")
        sys.exit(1)

    print("\nPASS: Gemma 4 integration is working.")


if __name__ == "__main__":
    main()
