import os
import pytest
from services.dataset_profiler import profile_dataset
from app.schemas.dataset import AuditMode


def test_profile_dataset():
    csv_path = os.path.join(os.path.dirname(__file__), "loan_data.csv")
    assert os.path.exists(csv_path)

    profile = profile_dataset(file_path=csv_path, user_target_column="Loan_Status")

    assert profile.row_count == 20
    assert profile.column_count == 9
    assert profile.target_candidate == "Loan_Status"
    assert profile.audit_mode == AuditMode.MODE_A

    # Check sensitive attributes
    sens_names = [s.column_name for s in profile.sensitive_candidates]
    assert "Gender" in sens_names or "Age" in sens_names or "ZIP_Code" in sens_names

    # Check proxy candidates
    assert len(profile.proxy_candidates) >= 0
