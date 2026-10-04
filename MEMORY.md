# MEMORY.md — Project Memory

## Current Stack

- Python
- Streamlit
- Google GenAI
- Gemma 4

## Current Model

`gemma-4-26b-a4b-it`

## Current API Environment Variable

`GEMINI_API_KEY`

## Important Architectural Decisions

- Gemma handles natural-language understanding.
- Python handles parsing, validation, and application logic.
- Streamlit handles the interface.
- No database is required for MVP.
- No authentication is required.
- Source messages must be preserved for every commitment and clarification.
- Gemma 4 is the default model.
- Model configuration is centralized in `config.py` and controlled by `GEMINI_MODEL` env var.
- Optional fallback model support exists but is disabled by default (`ENABLE_MODEL_FALLBACK=false`).
- When a fallback model is used, the actual model name is shown in the UI — never mislabeled as Gemma.

## File Layout

```
app.py            — Streamlit UI
config.py         — model + environment configuration
ai_service.py     — Gemma API calls, prompt, JSON parsing/validation
models.py         — structured result dataclasses
test_gemma.py     — quick integration test
requirements.txt  — Python dependencies
```

Update this file when important architecture decisions change.
