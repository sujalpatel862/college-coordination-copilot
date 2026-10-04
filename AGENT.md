# AGENT.md — Instructions for AI Coding Agents

## Before You Edit

1. **Inspect every file before modifying it.** Read `app.py`, `test_gemma.py`, `config.py`, `ai_service.py`, `models.py`, and `requirements.txt` first.
2. **Preserve existing functionality.** The Gemma 4 integration works — do not break it.
3. **Avoid unnecessary rewrites.** Small, targeted changes are better than refactors.

## Core Rules

- Keep **Gemma 4** (`gemma-4-26b-a4b-it`) central and default. Never replace it with another model during normal operation.
- Never expose API keys. Use environment variables only (`GEMINI_API_KEY`).
- Test changes after making them.
- Avoid scope creep — this is a one-day hackathon MVP.
- Do not add unnecessary dependencies.
- Keep the architecture understandable: `config.py` (config), `ai_service.py` (AI + parsing), `models.py` (data structures), `app.py` (UI).

## AI Behavior Rules (enforced in the system prompt)

- No hallucinated commitments
- No invented deadlines
- No invented people
- Distinguish questions from commitments
- Prefer the latest changed commitment
- Use "unclear" when information is unavailable
- Preserve source messages
