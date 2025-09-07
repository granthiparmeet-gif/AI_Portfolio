from typing import Tuple
import pandas as pd

def electricity_kgco2_from_df(df: pd.DataFrame, grid_intensity_kg_per_kwh: float) -> Tuple[float, float]:
    """
    Expects columns:
      - kwh (float)
      - renewable_kwh (float, optional)
    Returns (scope2_kgco2, renewable_share)
    """
    if df is None or df.empty or "kwh" not in df.columns:
        return 0.0, 0.0

    total_kwh = float(df["kwh"].fillna(0).sum())
    renewable_kwh = float(df.get("renewable_kwh", 0))
    if "renewable_kwh" in df.columns:
        renewable_kwh = float(df["renewable_kwh"].fillna(0).sum())

    fossil_kwh = max(total_kwh - renewable_kwh, 0.0)
    scope2_kg = fossil_kwh * grid_intensity_kg_per_kwh
    renewable_share = (renewable_kwh / total_kwh) if total_kwh > 0 else 0.0
    return float(scope2_kg), float(renewable_share)