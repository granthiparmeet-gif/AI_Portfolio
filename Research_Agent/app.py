import streamlit as st
from .orchestrator import run_research
from common.exceptions import BaseAIError

def run_app():
    st.title("🔎 Research Agent")

    query = st.text_input("Enter your research question:")
    if st.button("Run Research"):
        if not query.strip():
            st.warning("Please enter a question.")
            return
        with st.spinner("Researching..."):
            try:
                answer = run_research(query)
                st.success(answer)
            except BaseAIError as e:
                st.error(f"Error: {str(e)}")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")