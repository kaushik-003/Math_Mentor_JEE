"""
Math Mentor — Streamlit UI
Main entry point for the JEE Advanced problem solver web app.

Run with:  streamlit run app.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

from datetime import datetime
from uuid import uuid4

import config
from utils.trace import AgentTracer, TraceStep
from utils.ocr import extract_text_from_image
from utils.asr import transcribe_audio
from agents.guardrail_agent import GuardrailAgent
from agents.parser_agent import ParserAgent
from agents.router_agent import RouterAgent
from agents.solver_agent import SolverAgent
from agents.verifier_agent import VerifierAgent
from agents.refiner_agent import RefinerAgent
from agents.explainer_agent import ExplainerAgent
from rag.retriever import Retriever
from memory.store import MemoryStore

# ---------------------------------------------------------------------------
# Page config — must be first Streamlit call
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Math Mentor — JEE Solver",
    page_icon="🧮",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Auto-build knowledge base on first boot (cached across reruns)
# ---------------------------------------------------------------------------

@st.cache_resource
def init_knowledge_base():
    """Build the RAG knowledge base once per app session. Cached across reruns."""
    from rag.embedder import build_knowledge_base
    return build_knowledge_base()

init_knowledge_base()

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

_SS_DEFAULTS: dict = {
    "phase": "input",           # "input"|"clarifying"|"reviewing"|"solved"|"blocked"|"hint_shown"
    "learning_mode": "solve",   # "solve"|"hint"
    "extracted_text": "",
    "extraction_confidence": 1.0,
    "last_file_id": None,
    "clarification_attempt": 0,
    "parser_result": None,
    "router_result": None,
    "rag_results": [],
    "rag_ready": True,
    "current_result": None,     # most recent solver/refiner result
    "tracer": AgentTracer(),
    "feedback_given": False,
    "feedback_type": "",
    "feedback_comment": "",
    # Phase 4 additions
    "guardrail_result": None,
    "verifier_result": None,
    "refiner_result": None,
    "explainer_result": None,
    "verifier_crashed": False,
    "refiner_crashed": False,
    "hitl3_editing": False,
    "hitl3_edited_answer": "",
    # Hint mode state
    "hint_result": None,
    "hint_extra": None,
    "hint_problem_text": "",
    "hint_topic": "",
    "hint_rag_context": [],
    # Memory (Phase 5)
    "current_interaction_id": None,
    "memory_matches": [],
}

for _k, _v in _SS_DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

ss = st.session_state

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_AGENT_COLORS = {
    "GuardrailAgent":  "#E74C3C",   # red
    "ParserAgent":     "#4A90D9",   # blue
    "RouterAgent":     "#E67E22",   # orange
    "RAGRetriever":    "#8E44AD",   # purple
    "SolverAgent":     "#27AE60",   # green
    "VerifierAgent":   "#2980B9",   # steel blue
    "RefinerAgent":    "#F39C12",   # amber
    "ExplainerAgent":  "#16A085",   # teal
    "HintAgent":       "#D35400",   # dark orange
}

_DIFFICULTY_COLORS = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}

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
    ss.guardrail_result = None
    ss.verifier_result = None
    ss.refiner_result = None
    ss.explainer_result = None
    ss.verifier_crashed = False
    ss.refiner_crashed = False
    ss.hitl3_editing = False
    ss.hitl3_edited_answer = ""
    ss.hint_result = None
    ss.hint_extra = None
    ss.hint_problem_text = ""
    ss.hint_topic = ""
    ss.hint_rag_context = []
    ss.current_interaction_id = None
    ss.memory_matches = []


def _run_explainer_and_finish() -> None:
    """
    Run ExplainerAgent on ss.current_result and transition to 'solved' phase.
    Called from HITL #3 button handlers (approve / submit edit).
    """
    problem_text = (ss.parser_result or {}).get("problem_text", ss.extracted_text)
    topic = (ss.router_result or {}).get("topic") or "algebra"
    rag_context = [r["text"] for r in ss.rag_results]

    with st.spinner("Generating explanation..."):
        try:
            explainer = ExplainerAgent(tracer=ss.tracer)
            ss.explainer_result = explainer.explain(problem_text, topic, ss.current_result, rag_context)
        except Exception:
            ss.explainer_result = None

    ss.phase = "solved"
    _save_current_interaction()
    st.rerun()


def _search_memory(problem_text: str) -> None:
    """Search memory for similar past problems. Stores results in ss.memory_matches."""
    try:
        store = MemoryStore()
        ss.memory_matches = store.find_similar(problem_text)
    except Exception:
        ss.memory_matches = []


def _save_current_interaction() -> None:
    """Build an interaction dict from session state and persist to memory + vector store."""
    try:
        store = MemoryStore()
        interaction = {
            "id": str(uuid4()),
            "timestamp": datetime.now().isoformat(),
            "input_type": ss.get("input_mode", "text").lower(),
            "raw_input": ss.extracted_text,
            "parsed_question": (ss.parser_result or {}).get("problem_text", ""),
            "topic": (ss.router_result or {}).get("topic", ""),
            "subtopic": (ss.router_result or {}).get("subtopic", ""),
            "retrieved_context_sources": [r["source"] for r in ss.rag_results],
            "solution": ss.current_result,
            "verifier_outcome": {
                "is_correct": ss.verifier_result.get("is_correct") if ss.verifier_result else None,
                "confidence": ss.verifier_result.get("confidence") if ss.verifier_result else None,
                "was_refined": ss.refiner_result is not None,
            },
            "user_feedback": {"rating": None, "comment": "", "timestamp": None},
            "learning_mode": ss.learning_mode,
        }
        ss.current_interaction_id = store.save_interaction(interaction)
        store.add_to_vector_store(interaction["id"], interaction["parsed_question"])
    except Exception as e:
        print(f"[Memory] Failed to save interaction: {e}")


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


def _run_pipeline(problem_text: str) -> None:
    """
    Full pipeline (sequential):
      Guardrail → Parser → (HITL #2) → Router → RAG
      → [Solve mode: Solver → Verifier → (Refiner) → (HITL #3) → Explainer]
      → [Hint mode:  HintAgent → Display]

    Updates session state and calls st.rerun() at every phase transition.
    """
    tracer = AgentTracer()
    ss.tracer = tracer

    # ── Memory search (before any agents) ────────────────────────────
    _search_memory(problem_text)

    with st.spinner("Screening input & parsing problem..."):

        # ── Step 0: Guardrail ───────────────────────────────────────────
        guardrail = GuardrailAgent(tracer=tracer)
        guard = guardrail.screen(problem_text)
        ss.guardrail_result = guard

        if not guard["is_valid"]:
            ss.phase = "blocked"
            st.rerun()
            return

        # ── Step 1: Parser ──────────────────────────────────────────────
        parser = ParserAgent(tracer=tracer)
        parsed = parser.parse(problem_text)
        ss.parser_result = parsed

        if parsed["needs_clarification"] and ss.clarification_attempt == 0:
            ss.clarification_attempt = 1
            ss.phase = "clarifying"
            st.rerun()
            return

    with st.spinner("Classifying topic & retrieving knowledge..."):

        # ── Step 2: Router ──────────────────────────────────────────────
        router = RouterAgent(tracer=tracer)
        routing = router.classify(parsed["problem_text"])
        ss.router_result = routing
        topic = routing["topic"] or "algebra"

        # ── Step 3: RAG ────────────────────────────────────────────────
        import time
        retriever = Retriever()
        t0 = time.time()
        rag_results = retriever.search(parsed["problem_text"], topic=None, top_k=config.RAG_TOP_K)
        rag_duration_ms = (time.time() - t0) * 1000

        rag_step = TraceStep(
            agent_name="RAGRetriever",
            input_summary=f"[unfiltered] {parsed['problem_text'][:60]}",
            output_summary=f"{len(rag_results)} chunks retrieved",
            duration_ms=round(rag_duration_ms, 1),
            metadata={"topic": topic, "count": len(rag_results), "filtered": False},
        )
        tracer.steps.append(rag_step)

        ss.rag_results = rag_results
        ss.rag_ready = retriever._ready
        rag_context = [r["text"] for r in rag_results]

        # Inject memory context from similar past solutions
        if ss.memory_matches:
            best = ss.memory_matches[0]
            memory_ctx = (
                f"Previously solved similar problem:\n"
                f"Q: {best['parsed_question']}\n"
                f"A: {best['solution']['final_answer']}"
            )
            rag_context.append(memory_ctx)

    # ── Branch: Hint mode ────────────────────────────────────────────────
    if ss.learning_mode == "hint":
        with st.spinner("Generating hints..."):
            ss.hint_problem_text = parsed["problem_text"]
            ss.hint_topic = topic
            ss.hint_rag_context = rag_context

            explainer = ExplainerAgent(tracer=tracer)
            ss.hint_result = explainer.hint(
                problem_text=parsed["problem_text"],
                topic=topic,
                rag_context=rag_context,
            )
            ss.hint_extra = None
            ss.phase = "hint_shown"

        _save_current_interaction()
        st.rerun()
        return

    # ── Branch: Solve mode (full pipeline) ───────────────────────────────
    with st.spinner("Solving your problem..."):

        # ── Step 4: Solve ────────────────────────────────────────────────
        solver = SolverAgent(tracer=tracer)
        result = solver.solve(
            problem_text=parsed["problem_text"],
            topic=topic,
            rag_context=rag_context,
        )
        ss.current_result = result

        # ── Step 5: Verify ───────────────────────────────────────────────
        verifier_result = None
        try:
            verifier = VerifierAgent(tracer=tracer)
            verifier_result = verifier.verify(
                problem_text=parsed["problem_text"],
                topic=topic,
                solver_solution=result,
                rag_context=rag_context,
            )
            ss.verifier_result = verifier_result
            ss.verifier_crashed = False
        except Exception:
            ss.verifier_crashed = True
            ss.verifier_result = None

        # ── Step 6: Refine if needed ─────────────────────────────────────
        needs_hitl3 = False

        if verifier_result is not None and not verifier_result["is_correct"]:
            try:
                refiner = RefinerAgent(tracer=tracer)
                refined = refiner.refine(
                    problem_text=parsed["problem_text"],
                    topic=topic,
                    failed_solution=result,
                    verifier_issues=verifier_result["issues"],
                    rag_context=rag_context,
                )
                ss.refiner_result = refined
                ss.current_result = refined
                ss.refiner_crashed = False

                verifier2 = VerifierAgent(tracer=tracer)
                verifier_result2 = verifier2.verify(
                    problem_text=parsed["problem_text"],
                    topic=topic,
                    solver_solution=refined,
                    rag_context=rag_context,
                )
                ss.verifier_result = verifier_result2

                needs_hitl3 = (
                    not verifier_result2["is_correct"]
                    or verifier_result2["confidence"] < config.VERIFIER_CONFIDENCE_THRESHOLD
                )

            except Exception:
                ss.refiner_crashed = True
                ss.refiner_result = None
                needs_hitl3 = True

        elif verifier_result is not None:
            needs_hitl3 = verifier_result["confidence"] < config.VERIFIER_CONFIDENCE_THRESHOLD

        # ── Step 7: HITL #3 gate ─────────────────────────────────────────
        if needs_hitl3:
            ss.phase = "reviewing"
            st.rerun()
            return

        # ── Step 8: Explain ──────────────────────────────────────────────
        try:
            explainer = ExplainerAgent(tracer=tracer)
            ss.explainer_result = explainer.explain(
                problem_text=parsed["problem_text"],
                topic=topic,
                verified_solution=ss.current_result,
                rag_context=rag_context,
            )
        except Exception:
            ss.explainer_result = None

        ss.phase = "solved"
        _save_current_interaction()

    st.rerun()


def _run_full_solve_from_hint() -> None:
    """Run the full Solve pipeline when user clicks 'Show Full Solution' from hint mode."""
    tracer = ss.tracer
    problem_text = ss.hint_problem_text
    topic = ss.hint_topic
    rag_context = ss.hint_rag_context

    with st.spinner("Solving your problem..."):

        solver = SolverAgent(tracer=tracer)
        result = solver.solve(
            problem_text=problem_text,
            topic=topic,
            rag_context=rag_context,
        )
        ss.current_result = result

        verifier_result = None
        try:
            verifier = VerifierAgent(tracer=tracer)
            verifier_result = verifier.verify(
                problem_text=problem_text,
                topic=topic,
                solver_solution=result,
                rag_context=rag_context,
            )
            ss.verifier_result = verifier_result
            ss.verifier_crashed = False
        except Exception:
            ss.verifier_crashed = True
            ss.verifier_result = None

        needs_hitl3 = False

        if verifier_result is not None and not verifier_result["is_correct"]:
            try:
                refiner = RefinerAgent(tracer=tracer)
                refined = refiner.refine(
                    problem_text=problem_text,
                    topic=topic,
                    failed_solution=result,
                    verifier_issues=verifier_result["issues"],
                    rag_context=rag_context,
                )
                ss.refiner_result = refined
                ss.current_result = refined
                ss.refiner_crashed = False

                verifier2 = VerifierAgent(tracer=tracer)
                verifier_result2 = verifier2.verify(
                    problem_text=problem_text,
                    topic=topic,
                    solver_solution=refined,
                    rag_context=rag_context,
                )
                ss.verifier_result = verifier_result2

                needs_hitl3 = (
                    not verifier_result2["is_correct"]
                    or verifier_result2["confidence"] < config.VERIFIER_CONFIDENCE_THRESHOLD
                )

            except Exception:
                ss.refiner_crashed = True
                ss.refiner_result = None
                needs_hitl3 = True

        elif verifier_result is not None:
            needs_hitl3 = verifier_result["confidence"] < config.VERIFIER_CONFIDENCE_THRESHOLD

        if needs_hitl3:
            ss.phase = "reviewing"
            st.rerun()
            return

        try:
            explainer = ExplainerAgent(tracer=tracer)
            ss.explainer_result = explainer.explain(
                problem_text=problem_text,
                topic=topic,
                verified_solution=ss.current_result,
                rag_context=rag_context,
            )
        except Exception:
            ss.explainer_result = None

        ss.phase = "solved"
        _save_current_interaction()

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

    _LEARNING_LABELS = {
        "solve": "📖 Solve — Full step-by-step solution",
        "hint":  "💡 Hint & Guide — Hints and approach only",
    }
    _LEARNING_KEYS = list(_LEARNING_LABELS.keys())
    _LEARNING_DISPLAY = list(_LEARNING_LABELS.values())
    _current_learning_index = _LEARNING_KEYS.index(ss.learning_mode)

    st.caption("📚 Learning Mode")
    selected_learning_label = st.radio(
        "Learning Mode",
        _LEARNING_DISPLAY,
        index=_current_learning_index,
        key="learning_mode_radio",
        label_visibility="collapsed",
    )
    ss.learning_mode = _LEARNING_KEYS[_LEARNING_DISPLAY.index(selected_learning_label)]

    st.divider()

    # ── Agent Trace ────────────────────────────────────────────────────
    _learning_display_names = {"solve": "Solve", "hint": "Hint & Guide"}
    with st.expander(f"🔍 Agent Trace — 📚 Mode: {_learning_display_names[ss.learning_mode]}", expanded=False):
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

    # ── Retrieved Sources ──────────────────────────────────────────────
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

    # ── Memory Panel ──────────────────────────────────────────────────
    with st.expander("🧠 Memory", expanded=False):
        try:
            _mem_stats = MemoryStore().get_stats()
            st.metric("Total Problems Solved", _mem_stats["total"])
            st.metric("Correct Answers", _mem_stats["correct"])

            if _mem_stats["by_topic"]:
                st.write("**By Topic:**")
                for _topic, _count in _mem_stats["by_topic"].items():
                    st.write(f"  {_topic}: {_count}")

            if st.button("🗑️ Clear Memory", key="clear_memory_btn"):
                MemoryStore().clear()
                st.success("Memory cleared!")
                st.rerun()
        except Exception:
            st.caption("Memory unavailable.")

# ---------------------------------------------------------------------------
# Main Area
# ---------------------------------------------------------------------------

st.title("🧮 Math Mentor — JEE Problem Solver")
st.divider()

# ── Input Section ─────────────────────────────────────────────────────────────

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
        image_file_id = f"{uploaded_img.name}:{uploaded_img.size}"

        if image_file_id != ss.last_file_id:
            with st.spinner("Extracting text from image..."):
                ocr_result = extract_text_from_image(uploaded_img.read())
            ss.extracted_text = ocr_result["extracted_text"]
            ss.extraction_confidence = ocr_result["confidence"]
            ss.last_file_id = image_file_id
            _reset_pipeline()
            ss.last_file_id = image_file_id

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
    audio_file_id: str | None = None

    with col_up:
        uploaded_audio = st.file_uploader(
            "Upload audio file",
            type=["mp3", "wav", "m4a", "ogg", "webm"],
            key="audio_uploader",
        )
        if uploaded_audio is not None:
            audio_bytes = uploaded_audio.read()
            audio_filename = uploaded_audio.name
            audio_file_id = f"{uploaded_audio.name}:{uploaded_audio.size}"

    with col_rec:
        try:
            recorded = st.audio_input("Or record audio directly", key="audio_recorder")
            if recorded is not None and audio_bytes is None:
                audio_bytes = recorded.read()
                audio_filename = "recording.wav"
                audio_file_id = f"recording:{len(audio_bytes)}"
        except AttributeError:
            st.caption("Live recording requires Streamlit 1.31+")

    if audio_bytes is not None and audio_file_id is not None:
        if audio_file_id != ss.last_file_id:
            with st.spinner("Transcribing audio..."):
                asr_result = transcribe_audio(audio_bytes, audio_filename)
            ss.extracted_text = asr_result["processed_text"] or asr_result["transcript"]
            ss.extraction_confidence = asr_result["confidence"]
            ss.last_file_id = audio_file_id
            _reset_pipeline()
            ss.last_file_id = audio_file_id

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

# ── Blocked by Guardrail ──────────────────────────────────────────────────────

if ss.phase == "blocked" and ss.guardrail_result:
    st.divider()
    guard = ss.guardrail_result
    category_labels = {
        "off_topic":    "Off-topic input",
        "out_of_scope": "Out of scope",
        "harmful":      "Unsafe input detected",
        "too_vague":    "Input too vague",
    }
    label = category_labels.get(guard["category"], "Invalid input")
    st.error(f"**{label}**\n\n{guard['reason']}")
    if st.button("Try a different problem", key="guardrail_retry_btn"):
        _reset_pipeline()
        st.rerun()

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

# ── HITL #3: Verification Review ─────────────────────────────────────────────

if ss.phase == "reviewing" and ss.current_result:
    st.divider()
    st.warning("⚠️ I'm not fully confident in this answer. Please review before we continue.")

    result = ss.current_result
    verifier = ss.verifier_result or {}

    # Show the solution under review
    with st.expander("📋 Solution Under Review", expanded=True):
        steps = result.get("steps", [])
        if steps:
            for i, step in enumerate(steps, 1):
                st.markdown(f"**Step {i}.** {step}")
        st.markdown(f"**Proposed Answer:** {result.get('final_answer', '_No answer_')}")

    # Show verifier issues if any
    issues = verifier.get("issues", [])
    if issues:
        st.subheader("Issues Found")
        for iss in issues:
            severity = iss.get("severity", "low")
            icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")
            step_idx = iss.get("step_index", "?")
            st.markdown(f"{icon} **Step {step_idx}:** {iss.get('issue', '')}")

    conf = verifier.get("confidence", result.get("confidence", 0.0))
    st.caption(f"Verifier confidence: {conf:.0%}")

    st.divider()

    # Three-button HITL #3 decision
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✅ Approve anyway", key="hitl3_approve"):
            ss.hitl3_editing = False
            _run_explainer_and_finish()

    with col2:
        if st.button("✏️ Edit solution", key="hitl3_edit"):
            ss.hitl3_editing = True
            st.rerun()

    with col3:
        if st.button("❌ Reject", key="hitl3_reject"):
            _reset_pipeline()
            st.rerun()

    # Editing sub-form (shown only when user clicked "Edit solution")
    if ss.hitl3_editing:
        st.divider()
        edited_answer = st.text_area(
            "Enter the corrected final answer:",
            value=ss.current_result.get("final_answer", ""),
            height=80,
            key="hitl3_edit_area",
        )
        if st.button("Submit edit", type="primary", key="hitl3_submit"):
            ss.hitl3_edited_answer = edited_answer.strip()
            # Patch the current result with the human-corrected answer
            patched = dict(ss.current_result)
            patched["final_answer"] = ss.hitl3_edited_answer
            patched["steps"] = patched.get("steps", []) + [
                f"[Human correction] Final answer updated to: {ss.hitl3_edited_answer}"
            ]
            ss.current_result = patched
            ss.hitl3_editing = False
            _run_explainer_and_finish()

# ── Hint Mode Results ─────────────────────────────────────────────────────────

if ss.phase == "hint_shown" and ss.hint_result:
    st.divider()

    # ── Memory: similar past problem ─────────────────────────────────
    if ss.memory_matches:
        best = ss.memory_matches[0]
        st.info(f"Similar problem found! (Similarity: {best['similarity_score']:.0%})")
        with st.expander("Previously solved similar problem", expanded=False):
            st.write(f"**Question:** {best['parsed_question']}")
            st.write(f"**Answer:** {best['solution']['final_answer']}")
            st.write(f"**Feedback:** {best['user_feedback'].get('rating') or 'No feedback yet'}")

    hint = ss.hint_result
    diff_icon = _DIFFICULTY_COLORS.get(hint.get("difficulty", ""), "")
    concept = hint.get("concept", "")
    est_time = hint.get("estimated_time", "")

    if concept:
        st.markdown(f"📐 **{concept}** {diff_icon} · ⏱️ {est_time}")
        st.divider()

    st.markdown(hint.get("hint", ""))

    if ss.hint_extra:
        st.divider()
        st.markdown("### 💡 Additional Hint")
        st.markdown(ss.hint_extra.get("hint", ""))

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔓 Show Full Solution", type="primary", key="show_full_solution_btn"):
            _run_full_solve_from_hint()
    with col2:
        if st.button("💡 Give Me Another Hint", key="extra_hint_btn"):
            with st.spinner("Generating additional hint..."):
                hint_agent = ExplainerAgent(tracer=ss.tracer)
                ss.hint_extra = hint_agent.hint(
                    problem_text=ss.hint_problem_text,
                    topic=ss.hint_topic,
                    rag_context=ss.hint_rag_context,
                    extra_nudge=True,
                )
            st.rerun()

# ── Results ────────────────────────────────────────────────────────────────────

if ss.phase == "solved" and ss.current_result:
    st.divider()

    # ── Memory: similar past problem ─────────────────────────────────
    if ss.memory_matches:
        best = ss.memory_matches[0]
        st.info(f"Similar problem found! (Similarity: {best['similarity_score']:.0%})")
        with st.expander("Previously solved similar problem", expanded=False):
            st.write(f"**Question:** {best['parsed_question']}")
            st.write(f"**Answer:** {best['solution']['final_answer']}")
            st.write(f"**Feedback:** {best['user_feedback'].get('rating') or 'No feedback yet'}")

    result = ss.current_result
    router = ss.router_result or {}
    parsed = ss.parser_result or {}
    verifier = ss.verifier_result or {}
    explainer = ss.explainer_result or {}

    # ChromaDB availability notice
    if not ss.rag_ready:
        st.info(
            "Knowledge base not loaded — solving without reference context. "
            "Run `python -m rag.embedder` to populate ChromaDB.",
            icon="ℹ️",
        )

    # Verifier crash warning
    if ss.verifier_crashed:
        st.warning(
            "Verification step encountered an error — showing solver output directly. "
            "Please double-check the answer.",
            icon="⚠️",
        )

    # Refiner crash warning
    if ss.refiner_crashed:
        st.warning(
            "Refinement step encountered an error — the original solver output is shown. "
            "Issues may still be present.",
            icon="⚠️",
        )

    # ── Parsed problem (expandable) ─────────────────────────────────────
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

    # ── Header: confidence + verification status + concept ──────────────
    conf = result.get("confidence", 0.0)
    topic_label = router.get("topic", "").replace("_", " ").title()
    subtopic_label = router.get("subtopic", "")
    difficulty = explainer.get("difficulty", "")
    concept = explainer.get("concept", "")

    badge_col, verify_col, concept_col = st.columns([1, 1, 2])

    with badge_col:
        st.markdown(f"**{_solver_confidence_badge(conf)}**")

    with verify_col:
        if not ss.verifier_crashed and verifier:
            if verifier.get("is_correct", True):
                vconf = verifier.get("confidence", 0.0)
                if vconf >= config.VERIFIER_CONFIDENCE_THRESHOLD:
                    st.markdown("**Verified ✅**")
                else:
                    st.markdown("**Needs Review ⚠️**")
            else:
                # Refiner ran and fixed it — check latest verifier
                if ss.refiner_result and verifier.get("is_correct", False):
                    st.markdown("**Verified ✅** _(after refinement)_")
                else:
                    st.markdown("**Needs Review ⚠️**")

    with concept_col:
        if concept:
            diff_icon = _DIFFICULTY_COLORS.get(difficulty, "")
            st.markdown(f"📐 **{concept}** {diff_icon}")
        elif topic_label:
            st.markdown(f"📐 **Concept:** {topic_label} — {subtopic_label}")

    st.divider()

    # ── Refiner disclosure ───────────────────────────────────────────────
    if ss.refiner_result:
        corrections = ss.refiner_result.get("corrections_made", [])
        with st.expander("🔄 Solution was refined after initial verification", expanded=False):
            if corrections:
                for c in corrections:
                    st.markdown(f"- {c}")
            else:
                st.caption("Solution was re-computed but no specific corrections were recorded.")

    # ── Main explanation (from Explainer) or fallback (raw solver steps) ─
    if explainer.get("explanation"):
        st.markdown(explainer["explanation"])
    else:
        # Fallback to raw solver steps if Explainer failed or wasn't run
        st.subheader("Step-by-Step Solution")
        steps = result.get("steps", [])
        if steps:
            for i, step in enumerate(steps, 1):
                st.markdown(f"**Step {i}.** {step}")
        else:
            st.markdown("_No steps available._")

        # RAG-based common mistakes fallback
        common_chunks = [
            r for r in ss.rag_results
            if "common_mistake" in r.get("source", "").lower()
        ]
        if common_chunks:
            st.divider()
            st.subheader("Common Mistakes to Avoid")
            st.markdown(common_chunks[0]["text"][:500])

        if topic_label:
            st.divider()
            st.info(
                f"💡 **Practice Tip:** Reinforce this concept by solving more "
                f"{topic_label} problems focused on **{subtopic_label}**."
            )

    st.divider()

    # ── Final answer ─────────────────────────────────────────────────────
    st.subheader("Final Answer")
    final = result.get("final_answer", "")
    if final:
        st.success(final)
    else:
        st.warning("Could not determine a final answer.")

    st.divider()

    # ── Feedback ─────────────────────────────────────────────────────────
    if not ss.feedback_given:
        st.subheader("Was this solution correct?")
        fb_col1, fb_col2 = st.columns(2)

        with fb_col1:
            if st.button("✅ Correct", key="feedback_correct"):
                ss.feedback_type = "correct"
                ss.feedback_given = True
                try:
                    if ss.current_interaction_id:
                        MemoryStore().update_feedback(ss.current_interaction_id, "correct")
                except Exception:
                    pass
                st.rerun()

        with fb_col2:
            if st.button("❌ Incorrect", key="feedback_incorrect"):
                ss.feedback_type = "incorrect"
                st.rerun()

        if ss.feedback_type == "incorrect" and not ss.feedback_given:
            comment: str = st.text_input(
                "What was wrong? (optional)",
                key="feedback_comment_input",
            )
            if st.button("Submit feedback", key="feedback_submit"):
                ss.feedback_comment = comment
                ss.feedback_given = True
                try:
                    if ss.current_interaction_id:
                        MemoryStore().update_feedback(
                            ss.current_interaction_id, "incorrect", comment
                        )
                except Exception:
                    pass
                st.rerun()

    else:
        if ss.feedback_type == "correct":
            st.success("Thanks! Glad the solution was helpful. Feedback saved to memory!")
        else:
            st.info(
                "Thanks for the feedback — saved to memory! "
                "This will help improve future solutions."
            )
