from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AuditMode(str, Enum):
    MODE_A = "MODE_A"  # DATASET ONLY
    MODE_B = "MODE_B"  # DATASET + MODEL PREDICTIONS
    MODE_C = "MODE_C"  # DATASET + MODEL ARTIFACT


class EvidenceTag(str, Enum):
    OBSERVED = "OBSERVED"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"


class ColumnProfile(BaseModel):
    name: str
    data_type: str
    total_count: int
    missing_count: int
    missing_percentage: float
    unique_count: int
    is_constant: bool = False
    is_high_cardinality: bool = False
    sample_values: List[Any] = Field(default_factory=list)
    tag: EvidenceTag = EvidenceTag.OBSERVED
    stats: Dict[str, Any] = Field(default_factory=dict)


class SensitiveAttributeCandidate(BaseModel):
    column_name: str
    category: str  # e.g., age, gender, race, location, income, health
    reasoning: str
    confidence: float = 0.8
    is_confirmed_by_user: Optional[bool] = None
    tag: EvidenceTag = EvidenceTag.INFERRED


class ProxyCandidate(BaseModel):
    sensitive_column: str
    proxy_column: str
    association_type: str  # e.g., Cramer's V, Pearson, ANOVA F-test, Chi-square
    strength_score: float
    description: str
    hypothesis_text: str
    tag: EvidenceTag = EvidenceTag.INFERRED


class DatasetProfile(BaseModel):
    dataset_id: str
    file_name: str
    file_format: str
    row_count: int
    column_count: int
    columns: List[ColumnProfile] = Field(default_factory=list)
    target_candidate: Optional[str] = None
    sensitive_candidates: List[SensitiveAttributeCandidate] = Field(default_factory=list)
    proxy_candidates: List[ProxyCandidate] = Field(default_factory=list)
    missing_value_summary: Dict[str, int] = Field(default_factory=dict)
    class_distribution: Dict[str, Any] = Field(default_factory=dict)
    duplicate_rows: int = 0
    audit_mode: AuditMode = AuditMode.MODE_A
    has_predictions: bool = False
    has_model_artifact: bool = False
