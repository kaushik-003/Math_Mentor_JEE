"""
Math Mentor — Streamlit UI
Main entry point for the JEE Advanced problem solver web app.

Run with:  streamlit run app.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

import config
from utils.trace import AgentTracer
from utils.ocr import extract_text_from_image
from utils.asr import transcribe_audio
from agents.parser_agent import ParserAgent
from agents.router_agent import RouterAgent
from agents.solver_agent import SolverAgent
from rag.retriever import Retriever

# ---------------------------------------------------------------------------
# Page config — must be first Streamlit call
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Math Mentor — JEE Solver",
    page_icon="🧮",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

_SS_DEFAULTS: dict = {
    "phase": "input",           # "input" | "clarifying" | "solved"
    "extracted_text": "",
    "extraction_confidence": 1.0,
    "last_file_id": None,       # detect new uploads without re-running OCR/ASR
    "clarification_attempt": 0, # 0 = first parse; 1 = already asked once
    "parser_result": None,
    "router_result": None,
    "rag_results": [],
    "rag_ready": True,
    "current_result": None,
    "tracer": AgentTracer(),
    "feedback_given": False,
    "feedback_type": "",
    "feedback_comment": "",
}

for _k, _v in _SS_DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

ss = st.session_state

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_AGENT_COLORS = {
    "ParserAgent":  "#4A90D9",
    "RouterAgent":  "#E67E22",
    "SolverAgent":  "#27AE60",
    "RAGRetriever": "#8E44AD",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _input_confidence_badge(conf: float) -> str:
    pct = f"{conf:.0%}"
    if conf >= config.OCR_CONFIDENCE_THRESHOLD:
        return f"🟢 Confidence: {pct} — Looks good"
    elif conf >= 0.4:
        return f"🟡 Confidence: {pct} — Please review, extraction may have errors"
    else:
        return f"🔴 Confidence: {pct} — Low confidence, please correct the text before solving"


def _solver_confidence_badge(conf: float) -> str:
    if conf >= 0.9:
        return "🟢 High confidence"
    elif conf >= config.VERIFIER_CONFIDENCE_THRESHOLD:
        return "🟡 Medium confidence — verify the answer"
    else:
        return "🔴 Low confidence — manual verification recommended"


def _reset_pipeline() -> None:
    """Clear all pipeline results and return to input phase."""
    ss.phase = "input"
    ss.parser_result = None
    ss.router_result = None
    ss.rag_results = []
    ss.rag_ready = True
    ss.current_result = None
    ss.tracer = AgentTracer()
    ss.feedback_given = False
    ss.feedback_type = ""
    ss.feedback_comment = ""
    ss.clarification_attempt = 0
    ss.last_file_id = None


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


def _run_pipeline(problem_text: str) -> None:
    """
    Full pipeline: Parser → (HITL #2 if needed) → Router → RAG → Solver.

    Updates session state throughout and calls st.rerun() to trigger
    UI re-renders at phase transitions.
    """
    tracer = AgentTracer()
    ss.tracer = tracer

    with st.spinner("Solving your problem..."):
        # ── Step 1: Parse ──────────────────────────────────────────────────
        parser = ParserAgent(tracer=tracer)
        parsed = parser.parse(problem_text)
        ss.parser_result = parsed

        # ── HITL #2: Clarification gate ────────────────────────────────────
        # Only pause once. If clarification_attempt > 0 we proceed anyway.
        if parsed["needs_clarification"] and ss.clarification_attempt == 0:
            ss.clarification_attempt = 1
            ss.phase = "clarifying"
            st.rerun()
            return  # unreachable after rerun; documents intent

        # ── Step 2: Route ──────────────────────────────────────────────────
        router = RouterAgent(tracer=tracer)
        routing = router.classify(parsed["problem_text"])
        ss.router_result = routing
        topic = routing["topic"] or "algebra"

        # ── Step 3: RAG ────────────────────────────────────────────────────
        retriever = Retriever()
        tracer.start("RAGRetriever")
        rag_results = retriever.search(parsed["problem_text"], topic=routing["topic"])
        tracer.end(
            input_summary=f"[{topic}] {parsed['problem_text'][:60]}",
            output_summary=f"{len(rag_results)} chunks retrieved",
            metadata={"topic": topic, "count": len(rag_results)},
        )
        ss.rag_results = rag_results
        ss.rag_ready = retriever._ready

        # ── Step 4: Solve ──────────────────────────────────────────────────
        solver = SolverAgent(tracer=tracer)
        result = solver.solve(
            problem_text=parsed["problem_text"],
            topic=topic,
            rag_context=[r["text"] for r in rag_results],
        )
        ss.current_result = result
        ss.phase = "solved"

    st.rerun()


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🧮 Math Mentor")
    st.caption("JEE Advanced Problem Solver")
    st.divider()

    mode: str = st.radio(
        "Input Mode",
        ["Text", "Image", "Audio"],
        index=0,
        on_change=_reset_pipeline,
        key="input_mode",
    )

    st.divider()

    # ── Agent Trace ────────────────────────────────────────────────────────
    with st.expander("🔍 Agent Trace", expanded=False):
        steps = ss.tracer.get_steps() if ss.tracer else []
        if steps:
            for step in steps:
                color = _AGENT_COLORS.get(step.agent_name, "#888888")
                inp = step.input_summary[:80].replace("'", "&#39;")
                out = step.output_summary[:80].replace("'", "&#39;")
                st.markdown(
                    f"""<div style="border-left:4px solid {color};padding:6px 10px;
margin-bottom:8px;background:#f8f9fa;border-radius:2px;font-family:monospace;">
<strong>{step.agent_name}</strong>
<span style="color:#888;font-size:0.83em;"> ({step.duration_ms:.0f}ms)</span><br>
<span style="font-size:0.82em;color:#555;">In:&nbsp; {inp}</span><br>
<span style="font-size:0.82em;color:#333;">Out: {out}</span>
</div>""",
                    unsafe_allow_html=True,
                )
            st.caption(f"Total: {ss.tracer.total_duration_ms():.0f}ms across {len(steps)} steps")
        else:
            st.caption("No trace yet — solve a problem first.")

    # ── Retrieved Sources ──────────────────────────────────────────────────
    with st.expander("📚 Retrieved Sources", expanded=False):
        if ss.rag_results:
            for i, r in enumerate(ss.rag_results, 1):
                st.markdown(
                    f"**[{i}] {r['source']}** · `{r['topic']}` · score `{r['score']:.3f}`"
                )
                preview = r["text"][:200]
                st.caption(preview + ("..." if len(r["text"]) > 200 else ""))
                if i < len(ss.rag_results):
                    st.divider()
        else:
            st.caption("No sources retrieved yet.")

# ---------------------------------------------------------------------------
# Main Area
# ---------------------------------------------------------------------------

st.title("🧮 Math Mentor — JEE Problem Solver")
st.divider()

# ── Input Section ────────────────────────────────────────────────────────────

if mode == "Text":
    problem_input: str = st.text_area(
        "Enter your math problem:",
        placeholder="e.g. Solve x² - 5x + 6 = 0  |  Find d/dx [x³ sin x]  |  P(3 heads in 5 tosses)",
        height=120,
        key="text_input_area",
    )
    if st.button(
        "Solve",
        type="primary",
        disabled=not problem_input.strip(),
        key="text_solve_btn",
    ):
        _reset_pipeline()
        ss.extracted_text = problem_input.strip()
        ss.extraction_confidence = 1.0
        _run_pipeline(ss.extracted_text)

elif mode == "Image":
    uploaded_img = st.file_uploader(
        "Upload an image of your math problem (JPG or PNG)",
        type=["jpg", "jpeg", "png"],
        key="img_uploader",
    )

    if uploaded_img is not None:
        file_id = f"{uploaded_img.name}:{uploaded_img.size}"

        if file_id != ss.last_file_id:
            with st.spinner("Extracting text from image..."):
                ocr_result = extract_text_from_image(uploaded_img.read())
            ss.extracted_text = ocr_result["extracted_text"]
            ss.extraction_confidence = ocr_result["confidence"]
            ss.last_file_id = file_id
            # Reset any previous solve results when a new image is uploaded
            _reset_pipeline()
            ss.last_file_id = file_id  # restore after reset

            if ocr_result.get("notes"):
                st.info(f"OCR note: {ocr_result['notes']}")

        if ss.extracted_text:
            st.markdown(_input_confidence_badge(ss.extraction_confidence))
            edited_img_text: str = st.text_area(
                "Extracted text (edit if needed before solving):",
                value=ss.extracted_text,
                height=120,
                key="ocr_edit_area",
            )
            if st.button("Confirm & Solve", type="primary", key="ocr_solve_btn"):
                ss.extracted_text = edited_img_text.strip()
                _run_pipeline(ss.extracted_text)
        else:
            st.error(
                "Could not extract text from the image. "
                "Try a clearer photo or use Text mode to type the problem."
            )

elif mode == "Audio":
    col_up, col_rec = st.columns(2)
    audio_bytes: bytes | None = None
    audio_filename = "audio.wav"
    file_id: str | None = None

    with col_up:
        uploaded_audio = st.file_uploader(
            "Upload audio file",
            type=["mp3", "wav", "m4a", "ogg", "webm"],
            key="audio_uploader",
        )
        if uploaded_audio is not None:
            audio_bytes = uploaded_audio.read()
            audio_filename = uploaded_audio.name
            file_id = f"{uploaded_audio.name}:{uploaded_audio.size}"

    with col_rec:
        try:
            recorded = st.audio_input("Or record audio directly", key="audio_recorder")
            if recorded is not None and audio_bytes is None:
                audio_bytes = recorded.read()
                audio_filename = "recording.wav"
                file_id = f"recording:{len(audio_bytes)}"
        except AttributeError:
            st.caption("Live recording requires Streamlit 1.31+")

    if audio_bytes is not None and file_id is not None:
        if file_id != ss.last_file_id:
            with st.spinner("Transcribing audio..."):
                asr_result = transcribe_audio(audio_bytes, audio_filename)
            # Prefer processed text; fall back to raw transcript
            ss.extracted_text = asr_result["processed_text"] or asr_result["transcript"]
            ss.extraction_confidence = asr_result["confidence"]
            ss.last_file_id = file_id
            _reset_pipeline()
            ss.last_file_id = file_id  # restore after reset

        if ss.extracted_text:
            st.markdown(_input_confidence_badge(ss.extraction_confidence))
            edited_audio_text: str = st.text_area(
                "Transcribed text (edit if needed before solving):",
                value=ss.extracted_text,
                height=120,
                key="asr_edit_area",
            )
            if st.button("Confirm & Solve", type="primary", key="asr_solve_btn"):
                ss.extracted_text = edited_audio_text.strip()
                _run_pipeline(ss.extracted_text)
        else:
            st.error(
                "Could not transcribe the audio. "
                "Try a clearer recording or use Text mode."
            )

# ── HITL #2: Clarification ────────────────────────────────────────────────────

if ss.phase == "clarifying" and ss.parser_result:
    st.divider()
    st.warning("**The problem needs some clarification before it can be solved.**")

    questions = ss.parser_result.get("clarification_questions", [])
    for q in questions:
        st.markdown(f"• {q}")

    clarification: str = st.text_input(
        "Add clarification or missing context:",
        placeholder="e.g. 'x is a positive integer', 'find the exact value'",
        key="clarification_input",
    )

    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Re-submit with clarification", type="primary", key="resubmit_btn"):
            combined = ss.extracted_text + "\n\nAdditional context: " + clarification
            ss.extracted_text = combined
            ss.clarification_attempt = 1
            _run_pipeline(combined)
    with c2:
        if st.button("Skip & Solve Anyway", key="skip_clarify_btn"):
            ss.clarification_attempt = 1
            _run_pipeline(ss.parser_result["problem_text"])

# ── Results ────────────────────────────────────────────────────────────────────

if ss.phase == "solved" and ss.current_result:
    st.divider()

    result = ss.current_result
    router = ss.router_result or {}
    parsed = ss.parser_result or {}

    # ChromaDB availability notice
    if not ss.rag_ready:
        st.info(
            "Knowledge base not loaded — solving without reference context. "
            "Run `python -m rag.embedder` to populate ChromaDB.",
            icon="ℹ️",
        )

    # ── Parsed problem (expandable) ────────────────────────────────────────
    with st.expander("🔎 Parsed Problem", expanded=False):
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**Problem:**\n\n{parsed.get('problem_text', '')}")
            what = parsed.get("what_to_find", "")
            if what:
                st.markdown(f"**Find:** {what}")
        with col_b:
            variables = parsed.get("variables", [])
            if variables:
                st.markdown(f"**Variables:** {', '.join(variables)}")
            constraints = parsed.get("constraints", [])
            if constraints:
                st.markdown(f"**Constraints:** {', '.join(constraints)}")
        if parsed.get("cleaned_from_original"):
            st.caption("✏️ Problem text was cleaned/interpreted from the original input.")

    st.divider()

    # ── Confidence + concept header ────────────────────────────────────────
    conf = result.get("confidence", 0.0)
    topic_label = router.get("topic", "").replace("_", " ").title()
    subtopic_label = router.get("subtopic", "")

    badge_col, concept_col = st.columns([1, 2])
    with badge_col:
        st.markdown(f"**{_solver_confidence_badge(conf)}**")
    with concept_col:
        if topic_label:
            st.markdown(f"📐 **Concept:** {topic_label} — {subtopic_label}")

    st.divider()

    # ── Step-by-step solution ──────────────────────────────────────────────
    st.subheader("Step-by-Step Solution")
    steps = result.get("steps", [])
    if steps:
        for i, step in enumerate(steps, 1):
            st.markdown(f"**Step {i}.** {step}")
    else:
        st.markdown("_No steps available._")

    st.divider()

    # ── Final answer ───────────────────────────────────────────────────────
    st.subheader("Final Answer")
    final = result.get("final_answer", "")
    if final:
        st.success(final)
    else:
        st.warning("Could not determine a final answer.")

    # ── Common mistakes from RAG ───────────────────────────────────────────
    common_chunks = [
        r for r in ss.rag_results
        if "common_mistake" in r.get("source", "").lower()
    ]
    if common_chunks:
        st.divider()
        st.subheader("Common Mistakes to Avoid")
        st.markdown(common_chunks[0]["text"][:500])

    # ── Practice tip ──────────────────────────────────────────────────────
    if topic_label:
        st.divider()
        st.info(
            f"💡 **Practice Tip:** Reinforce this concept by solving more "
            f"{topic_label} problems focused on **{subtopic_label}**."
        )

    st.divider()

    # ── Feedback ──────────────────────────────────────────────────────────
    if not ss.feedback_given:
        st.subheader("Was this solution correct?")
        fb_col1, fb_col2 = st.columns(2)

        with fb_col1:
            if st.button("✅ Correct", key="feedback_correct"):
                ss.feedback_type = "correct"
                ss.feedback_given = True
                st.rerun()

        with fb_col2:
            if st.button("❌ Incorrect", key="feedback_incorrect"):
                ss.feedback_type = "incorrect"
                st.rerun()

        # Show comment box only after Incorrect is clicked, before final submit
        if ss.feedback_type == "incorrect" and not ss.feedback_given:
            comment: str = st.text_input(
                "What was wrong? (optional)",
                key="feedback_comment_input",
            )
            if st.button("Submit feedback", key="feedback_submit"):
                ss.feedback_comment = comment
                ss.feedback_given = True
                st.rerun()

    else:
        if ss.feedback_type == "correct":
            st.success("Thanks! Glad the solution was helpful.")
        else:
            st.info("Thanks for the feedback — your response has been recorded.")
