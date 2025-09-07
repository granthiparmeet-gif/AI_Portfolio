import streamlit as st

st.set_page_config(page_title="AI Labs | Parmeet Singh", page_icon="🧪", layout="wide")

st.title("🧪 AI Labs")
st.write("Welcome to my collection of interactive AI projects. Explore the demos below:")

# ---- YouTube RAG ----
st.markdown("### 🎥 YouTube RAG")
st.write("Paste a YouTube URL and ask grounded questions about its transcript.")
if st.button("🚀 Open YouTube RAG"):
    st.switch_page("pages/YouTube_RAG.py")

# ---- Excel_Viz_Agents ----
st.markdown("### 📊 Excel Viz (LangGraph)")
st.write("Upload Excel, describe a chart, and the agentic flow will plan, validate, and render a safe Vega-Lite chart.")
if st.button("🚀 Open Excel Viz"):
    st.switch_page("pages/Excel_Viz_Agents.py")  # multipage navigation  [oai_citation:11‡Streamlit Docs](https://docs.streamlit.io/develop/api-reference/navigation/st.switch_page?utm_source=chatgpt.com)

# ---- CrewAI Multi-Agent Team ----
st.markdown("### 👥 CrewAI Multi-Agent Team")
st.write("See multiple AI agents collaborate on a shared task.")
if st.button("🚀 Open CrewAI Demo"):
    st.switch_page("pages/CrewAI_Agents.py")

# ---- AutoGen Workflow ----
st.markdown("### 🔄 AutoGen Workflow")
st.write("Watch AutoGen agents debate and refine answers.")
if st.button("🚀 Open AutoGen Demo"):
    st.switch_page("pages/AutoGen_Workflow.py")