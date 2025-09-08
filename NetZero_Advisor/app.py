import streamlit as st
from .graph import build_graph
from common.exceptions import BaseAIError

def run_app():
    st.title("🌍 NetZero Advisor")
    st.write("Upload your sustainability report or energy dataset and generate a NetZero roadmap.")

    uploaded_file = st.file_uploader("Upload CSV or TXT", type=["csv", "txt"])
    user_goal = st.text_input("What do you want? (e.g., 'Generate a NetZero roadmap')")

    if st.button("Run Advisor"):
        if not uploaded_file or not user_goal:
            st.warning("Please upload a file and enter a goal.")
            return

        try:
            # Read file
            file_content = uploaded_file.read().decode("utf-8")

            # Build and run graph
            graph = build_graph()
            result = graph.invoke({"file_content": file_content, "goal": user_goal})

            if "plan" in result:
                st.subheader("📋 Actionable Roadmap")
                st.write(result["plan"])
            else:
                st.error("Error: LLM failed to generate an actionable plan.")
        except BaseAIError as e:
            st.error(f"Error: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
