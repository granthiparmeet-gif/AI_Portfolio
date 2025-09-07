import json
from typing import List
import pandas as pd
import altair as alt

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable  # per-node spans appear in LangSmith

from .schemas import State, ChartSpec, FilterRule
from .exceptions import SpecValidationError
from .logger import get_logger

log = get_logger(__name__)

# ---------- Utilities ----------

def _df_from_state(state: State) -> pd.DataFrame:
    # df_json uses orient="records"
    return pd.DataFrame(json.loads(state["df_json"]))

def _apply_filters(df: pd.DataFrame, filters: List[FilterRule]) -> pd.DataFrame:
    for rule in filters:
        col = rule.column
        if col not in df.columns:
            continue
        val = rule.value
        if rule.op == "==":
            df = df[df[col] == val]
        elif rule.op == "!=":
            df = df[df[col] != val]
        elif rule.op == ">":
            df = df[df[col] > val]
        elif rule.op == "<":
            df = df[df[col] < val]
        elif rule.op == ">=":
            df = df[df[col] >= val]
        elif rule.op == "<=":
            df = df[df[col] <= val]
        elif rule.op == "in":
            vals = val if isinstance(val, list) else [val]
            df = df[df[col].isin(vals)]
        elif rule.op == "not in":
            vals = val if isinstance(val, list) else [val]
            df = df[~df[col].isin(vals)]
    return df

# ---------- Nodes ----------

@traceable(name="summarize_schema")
def summarize_schema_node(state: State) -> State:
    df = _df_from_state(state)
    if df.empty:
        raise SpecValidationError("Dataframe is empty.")
    parts = []
    for col, dtype in df.dtypes.items():
        sample = df[col].dropna().head(3).tolist()
        parts.append(f"{col} ({str(dtype)}), samples={sample}")
    state["df_schema"] = " | ".join(parts)
    state.setdefault("messages", []).append("Schema summarized.")
    log.info("Schema summarized.")
    return state

@traceable(name="parse_request")
def parse_request_node(state: State, llm: ChatOpenAI) -> State:
    prompt = ChatPromptTemplate.from_template(
        "You are a data viz planner. Given a Pandas schema and a user request, "
        "RETURN ONLY a JSON for ChartSpec with fields: "
        "chart_type, x, y (nullable), aggregate (nullable), color (nullable), "
        "filters (array of FilterRule). No extra text.\n\n"
        "Schema:\n{schema}\n\nRequest:\n{request}"
    )
    messages = prompt.format_messages(schema=state["df_schema"], request=state["user_request"])

    # Modern structured outputs (LangChain 0.3+)
    spec: ChartSpec = llm.with_structured_output(ChartSpec).invoke(messages)
    state["chart_spec"] = spec
    state.setdefault("messages", []).append(f"Parsed spec: {spec.model_dump()}")
    log.info("Parsed ChartSpec.")
    return state

@traceable(name="critic")
def critic_node(state: State, llm: ChatOpenAI) -> State:
    """
    Sanity-check: ensure referenced columns exist; if not, ask LLM to correct spec.
    """
    spec = state["chart_spec"]
    df = _df_from_state(state)

    errors = []
    if spec.x not in df.columns:
        errors.append(f"x '{spec.x}' not found")
    if spec.y and spec.y not in df.columns:
        errors.append(f"y '{spec.y}' not found")

    if errors:
        import json as _json
        prompt = ChatPromptTemplate.from_template(
            "Given the schema and an invalid ChartSpec, return a corrected JSON ChartSpec ONLY.\n\n"
            "Schema:\n{schema}\n\nInvalid Spec:\n{spec_json}"
        )
        msgs = prompt.format_messages(schema=state["df_schema"], spec_json=_json.dumps(spec.model_dump()))
        resp = llm.invoke(msgs).content.strip()
        if resp.startswith("{"):
            try:
                corrected = ChartSpec.model_validate_json(resp)
                state["chart_spec"] = corrected
                state.setdefault("messages", []).append("Critic corrected spec.")
                log.info("Critic corrected spec.")
            except Exception:
                state.setdefault("messages", []).append("Critic returned invalid JSON; ignoring.")
                log.warning("Critic returned invalid JSON; ignoring.")
        else:
            state.setdefault("messages", []).append("Critic returned non-JSON; ignoring.")
            log.warning("Critic returned non-JSON; ignoring.")
    else:
        state.setdefault("messages", []).append("Critic: ok.")
        log.info("Critic: ok.")
    return state

@traceable(name="build_vega")
def build_vega_node(state: State) -> State:
    spec: ChartSpec = state["chart_spec"]
    df = _df_from_state(state)

    # apply filters, then validate columns again
    df = _apply_filters(df, spec.filters)
    if spec.x not in df.columns:
        raise SpecValidationError(f"x column '{spec.x}' not in DataFrame.")
    if spec.y and spec.y not in df.columns:
        raise SpecValidationError(f"y column '{spec.y}' not in DataFrame.")

    chart = alt.Chart(df)

    # mark
    if spec.chart_type == "bar":
        chart = chart.mark_bar()
    elif spec.chart_type == "line":
        chart = chart.mark_line()
    elif spec.chart_type == "area":
        chart = chart.mark_area()
    elif spec.chart_type == "scatter":
        chart = chart.mark_circle()
    elif spec.chart_type == "pie":
        chart = chart.mark_arc()
    else:
        chart = chart.mark_bar()

    # encodings
    enc = {}
    if spec.x:
        enc["x"] = spec.x
    if spec.y:
        if spec.aggregate and spec.y:
            enc["y"] = f"{spec.aggregate}({spec.y})"
        else:
            enc["y"] = spec.y
    if spec.color:
        enc["color"] = spec.color

    chart = chart.encode(**enc)
    state["vega_spec"] = chart.to_dict()
    state.setdefault("messages", []).append("Vega spec built.")
    log.info("Vega spec built.")
    return state