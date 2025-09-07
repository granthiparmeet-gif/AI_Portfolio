import os
import io
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from .schemas import State, EmissionFactors
from .graph import build_graph
from .rag import load_pdf_text
from common.logger import get_logger
from common.exceptions import AppBaseException, DataProcessingError

load_dotenv()
log = get_logger(__name__)

def _read_csv(file) -> pd.DataFrame:
    try:
        return pd.read_csv(file)
    except Exception as e:
        log.error(f"CSV read failed: {e}")
        raise DataProcessingError("Could not read CSV. Expect columns: kwh, renewable_kwh (optional).")

def run_app():
    st.set_page_config(page_title="NetZero Advisor", page_icon="🌍", layout="wide")
    st.title("🌍 NetZero Advisor — Agentic Sustainability")

    colA, colB = st.columns([1, 1])
    with colA:
        pdf_file = st.file_uploader("Upload Sustainability Report (PDF, optional)", type=["pdf"])
        csv_file = st.file_uploader("Upload Energy Usage (CSV: kwh, renewable_kwh)", type=["csv"])
    with colB:
        user_req = st.text_input("What do you want?", value="Generate a NetZero roadmap")
        grid_intensity = st.number_input("Grid intensity (kg CO₂ per kWh)", min_value=0.0, value=0.475, step=0.01)

    if st.button("Generate Roadmap"):
        if not csv_file:
            st.warning("Please upload at least the energy CSV.")
            return

        try:
            with st.spinner("Processing…"):
                pdf_text = ""
                if pdf_file is not None:
                    pdf_bytes = io.BytesIO(pdf_file.read())
                    pdf_text = load_pdf_text(pdf_bytes)

                df = _read_csv(csv_file)
                df_json = df.to_json(orient="records")

                factors = EmissionFactors(grid_intensity_kg_per_kwh=float(grid_intensity))

                graph = build_graph()
                init_state: State = {
                    "user_request": user_req,
                    "pdf_text": pdf_text,
                    "energy_df_json": df_json,
                    "factors": factors,
                }

                result: State = graph.invoke(init_state)

            if "report" in result:
                r = result["report"]
                st.subheader("Roadmap (Markdown)")
                st.markdown(r.summary_md)

                b = r.breakdown
                st.subheader("Emissions Breakdown (kg CO₂)")
                chart_df = pd.DataFrame({
                    "Scope": ["Scope 1", "Scope 2", "Scope 3"],
                    "kgCO2": [b.scope1_kgco2, b.scope2_kgco2, b.scope3_kgco2],
                })
                st.bar_chart(chart_df.set_index("Scope"))

                md_bytes = r.summary_md.encode("utf-8")
                st.download_button("Download report.md", data=md_bytes, file_name="netzero_roadmap.md", mime="text/markdown")

                if result.get("context_snippets"):
                    with st.expander("Grounding snippets from PDF"):
                        for i, s in enumerate(result["context_snippets"], 1):
                            st.write(f"**Snippet {i}:** {s}")
            else:
                st.error("No report produced. Please try again with a valid CSV.")

        except AppBaseException as e:
            st.error(f"Error: {str(e)}")
        except Exception as e:
            log.exception("Unhandled NetZero Advisor error")
            st.error(f"Unexpected error: {e}")