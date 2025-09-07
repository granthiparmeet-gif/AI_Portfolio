import io
import json
from typing import List
import pandas as pd

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from .schemas import State, EmissionFactors, EmissionBreakdown, ActionPlanItem, RoadmapReport
from .calculators import electricity_kgco2_from_df
from .rag import build_retriever_from_text
from common.logger import get_logger
from common.exceptions import DataProcessingError, NetZeroError

log = get_logger(__name__)

# ------------- extractor -------------
def extractor_node(state: State) -> State:
    # Normalize factors
    f = state.get("factors") or EmissionFactors()
    if not isinstance(f, EmissionFactors):
        f = EmissionFactors.model_validate(f)
    state["factors"] = f

    # Normalize energy df
    if state.get("energy_df_json"):
        try:
            df = pd.DataFrame(json.loads(state["energy_df_json"]))
            # lower column names
            df.columns = [str(c).strip().lower() for c in df.columns]
            for col in ["kwh", "renewable_kwh"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
            state["energy_df_json"] = df.to_json(orient="records")
            log.info(f"Energy DF normalized: shape={df.shape}")
        except Exception as e:
            log.error(f"Energy CSV parse failed: {e}")
            raise DataProcessingError("Energy usage CSV is invalid or unreadable.")
    return state

# ------------- rag (optional) -------------
def rag_node(state: State) -> State:
    txt = state.get("pdf_text", "")
    if not txt.strip():
        state["context_snippets"] = []
        return state
    retriever = build_retriever_from_text(txt)
    docs = retriever.get_relevant_documents(state.get("user_request", "") or "summary")
    snippets = []
    for d in docs:
        s = d.page_content.strip().replace("\n", " ")
        snippets.append(s[:500])
    state["context_snippets"] = snippets
    log.info(f"RAG produced {len(snippets)} snippets")
    return state

# ------------- calculator -------------
def calculator_node(state: State) -> State:
    f: EmissionFactors = state["factors"]
    df = pd.DataFrame(json.loads(state.get("energy_df_json", "[]")))
    scope2, ren_share = electricity_kgco2_from_df(df, f.grid_intensity_kg_per_kwh)

    breakdown = EmissionBreakdown(scope2_kgco2=scope2)
    state["breakdown"] = breakdown

    msg = f"Scope2={scope2:,.0f} kgCO2; Renewable share={ren_share:.1%}"
    state.setdefault("messages", []).append(msg)
    log.info("Calculator: " + msg)
    return state

# ------------- advisor (LLM optional) -------------
def _heuristic_actions(scope2: float, ren_share: float) -> List[ActionPlanItem]:
    actions: List[ActionPlanItem] = []
    if ren_share < 0.4:
        actions.append(ActionPlanItem(
            action="Increase renewable procurement to 50%",
            category="renewables", est_reduction_kgco2=scope2 * 0.2,
            effort="medium", timeframe_months=12,
            rationale="Move from current mix to higher renewable share via PPAs/RECs."
        ))
    if scope2 > 10_000:
        actions.append(ActionPlanItem(
            action="Conduct energy audits across facilities",
            category="efficiency", est_reduction_kgco2=scope2 * 0.1,
            effort="low", timeframe_months=6,
            rationale="Identify HVAC/lighting/process optimization opportunities."
        ))
        actions.append(ActionPlanItem(
            action="Deploy LED & smart controls",
            category="efficiency", est_reduction_kgco2=scope2 * 0.05,
            effort="medium", timeframe_months=9,
            rationale="Fast payback measures to cut electricity load."
        ))
    actions.append(ActionPlanItem(
        action="Employee behavioral program",
        category="behavior", est_reduction_kgco2=max(scope2 * 0.02, 500.0),
        effort="low", timeframe_months=6,
        rationale="Awareness, shutdown policies, and green champions."
    ))
    return actions

def advisor_node(state: State) -> State:
    b: EmissionBreakdown = state["breakdown"]
    df_preview = json.loads(state.get("energy_df_json", "[]"))[:6]
    ren_share = 0.0
    try:
        total_kwh = sum(float(r.get("kwh", 0)) for r in df_preview)
        ren_kwh = sum(float(r.get("renewable_kwh", 0)) for r in df_preview)
        ren_share = (ren_kwh / total_kwh) if total_kwh > 0 else 0.0
    except Exception:
        ren_share = 0.0

    actions = _heuristic_actions(b.scope2_kgco2, ren_share)

    # Optional: ask LLM for 2 short suggestions (soft, non-struct)
    try:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        prompt = ChatPromptTemplate.from_template(
            "You are a sustainability advisor. Given the scope2 (kgCO2) {scope2} and renewable share {ren:.1%}, "
            "suggest exactly two concise, practical actions (one efficiency, one renewables). "
            "Return as two bullet points starting with '- '."
        )
        msgs = prompt.format_messages(scope2=b.scope2_kgco2, ren=ren_share)
        out = llm.invoke(msgs).content or ""
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("- "):
                actions.append(ActionPlanItem(
                    action=line[2:],
                    category="efficiency" if "efficien" in line.lower() else "renewables",
                    est_reduction_kgco2=max(b.scope2_kgco2 * 0.03, 250.0),
                    effort="medium",
                    timeframe_months=12,
                    rationale="LLM-suggested."
                ))
    except Exception as e:
        log.warning(f"LLM suggestions skipped: {e}")

    state["actions"] = actions
    log.info(f"Advisor produced {len(actions)} actions (heuristic + optional LLM)")
    return state

# ------------- writer -------------
def writer_node(state: State) -> State:
    b: EmissionBreakdown = state["breakdown"]
    actions: List[ActionPlanItem] = state.get("actions", [])

    lines = [
        "# NetZero Roadmap",
        "",
        "## Summary",
        f"- Estimated Scope 2 emissions: **{b.scope2_kgco2:,.0f} kg CO₂**",
        f"- Total (Scopes 1+2+3): **{b.total_kgco2:,.0f} kg CO₂**",
        "",
        "## Recommended Actions",
    ]
    for i, a in enumerate(actions, 1):
        lines.append(
            f"{i}. **{a.action}** — _{a.category}_, effort: {a.effort}, "
            f"est. reduction: **{a.est_reduction_kgco2:,.0f} kg CO₂**, timeframe: {a.timeframe_months} mo.\n"
            f"   - Rationale: {a.rationale}"
        )
    md = "\n".join(lines)

    report = RoadmapReport(
        title="NetZero Roadmap",
        summary_md=md,
        breakdown=b,
        actions=actions,
    )
    state["report"] = report
    log.info("Writer produced roadmap markdown")
    return state