import streamlit as st
from .orchestrator import run_research

def run_app():
    st.set_page_config(page_title="Research Agent", page_icon="🧭", layout="wide")
    st.title("Deep Research (OpenAI Agents SDK + MCP)")
    q = st.text_area("What should I research?", height=120,
                     placeholder="e.g., Are small modular reactors viable for data centers within 5 years?")
    if st.button("Run Research"):
        if not q.strip():
            st.warning("Please enter a question.")
            return
        with st.spinner("Researching..."):
            result = run_research(q)
        st.markdown("### Answer")
        st.write(result.get("answer",""))
        hints = result.get("sources_hint") or []
        if hints:
            with st.expander("Tool output hints"):
                for i, h in enumerate(hints, 1):
                    st.code(h)
