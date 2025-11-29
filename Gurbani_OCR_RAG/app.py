from __future__ import annotations

from pathlib import Path
from typing import Iterable

import streamlit as st

from .ask import ask_question, load_resources

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


@st.cache_resource
def _cached_resources():
    return load_resources()


def _format_chunk(chunk: dict[str, object]) -> str:
    text = chunk.get("text", "").strip()
    snippet = text[:360].rstrip()
    if len(text) > 360:
        snippet += "…"
    return f"**Chunk {chunk.get('id', '?')}**\n\n{snippet}"


def _display_chunks(chunks: Iterable[dict[str, object]]):
    for chunk in chunks:
        st.markdown(_format_chunk(chunk))
        st.divider()


def _image_gallery():
    images = sorted(DATA_DIR.glob("Page_*.jpeg"))
    if not images:
        return
    st.subheader("OCR source snapshots")
    cols = st.columns(len(images))
    for col, path in zip(cols, images):
        col.image(str(path), caption=path.name, width=180)


def run_app(embed: bool = False):
    if not embed:
        st.set_page_config(page_title="Gurbani OCR RAG", layout="wide")
    st.title("Gurbani OCR RAG Chatbot")
    st.write(
        "Ask grounded questions in English or Punjabi and receive evidence-backed answers "
        "Citied directly from the OCR text extracted from Gurmukhi manuscripts."
    )
    _image_gallery()

    try:
        client, index, chunks = _cached_resources()
    except SystemExit as err:
        st.error(str(err))
        return

    st.markdown("**Ask your question:**")
    question = st.text_area(
        "",
        placeholder="Example: What life lesson is being highlighted in this passage?",
        key="gurbani_query",
        height=140,
        label_visibility="collapsed",
    )

    state_answer_key = "gurbani_answer"
    state_chunks_key = "gurbani_chunks"
    if state_answer_key not in st.session_state:
        st.session_state[state_answer_key] = ""
        st.session_state[state_chunks_key] = []

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Generate grounded answer"):
            if not question.strip():
                st.warning("Please type a question before generating an answer.")
            else:
                with st.spinner("Retrieving context…"):
                    try:
                        answer, retrieved = ask_question(question, client, index, chunks)
                    except Exception as exc:  # pragma: no cover
                        st.error(f"Unable to run assistant: {exc}")
                        answer, retrieved = "", []
                st.session_state[state_answer_key] = answer
                st.session_state[state_chunks_key] = retrieved

        if st.session_state[state_answer_key]:
            st.subheader("Answer")
            st.markdown(st.session_state[state_answer_key])
            st.caption("Responses cite the chunk IDs sourced from the OCR text.")

        if st.session_state[state_chunks_key]:
            st.subheader("Retrieved chunks")
            _display_chunks(st.session_state[state_chunks_key])

    with col2:
        st.info("Sources are the cleaned OCR output from the Gurbani manuscript.")
        st.caption("Top chunks are re-used to keep the assistant grounded.")
