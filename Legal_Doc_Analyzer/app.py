import streamlit as st
from .pipeline import analyze_contract
from common.exceptions import BaseAIError

def run_app():
    st.title("Legal Document Analyzer")

    uploaded_file = st.file_uploader("Upload a contract (PDF)", type=["pdf"])
    query = st.text_input("Ask a legal question about this contract:")

    if st.button("Analyze"):
        if not uploaded_file or not query:
            st.warning("Please upload a file and enter a question.")
            return

        try:
            with st.spinner("Processing contract..."):
                result = analyze_contract(uploaded_file, query)
                if result.startswith("Error:"):
                    st.error(result)
                else:
                    st.success(result)
        except BaseAIError as e:
            st.error(f"Error: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
