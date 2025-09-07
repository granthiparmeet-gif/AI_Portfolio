import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig

from .graph import build_graph
from .schemas import State
from .exceptions import InvalidExcelError, SpecValidationError, ExcelVizException
from .logger import get_logger

load_dotenv()
log = get_logger(__name__)

def run_app():
    st.set_page_config(page_title="Excel Viz (LangGraph)", page_icon="📊", layout="wide")
    st.title("📊 Excel Viz — Multi-Agent (LangGraph)")
    st.caption("Upload an Excel file, describe a chart, and let agents plan, critique, and render a safe Vega-Lite chart.")

    uploaded = st.file_uploader("Upload .xlsx", type=["xlsx"])
    user_req = st.text_input("Describe your chart (e.g., 'Bar chart of total sales by region, color by product')")

    if st.button("Generate"):
        if not uploaded:
            st.warning("Please upload an Excel file.")
            return
        if not user_req.strip():
            st.warning("Please describe the chart you want.")
            return

        try:
            with st.spinner("Processing…"):
                try:
                    df = pd.read_excel(uploaded, engine="openpyxl")
                except Exception as e:
                    log.error(f"Excel read failed: {e}")
                    raise InvalidExcelError("Could not read the Excel file. Please check format/content.")

                if df.empty:
                    raise InvalidExcelError("The uploaded Excel has no rows.")

                llm_factory = lambda: ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=0.1,
                    api_key=os.getenv("OPENAI_API_KEY"),
                )

                graph = build_graph(llm_factory)
                init: State = {
                    "user_request": user_req,
                    "df_json": df.to_json(orient="records"),
                    "messages": [],
                }

                # LangSmith: env enables tracing; add per-run metadata/tags
                config: RunnableConfig = {
                    "metadata": {
                        "app": "excel_viz_agents",
                        "author": "Parmeet Singh",
                        "sheet_rows": int(len(df)),
                    },
                    "tags": ["excel", "viz", "langgraph", "portfolio"],
                }

                result: State = graph.invoke(init, config=config)

            if "vega_spec" in result:
                st.subheader("Generated Chart")
                st.vega_lite_chart(result["vega_spec"])  # spec already contains embedded data

                with st.expander("Debug / Trace"):
                    if "chart_spec" in result:
                        st.write("ChartSpec:")
                        st.json(result["chart_spec"].model_dump())
                    st.write("Vega Spec:")
                    st.json(result.get("vega_spec", {}))
                    for m in result.get("messages", []):
                        st.write("-", m)
            else:
                st.error("No chart produced. Please refine your request.")

        except InvalidExcelError as e:
            st.error(str(e))
        except SpecValidationError as e:
            st.error(f"Chart spec error: {e}")
        except ExcelVizException as e:
            st.error(f"App error: {e}")
        except Exception as e:
            log.exception("Unhandled error.")
            st.error(f"Unexpected error: {e}")