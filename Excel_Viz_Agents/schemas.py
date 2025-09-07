from typing import Union, List, Dict, Any, Optional, TypedDict, Literal
from pydantic import BaseModel, Field, ConfigDict

class FilterRule(BaseModel):
    column: str = Field(..., description="Exact column name in the dataframe")
    op: Literal["==", "!=", ">", "<", ">=", "<=", "in", "not in"]
    value: Union[
        str, int, float, bool,
        List[str], List[int], List[float], List[bool]
    ] = Field(..., description="Value or list of values to filter by")
    model_config = ConfigDict(extra="forbid")  # -> additionalProperties: false

class ChartSpec(BaseModel):
    chart_type: Literal["bar", "line", "area", "scatter", "pie"]
    x: str
    y: Optional[str] = None
    aggregate: Optional[Literal["sum", "avg", "count", "min", "max"]] = None
    color: Optional[str] = None
    filters: List[FilterRule] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")  # -> additionalProperties: false

class State(TypedDict, total=False):
    # inputs
    user_request: str
    df_json: str          # DataFrame serialized by df.to_json(orient="records")
    df_schema: str        # textual summary for prompting
    # plan/spec
    chart_spec: ChartSpec
    # outputs
    vega_spec: Dict[str, Any]
    messages: List[str]