# College Coordination Copilot

## Problem

College group chats contain important commitments mixed with casual conversation, questions, changes, and unclear statements.

Students can easily lose track of:

- who agreed to do something
- what they agreed to do
- when it is due
- what is still unresolved

A scattered WhatsApp or Discord thread becomes a coordination nightmare the night before a deadline.

## Solution

College Coordination Copilot analyzes messy conversations and converts them into a structured coordination board. Paste a group chat, click **Analyze Commitments**, and Gemma 4 extracts every commitment with the responsible person, task, deadline, status, and the exact source message — plus a dedicated **Needs Clarification** section for unanswered questions and ambiguous items.

## How It Works

```
Conversation
      ↓
   Gemma 4
      ↓
Structured JSON
      ↓
Python validation
      ↓
Coordination Board
```

1. The user pastes a raw group-chat conversation.
2. Gemma 4 receives a strict system prompt and returns structured JSON.
3. Python validates the JSON, strips code fences if present, and normalizes statuses.
4. The Streamlit UI renders commitments as cards and clarifications in a separate section.
5. Every result is traceable back to its original source message.

## Features

- **Commitment extraction** — person, task, deadline, status, and source for each commitment
- **Deadline extraction** — explicit deadlines or "unclear" when none is stated
- **Status detection** — pending, completed, or unclear
- **Source traceability** — every commitment and clarification links to the exact original message
- **Needs Clarification** — unanswered questions, ambiguous responsibilities, and conflicting commitments in a dedicated section
- **Editable local status** — change a commitment's status right in the UI (session-local, no database)
- **Latest-commitment preference** — if someone changes their mind, the latest clear commitment wins

## Tech Stack

- **Python**
- **Streamlit** — UI
- **Google GenAI API** — AI inference
- **Gemma 4** (`gemma-4-26b-a4b-it`) — natural-language understanding and commitment extraction

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure your API key

Copy the example env file and add your Google GenAI API key:

```bash
cp .env.example .env
```

Edit `.env`:

```
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemma-4-26b-a4b-it
GEMINI_FALLBACK_MODEL=
ENABLE_MODEL_FALLBACK=false
```

### 3. Run the app

```bash
streamlit run app.py
```

## Model

**Gemma 4** (`gemma-4-26b-a4b-it`) is the default and primary model. Gemma is responsible for understanding messy human conversation and extracting structured commitments — it turns unstructured chat text into clean JSON that the Python layer can validate and display.

The model name is centralized in `config.py` and controlled by the `GEMINI_MODEL` environment variable, so it can be changed without touching application logic.

### Fallback (optional)

If `ENABLE_MODEL_FALLBACK=true` and `GEMINI_FALLBACK_MODEL` is set, the app will try the fallback model when Gemma 4 is rate-limited or unavailable. The actual model used is always shown in the UI — the app never claims a fallback response came from Gemma.

## Security

- API keys are stored in environment variables via `.env` — **never** in source code.
- `.env` is listed in `.gitignore` and must never be committed to GitHub.
- `.env.example` contains only placeholder values.

## Hackathon Challenge

**Challenge 01 — Best Use of Gemma 4**

College Coordination Copilot makes Gemma 4 a meaningful, central part of the application. Gemma is not a bolted-on chatbot — it is the core engine that understands messy, informal, real-world student conversations and produces structured, validated, traceable commitments. The entire product depends on Gemma's language understanding to solve a problem that traditional rule-based parsing cannot.
