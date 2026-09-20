import os
import pandas as pd
from services.proxy_analyzer import detect_proxy_attributes


def test_proxy_analyzer():
    csv_path = os.path.join(os.path.dirname(__file__), "loan_data.csv")
    df = pd.read_csv(csv_path)

    proxies = detect_proxy_attributes(df, sensitive_columns=["Gender", "ZIP_Code"], target_column="Loan_Status")

    assert isinstance(proxies, list)
    for p in proxies:
        assert p.strength_score >= 0.25
        assert "Potential proxy candidate" in p.description
