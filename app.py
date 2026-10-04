"""College Coordination Copilot — Streamlit application.

Turns messy group chats into clear commitments, powered by Gemma 4.
"""

import streamlit as st

from config import MODEL_NAME, FALLBACK_MODEL, ENABLE_FALLBACK
from ai_service import analyze_conversation
from models import AnalysisResult

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="College Coordination Copilot",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Custom CSS — clean, modern, hackathon-polished
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Base */
    .stApp {
        background-color: #0f172a;
        color: #e2e8f0;
    }

    /* Header block */
    .header-block {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem;
    }
    .header-block h1 {
        font-size: 2.4rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.3rem;
        letter-spacing: -0.02em;
    }
    .header-block .subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        font-weight: 400;
    }

    /* Powered badge */
    .powered-badge {
        display: inline-block;
        margin-top: 0.8rem;
        padding: 0.3rem 0.9rem;
        background: linear(135deg, #1e293b, #1e3a5f);
        border: 1px solid #334155;
        border-radius: 999px;
        font-size: 0.78rem;
        color: #7dd3fc;
        font-weight: 500;
    }

    /* Cards */
    .commitment-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 1rem;
        transition: border-color 0.2s;
    }
    .commitment-card:hover {
        border-color: #38bdf8;
    }
    .card-top {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 0.7rem;
        flex-wrap: wrap;
    }
    .person-name {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f1f5f9;
    }
    .status-badge {
        padding: 0.2rem 0.7rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .status-pending {
        background: #155e75;
        color: #67e8f9;
    }
    .status-completed {
        background: #14532d;
        color: #86efac;
    }
    .status-unclear {
        background: #78350f;
        color: #fcd34d;
    }
    .card-task {
        font-size: 0.95rem;
        color: #e2e8f0;
        margin-bottom: 0.5rem;
    }
    .card-meta {
        font-size: 0.82rem;
        color: #94a3b8;
    }
    .card-source {
        margin-top: 0.5rem;
        padding: 0.6rem 0.8rem;
        background: #0f172a;
        border-radius: 8px;
        font-size: 0.8rem;
        color: #cbd5e1;
        font-style: italic;
        border-left: 3px solid #334155;
    }

    /* Clarification cards */
    .clarification-card {
        background: #1c1917;
        border: 1px solid #44403c;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        border-left: 3px solid #f59e0b;
    }
    .clarification-issue {
        font-size: 0.95rem;
        color: #fef3c7;
        font-weight: 500;
        margin-bottom: 0.4rem;
    }

    /* Section headers */
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-top: 2rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .section-count {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748b;
        background: #1e293b;
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
    }

    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 2rem 1rem;
        color: #64748b;
        font-size: 0.95rem;
    }

    /* Spinner text */
    .processing-text {
        text-align: center;
        color: #38bdf8;
        font-size: 1rem;
        padding: 1.5rem 0;
    }

    /* Text area styling */
    .stTextArea > div > div > textarea {
        background-color: #1e293b;
        color: #e2e8f0;
        border: 1px solid #334155;
        border-radius: 10px;
        font-size: 0.9rem;
        min-height: 180px;
    }
    .stTextArea > div > div > textarea:focus {
        border-color: #38bdf8;
        box-shadow: 0 0 0 1px #38bdf8;
    }

    /* Button */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #0284c7, #0ea5e9);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1.5rem;
        font-size: 1.05rem;
        font-weight: 700;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #0369a1, #0284c7);
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(14, 165, 233, 0.3);
    }

    /* Select box for status editing */
    .stSelectbox > div > div {
        background-color: #1e293b;
        color: #e2e8f0;
        border-color: #334155;
    }

    /* Model info bar */
    .model-bar {
        text-align: center;
        font-size: 0.75rem;
        color: #475569;
        margin-top: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _status_badge(status: str) -> str:
    css_class = {
        "pending": "status-pending",
        "completed": "status-completed",
        "unclear": "status-unclear",
    }.get(status, "status-unclear")
    return f'<span class="status-badge {css_class}">{status}</span>'


def _render_commitments(result: AnalysisResult) -> None:
    st.markdown(
        f'<div class="section-header">Commitments '
        f'<span class="section-count">{len(result.commitments)}</span></div>',
        unsafe_allow_html=True,
    )

    if not result.has_commitments:
        st.markdown(
            '<div class="empty-state">No commitments were found in this conversation. '
            "Try pasting a different chat.</div>",
            unsafe_allow_html=True,
        )
        return

    # Allow the user to edit status — session-local.
    for i, c in enumerate(result.commitments):
        col_card, col_status = st.columns([3, 1])

        with col_card:
            st.markdown(
                f"""
                <div class="commitment-card">
                    <div class="card-top">
                        <span class="person-name">{c.person}</span>
                        {_status_badge(st.session_state.get(f"status_{i}", c.status))}
                    </div>
                    <div class="card-task">{c.task}</div>
                    <div class="card-meta">Deadline: {c.deadline}</div>
                    <div class="card-source">"{c.source}"</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_status:
            current = st.session_state.get(f"status_{i}", c.status)
            new_status = st.selectbox(
                "Status",
                options=["pending", "completed", "unclear"],
                index=["pending", "completed", "unclear"].index(current),
                key=f"status_select_{i}",
                label_visibility="collapsed",
            )
            st.session_state[f"status_{i}"] = new_status


def _render_clarifications(result: AnalysisResult) -> None:
    st.markdown(
        f'<div class="section-header">⚠️ Needs Clarification '
        f'<span class="section-count">{len(result.needs_clarification)}</span></div>',
        unsafe_allow_html=True,
    )

    if not result.has_clarifications:
        st.markdown(
            '<div class="empty-state">No items need clarification. Everything looks clear.</div>',
            unsafe_allow_html=True,
        )
        return

    for item in result.needs_clarification:
        st.markdown(
            f"""
            <div class="clarification-card">
                <div class="clarification-issue">{item.issue}</div>
                <div class="card-source">"{item.source}"</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="header-block">
        <h1>COLLEGE COORDINATION COPILOT</h1>
        <div class="subtitle">Turn messy group chats into clear commitments.</div>
        <div class="powered-badge">Powered by Gemma 4</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------
conversation = st.text_area(
    "Paste your college/group chat here...",
    height=200,
    placeholder="e.g.\nRahul: I'll make the PPT tonight.\nSujal: I'll ask sir tomorrow.\nAman: Does anyone have the circuit diagram?",
    label_visibility="collapsed",
)

analyze = st.button("Analyze Commitments", type="primary")

# ---------------------------------------------------------------------------
# Processing
# ---------------------------------------------------------------------------
if analyze:
    if not conversation.strip():
        st.warning("Please paste a conversation to analyze.")
    else:
        # Reset session-local status overrides.
        for key in list(st.session_state.keys()):
            if key.startswith("status_"):
                del st.session_state[key]

        with st.spinner("Gemma 4 is analyzing the conversation..."):
            result, error = analyze_conversation(conversation)

        if error:
            st.error(error)
        else:
            st.success("Analysis complete!")
            _render_commitments(result)
            _render_clarifications(result)

            # Model transparency.
            model_label = result.model_used or MODEL_NAME
            fallback_note = ""
            if result.model_used and result.model_used != MODEL_NAME:
                fallback_note = (
                    f" (fallback model used: {result.model_used})"
                )
            st.markdown(
                f'<div class="model-bar">Analyzed with: {model_label}{fallback_note}</div>',
                unsafe_allow_html=True,
            )

# ---------------------------------------------------------------------------
# Footer model info (before any analysis)
# ---------------------------------------------------------------------------
if not analyze:
    active_models = [MODEL_NAME]
    if ENABLE_FALLBACK and FALLBACK_MODEL:
        active_models.append(FALLBACK_MODEL)
    fallback_display = (
        f" + fallback: {FALLBACK_MODEL}" if ENABLE_FALLBACK and FALLBACK_MODEL else ""
    )
    st.markdown(
        f'<div class="model-bar">Model: {MODEL_NAME}{fallback_display}</div>',
        unsafe_allow_html=True,
    )
