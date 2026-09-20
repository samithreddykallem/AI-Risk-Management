import os
import uuid
import logging
from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np

from app.schemas.dataset import (
    DatasetProfile,
    ColumnProfile,
    AuditMode,
    EvidenceTag
)
from services.sensitive_detector import detect_sensitive_attributes
from services.proxy_analyzer import detect_proxy_attributes

logger = logging.getLogger("ai_engine.dataset_profiler")


def profile_dataset(
    file_path: str,
    dataset_name: Optional[str] = None,
    user_target_column: Optional[str] = None,
    user_sensitive_attributes: Optional[List[str]] = None,
    predictions_path: Optional[str] = None,
    model_artifact_path: Optional[str] = None
) -> DatasetProfile:
    """
    Ingests CSV/XLSX/JSON datasets safely, builds a comprehensive DatasetProfile,
    discovers sensitive attribute candidates and proxy relationships.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found at path: {file_path}")

    file_name = dataset_name or os.path.basename(file_path)
    file_ext = os.path.splitext(file_name)[1].lower()

    # Determine file format & load dataframe safely
    try:
        if file_ext == ".csv":
            df = pd.read_csv(file_path)
            file_format = "CSV"
        elif file_ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path)
            file_format = "XLSX"
        elif file_ext == ".json":
            df = pd.read_json(file_path)
            file_format = "JSON"
        else:
            # Fallback csv attempt
            df = pd.read_csv(file_path)
            file_format = "CSV"
    except Exception as e:
        logger.error(f"Failed to read dataset file {file_path}: {e}")
        raise ValueError(f"Could not parse dataset file: {str(e)}")

    row_count, column_count = df.shape

    # Process column profiles
    column_profiles: List[ColumnProfile] = []
    missing_summary: Dict[str, int] = {}

    for col in df.columns:
        series = df[col]
        missing_cnt = int(series.isnull().sum())
        missing_pct = float(missing_cnt / row_count * 100) if row_count > 0 else 0.0
        unique_cnt = int(series.nunique(dropna=True))
        is_const = unique_cnt <= 1
        is_high_card = unique_cnt > (row_count * 0.5) and row_count > 20

        # Sample values (convert numpy/pandas types to native Python)
        sample_vals = series.dropna().unique()[:5].tolist()
        sample_vals = [int(v) if isinstance(v, (np.integer, bool)) else float(v) if isinstance(v, np.floating) else str(v) for v in sample_vals]

        col_prof = ColumnProfile(
            name=str(col),
            data_type=str(series.dtype),
            total_count=row_count,
            missing_count=missing_cnt,
            missing_percentage=round(missing_pct, 2),
            unique_count=unique_cnt,
            is_constant=is_const,
            is_high_cardinality=is_high_card,
            sample_values=sample_vals,
            tag=EvidenceTag.OBSERVED
        )
        column_profiles.append(col_prof)
        if missing_cnt > 0:
            missing_summary[str(col)] = missing_cnt

    # Target candidate identification
    target_col = user_target_column
    if not target_col:
        potential_targets = [
            c for c in df.columns 
            if str(c).lower() in ["target", "label", "status", "approved", "loan_status", "fraud", "churn", "default", "decision", "outcome", "y"]
        ]
        if potential_targets:
            target_col = str(potential_targets[0])
        elif column_count > 0:
            # Fallback to last column if binary or low cardinality
            last_col = df.columns[-1]
            if df[last_col].nunique() <= 10:
                target_col = str(last_col)

    # Class distribution if target column exists
    class_dist: Dict[str, Any] = {}
    if target_col and target_col in df.columns:
        counts = df[target_col].value_counts(dropna=False).to_dict()
        class_dist = {str(k): int(v) for k, v in counts.items()}

    # Duplicate rows
    dup_rows = int(df.duplicated().sum())

    # Detect audit mode
    has_preds = bool(predictions_path and os.path.exists(predictions_path))
    has_model = bool(model_artifact_path and os.path.exists(model_artifact_path))

    if has_model:
        mode = AuditMode.MODE_C
    elif has_preds:
        mode = AuditMode.MODE_B
    else:
        mode = AuditMode.MODE_A

    # Sensitive attribute candidates
    sensitive_candidates = detect_sensitive_attributes(df, user_sensitive_attributes)

    # Proxy candidates
    sensitive_col_names = [s.column_name for s in sensitive_candidates]
    if user_sensitive_attributes:
        sensitive_col_names = list(set(sensitive_col_names + user_sensitive_attributes))

    proxy_candidates = detect_proxy_attributes(df, sensitive_col_names, target_col)

    dataset_id = f"DS-{uuid.uuid4().hex[:8]}"

    profile = DatasetProfile(
        dataset_id=dataset_id,
        file_name=file_name,
        file_format=file_format,
        row_count=row_count,
        column_count=column_count,
        columns=column_profiles,
        target_candidate=target_col,
        sensitive_candidates=sensitive_candidates,
        proxy_candidates=proxy_candidates,
        missing_value_summary=missing_summary,
        class_distribution=class_dist,
        duplicate_rows=dup_rows,
        audit_mode=mode,
        has_predictions=has_preds,
        has_model_artifact=has_model
    )

    logger.info(f"Dataset profiled successfully: {file_name} ({row_count} rows, {column_count} cols, Mode: {mode.value})")
    return profile
