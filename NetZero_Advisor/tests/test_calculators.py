import pandas as pd
from NetZero_Advisor.calculators import electricity_kgco2_from_df

def test_electricity_kgco2_from_df():
    df = pd.DataFrame({"kwh": [1000, 500], "renewable_kwh": [200, 100]})
    scope2, ren_share = electricity_kgco2_from_df(df, 0.5)
    assert round(scope2, 2) == 600.00  # (1500 - 300) * 0.5 = 600
    assert round(ren_share, 2) == 0.20