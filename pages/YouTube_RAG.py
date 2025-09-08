import sys
from pathlib import Path
import streamlit as st

root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from YouTube_RAG.app import run_app
st.set_page_config(page_title="YouTube RAG", page_icon="🎬", layout="centered")
run_app()
