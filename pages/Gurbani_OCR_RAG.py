import sys
from pathlib import Path

import streamlit as st

root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from Gurbani_OCR_RAG.app import run_app  # isort: skip

run_app()
