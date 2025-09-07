import streamlit as st
from .pipeline import answer_question
from common.exceptions import BaseAIError  # updated import

def run_app():
    st.title("YouTube RAG • (Latest LangChain)")

    url = st.text_input("Enter a YouTube URL:")
    query = st.text_input("Ask a question about the video:")

    if st.button("Get Answer"):
        if not (url and query):
            st.warning("Please enter both a URL and a question.")
            return

        with st.spinner("Processing..."):
            try:
                result = answer_question(url, query)
                ans = result.get("answer", "")
                if ans.startswith("Error:"):
                    st.error(ans)
                else:
                    st.success(ans)

                    # Show sources/snippets
                    docs = result.get("context", []) or []
                    if docs:
                        with st.expander("Show retrieved snippets"):
                            for i, d in enumerate(docs, 1):
                                snippet = (d.page_content or "")[:400].strip()
                                st.markdown(f"**Snippet {i}:**\n\n{snippet}...")
                # optional: clear inputs, etc.
            except BaseAIError as e:  # updated exception
                st.error(f"Error: {str(e)}")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")