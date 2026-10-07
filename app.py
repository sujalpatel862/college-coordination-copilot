"""College Coordination Copilot — Streamlit application.

Turns messy group chats into clear commitments, powered by Gemma 4.
"""

import streamlit as st

from config import MODEL_NAME, FALLBACK_MODEL, ENABLE_FALLBACK, get_api_key
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
# Sample Scenarios for 1-click Demo
# ---------------------------------------------------------------------------
SAMPLE_SCENARIOS = {
    "Hackathon Rush": (
        "Rahul: I'll make the PPT tonight.\n"
        "Sujal: I'll ask sir about the submission deadline tomorrow morning.\n"
        "Aman: Does anyone have the circuit diagram?\n"
        "Priya: I'll bring the HDMI cable and test the hardware.\n"
        "Rahul: Actually I can't finish tonight. I'll do it tomorrow morning by 10 AM.\n"
        "Tanmay: If Rahul finishes the PPT, I will review the slides."
    ),
    "Final Year Project": (
        "Kavya: I will complete the dataset preprocessing by Friday 5 PM.\n"
        "Arjun: Who is writing the literature survey section?\n"
        "Neha: I can submit the hardware component bill to the HOD office on Monday.\n"
        "Kavya: Actually Friday is a college holiday, so I will deliver the dataset by Thursday evening instead.\n"
        "Vikram: Did professor approve our project abstract?"
    ),
    "College Fest Team": (
        "Ananya: I am booking the auditorium for Saturday morning.\n"
        "Rohan: I will order the guest mementos and certificates by Wednesday.\n"
        "Dev: Can someone confirm how many guest speakers are attending?\n"
        "Sneha: I will design and print the event banner tonight.\n"
        "Rohan: The vendor said certificates need extra time, so I will collect them on Thursday 2 PM."
    ),
}

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
        padding: 2rem 1rem 1.2rem;
    }
    .header-block h1 {
        font-size: 2.3rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.3rem;
        letter-spacing: -0.02em;
    }
    .header-block .subtitle {
        font-size: 1.05rem;
        color: #94a3b8;
        font-weight: 400;
    }

    /* Powered badge */
    .powered-badge {
        display: inline-block;
        margin-top: 0.7rem;
        padding: 0.3rem 0.9rem;
        background: linear-gradient(135deg, #1e293b, #1e3a5f);
        border: 1px solid #334155;
        border-radius: 999px;
        font-size: 0.8rem;
        color: #7dd3fc;
        font-weight: 600;
    }

    /* Metric Bar */
    .metric-container {
        display: flex;
        gap: 0.75rem;
        margin: 1.5rem 0 1rem;
        flex-wrap: wrap;
    }
    .metric-card {
        flex: 1;
        min-width: 120px;
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        text-align: center;
    }
    .metric-number {
        font-size: 1.5rem;
        font-weight: 800;
        color: #38bdf8;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.04em;
    }

    /* Cards */
    .commitment-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.85rem;
        transition: border-color 0.2s;
    }
    .commitment-card:hover {
        border-color: #38bdf8;
    }
    .card-top {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 0.6rem;
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
        font-weight: 500;
    }
    .card-meta {
        font-size: 0.82rem;
        color: #94a3b8;
    }
    .card-source {
        margin-top: 0.5rem;
        padding: 0.5rem 0.8rem;
        background: #0f172a;
        border-radius: 8px;
        font-size: 0.8rem;
        color: #cbd5e1;
        font-style: italic;
        border-left: 3px solid #38bdf8;
    }

    /* Clarification cards */
    .clarification-card {
        background: #1c1917;
        border: 1px solid #44403c;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        border-left: 4px solid #f59e0b;
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
        margin-top: 1.8rem;
        margin-bottom: 0.8rem;
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
        padding: 1.8rem 1rem;
        color: #64748b;
        font-size: 0.95rem;
        background: #1e293b55;
        border-radius: 10px;
        border: 1px dashed #334155;
    }

    /* Sample pills header */
    .sample-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #94a3b8;
        margin-bottom: 0.4rem;
    }

    /* Model info bar */
    .model-bar {
        text-align: center;
        font-size: 0.78rem;
        color: #64748b;
        margin-top: 2.5rem;
        padding: 0.8rem;
        border-top: 1px solid #1e293b;
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


# ---------------------------------------------------------------------------
# Sidebar: System & API Config
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Settings & Info")
    configured_key = get_api_key()

    if configured_key:
        st.success("API Key detected from environment / .env")
        api_key_override = configured_key
    else:
        st.warning("No API key in .env")
        api_key_override = st.text_input(
            "Enter Gemini API Key:",
            type="password",
            help="API key for Gemma 4 via Google GenAI",
        )

    st.markdown("---")
    st.markdown(f"**Primary Model:** `{MODEL_NAME}`")
    if ENABLE_FALLBACK and FALLBACK_MODEL:
        st.markdown(f"**Fallback Model:** `{FALLBACK_MODEL}` (enabled)")
    else:
        st.markdown("**Fallback:** Disabled")

    st.markdown("---")
    st.markdown(
        """
        **How it works:**
        1. Paste group chat messages.
        2. Gemma 4 extracts clear commitments.
        3. Identifies missing deadlines & questions.
        4. Update task statuses interactively!
        """
    )


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="header-block">
        <h1>🎓 COLLEGE COORDINATION COPILOT</h1>
        <div class="subtitle">Turn messy group chats into clear, actionable commitments.</div>
        <div class="powered-badge">Powered by Gemma 4 (gemma-4-26b-a4b-it)</div>
    </div>
    """,
    unsafe_allow_html=True,
)


def _load_sample(sample_name: str) -> None:
    st.session_state["chat_textarea"] = SAMPLE_SCENARIOS[sample_name]


def _clear_all() -> None:
    st.session_state["chat_textarea"] = ""
    st.session_state["analysis_result"] = None
    st.session_state["analysis_error"] = None


# ---------------------------------------------------------------------------
# Sample Scenarios Loader
# ---------------------------------------------------------------------------
st.markdown('<div class="sample-title">💡 Quick Demo Samples:</div>', unsafe_allow_html=True)
sample_cols = st.columns(len(SAMPLE_SCENARIOS))
for idx, label in enumerate(SAMPLE_SCENARIOS.keys()):
    with sample_cols[idx]:
        st.button(
            f"📋 {label}",
            key=f"sample_btn_{idx}",
            on_click=_load_sample,
            args=(label,),
            use_container_width=True,
        )


# ---------------------------------------------------------------------------
# Input Area
# ---------------------------------------------------------------------------
conversation_text = st.text_area(
    "Paste your college group chat here...",
    height=190,
    placeholder=(
        "Paste messy conversation here...\n\n"
        "e.g.\n"
        "Rahul: I'll make the PPT tonight.\n"
        "Sujal: I'll ask sir tomorrow about the submission.\n"
        "Aman: Does anyone have the circuit diagram?"
    ),
    key="chat_textarea",
)

btn_col1, btn_col2 = st.columns([3, 1])
with btn_col1:
    analyze_clicked = st.button("🚀 Analyze Commitments", type="primary", use_container_width=True)
with btn_col2:
    st.button("🗑️ Clear", on_click=_clear_all, use_container_width=True)


# ---------------------------------------------------------------------------
# Analysis Execution
# ---------------------------------------------------------------------------
if analyze_clicked:
    input_to_analyze = conversation_text.strip()
    if not input_to_analyze:
        st.warning("Please paste a conversation or select a sample above.")
    else:
        with st.spinner("Gemma 4 is analyzing commitments and questions..."):
            result, error = analyze_conversation(
                input_to_analyze,
                api_key=api_key_override or None,
            )

        if error:
            st.session_state["analysis_error"] = error
            st.session_state["analysis_result"] = None
        else:
            st.session_state["analysis_error"] = None
            st.session_state["analysis_result"] = result


# ---------------------------------------------------------------------------
# Render Results (Persistent across Streamlit reruns)
# ---------------------------------------------------------------------------
current_error = st.session_state.get("analysis_error")
current_result: AnalysisResult = st.session_state.get("analysis_result")

if current_error:
    st.error(current_error)

if current_result:
    # Ensure session state for all commitments is always initialized
    for i, c in enumerate(current_result.commitments):
        if f"status_select_{i}" not in st.session_state:
            st.session_state[f"status_select_{i}"] = c.status
        else:
            c.status = st.session_state[f"status_select_{i}"]

    # Metrics summary
    total_commitments = len(current_result.commitments)
    pending_count = sum(1 for c in current_result.commitments if c.status == "pending")
    completed_count = sum(1 for c in current_result.commitments if c.status == "completed")
    unresolved_count = len(current_result.needs_clarification)

    st.markdown(
        f"""
        <div class="metric-container">
            <div class="metric-card">
                <div class="metric-number">{total_commitments}</div>
                <div class="metric-label">Commitments</div>
            </div>
            <div class="metric-card">
                <div class="metric-number">{pending_count}</div>
                <div class="metric-label">Pending</div>
            </div>
            <div class="metric-card">
                <div class="metric-number">{completed_count}</div>
                <div class="metric-label">Completed</div>
            </div>
            <div class="metric-card">
                <div class="metric-number" style="color: #f59e0b;">{unresolved_count}</div>
                <div class="metric-label">Clarifications</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Filter control
    filter_col, _ = st.columns([2, 2])
    with filter_col:
        status_filter = st.selectbox(
            "Filter Commitments:",
            options=["All", "pending", "completed", "unclear"],
            index=0,
            key="status_filter",
        )

    # 1. Commitments Section
    filtered_commitments = [
        (i, c) for i, c in enumerate(current_result.commitments)
        if status_filter == "All" or c.status == status_filter
    ]

    st.markdown(
        f'<div class="section-header">📌 Commitments '
        f'<span class="section-count">{len(filtered_commitments)} of {total_commitments}</span></div>',
        unsafe_allow_html=True,
    )

    if not current_result.has_commitments:
        st.markdown(
            '<div class="empty-state">No commitments were found in this conversation. '
            "Try pasting a different chat.</div>",
            unsafe_allow_html=True,
        )
    elif not filtered_commitments:
        st.markdown(
            f'<div class="empty-state">No commitments with status "{status_filter}".</div>',
            unsafe_allow_html=True,
        )
    else:
        for i, c in filtered_commitments:
            col_card, col_status = st.columns([3, 1])

            with col_card:
                st.markdown(
                    f"""
                    <div class="commitment-card">
                        <div class="card-top">
                            <span class="person-name">{c.person}</span>
                            {_status_badge(c.status)}
                        </div>
                        <div class="card-task">{c.task}</div>
                        <div class="card-meta">📅 Deadline: <strong>{c.deadline}</strong></div>
                        <div class="card-source">"{c.source}"</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col_status:
                options = ["pending", "completed", "unclear"]
                current_idx = options.index(c.status) if c.status in options else 0

                st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)
                new_status = st.selectbox(
                    "Update Status",
                    options=options,
                    index=current_idx,
                    key=f"status_select_{i}",
                    label_visibility="collapsed",
                )
                c.status = new_status

    # 2. Needs Clarification Section
    st.markdown(
        f'<div class="section-header">⚠️ Needs Clarification '
        f'<span class="section-count">{len(current_result.needs_clarification)}</span></div>',
        unsafe_allow_html=True,
    )

    if not current_result.has_clarifications:
        st.markdown(
            '<div class="empty-state">No items need clarification. Everything looks clear!</div>',
            unsafe_allow_html=True,
        )
    else:
        for item in current_result.needs_clarification:
            st.markdown(
                f"""
                <div class="clarification-card">
                    <div class="clarification-issue">❓ {item.issue}</div>
                    <div class="card-source">"{item.source}"</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # 3. Share / Export Section
    st.markdown("---")
    with st.expander("📋 Export / Copy for WhatsApp & Discord"):
        st.markdown("Copy the structured action items directly into your group chat:")
        st.code(current_result.to_markdown(), language="markdown")

    # Model transparency info
    model_label = current_result.model_used or MODEL_NAME
    fallback_note = ""
    if current_result.model_used and current_result.model_used != MODEL_NAME:
        fallback_note = f" (fallback model used: {current_result.model_used})"
    st.markdown(
        f'<div class="model-bar">Analyzed with: <strong>{model_label}</strong>{fallback_note}</div>',
        unsafe_allow_html=True,
    )
else:
    # Model bar before analysis
    active_models = [MODEL_NAME]
    fallback_display = (
        f" + fallback: {FALLBACK_MODEL}" if ENABLE_FALLBACK and FALLBACK_MODEL else ""
    )
    st.markdown(
        f'<div class="model-bar">Active Model: <strong>{MODEL_NAME}</strong>{fallback_display}</div>',
        unsafe_allow_html=True,
    )
