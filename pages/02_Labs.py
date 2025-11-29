import streamlit as st

st.set_page_config(page_title="AI Labs", page_icon="🧪", layout="centered")

st.title("AI Labs")
st.write("Welcome to my collection of interactive AI projects. Explore the demos below:")

# --- YouTube RAG ---
st.markdown("### YouTube RAG")
st.write("Paste a YouTube URL and ask grounded questions about its transcript.")
st.link_button("Open Demo", "07_YouTube_RAG")

# --- NetZero Advisor ---
st.markdown("### NetZero Advisor")
st.write("Upload your sustainability report or energy dataset and generate a NetZero roadmap.")
st.link_button("Open Demo", "04_NetZero_Advisor")

# --- Research Agent ---
st.markdown("### Research Agent")
st.write("Ask any research question and let the AI agent gather, analyze, and summarize findings.")
st.link_button("Open Demo", "06_Research_Agent")

# --- Legal Document Analyzer ---
st.markdown("### Legal Document Analyzer")
st.write("Upload contracts or agreements and let the AI extract key clauses, obligations, and risks.")
st.link_button("Open Demo", "05_Legal_Doc_Analyzer")

# --- Gurbani OCR RAG ---
st.markdown("### Gurbani OCR RAG")
st.write(
    "Ask English or Punjabi questions about the Gurbani manuscript. The assistant only answers "
    "from the provided OCR text and cites chunk IDs for every claim."
)
st.link_button("Open Demo", "03_Gurbani_OCR_RAG")

st.divider()
st.caption("Built with LangChain, LangGraph, OpenAI SDK, CrewAI & FastAPI")
