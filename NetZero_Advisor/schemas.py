from typing import List, Optional, Dict, Any, TypedDict, Literal
from pydantic import BaseModel, Field, ConfigDict


class EmissionFactors(BaseModel):
    grid_intensity_kg_per_kwh: float = Field(
        0.475, description="kg CO₂ per kWh for grid electricity."
    )
    model_config = ConfigDict(extra="allow")


class EmissionBreakdown(BaseModel):
    scope1_kgco2: float = 0.0
    scope2_kgco2: float = 0.0
    scope3_kgco2: float = 0.0

    @property
    def total_kgco2(self) -> float:
        return float(self.scope1_kgco2 + self.scope2_kgco2 + self.scope3_kgco2)

    model_config = ConfigDict(extra="allow")


class ActionPlanItem(BaseModel):
    action: str
    category: Literal["efficiency", "renewables", "policy", "offsets", "behavior"] = "efficiency"
    est_reduction_kgco2: float = 0.0
    effort: Literal["low", "medium", "high"] = "medium"
    timeframe_months: int = 6
    rationale: str = ""
    model_config = ConfigDict(extra="allow")


class RoadmapReport(BaseModel):
    title: str
    summary_md: str
    breakdown: EmissionBreakdown
    actions: List[ActionPlanItem]
    model_config = ConfigDict(extra="allow")


class State(TypedDict, total=False):
    user_request: str
    pdf_text: str
    energy_df_json: str
    factors: EmissionFactors

    context_snippets: List[str]
    breakdown: EmissionBreakdown
    actions: List[ActionPlanItem]

    report: RoadmapReport