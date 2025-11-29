# Gurbani OCR RAG

This folder contains the artifacts and helpers behind the **Gurbani OCR RAG** demo that is now part of the AI Portfolio.

## Contents

- `data/` – static assets such as the cleaned OCR text (`Gurbani.txt`), pre-built chunk list (`chunks.json`), and sample page images.
- `build_index.py` – creates multilingual FAISS embeddings from the OCR text and writes `index.faiss` + `chunks.json` back into `data/`.
- `app.py` – Streamlit launchpad that loads the index, runs strict retrieval, and surfaces grounded answers.

## Setup notes

1. Ensure `OPENAI_API_KEY` is available in the shared `.env` file at the repository root.
2. Run `python -m Gurbani_OCR_RAG.build_index` (or use the builder helper) to regenerate the FAISS index if you replace the source text.
3. Launch the portfolio via `streamlit run Home.py` and choose **Gurbani OCR RAG** from the Labs sidebar.

The demo is intentionally grounded: the assistant returns only evidence-backed responses from the provided OCR text and refuses gaps in the source material.
