import re
from typing import List, Optional
import pandas as pd
from app.schemas.dataset import SensitiveAttributeCandidate, EvidenceTag


SENSITIVE_KEYWORDS = {
    "gender": ["gender", "sex", "male", "female"],
    "age": ["age", "dob", "birth", "birthdate", "year_of_birth", "yob"],
    "race": ["race", "ethnicity", "skin_color", "origin", "ancestry", "tribal"],
    "location": ["zip", "zipcode", "zip_code", "postcode", "postal_code", "neighborhood", "area", "region", "district", "city", "state"],
    "income": ["income", "salary", "wage", "wealth", "earning", "net_worth", "revenue"],
    "disability": ["disability", "disabled", "handicap", "medical_condition"],
    "education": ["education", "degree", "school", "qualification", "university"],
    "employment": ["employment", "job", "occupation", "employer", "work_status"],
    "nationality": ["nationality", "citizenship", "country_of_origin", "immigration"],
    "health": ["health", "medical", "diagnosis", "disease", "treatment", "patient_status"]
}


def detect_sensitive_attributes(
    df: pd.DataFrame,
    user_sensitive: Optional[List[str]] = None
) -> List[SensitiveAttributeCandidate]:
    """
    Identifies potential sensitive attributes based on column names, patterns, and user input.
    Label is explicitly 'Potentially sensitive attribute identified' (does not claim legal facts).
    """
    candidates: List[SensitiveAttributeCandidate] = []
    user_sensitive_set = set(user_sensitive or [])

    for col in df.columns:
        col_lower = str(col).lower().strip()
        matched_cat = None
        matched_reasoning = ""

        # Check against user specified list first
        if col in user_sensitive_set or col_lower in user_sensitive_set:
            candidates.append(
                SensitiveAttributeCandidate(
                    column_name=str(col),
                    category="user_specified",
                    reasoning=f"User explicitly designated '{col}' as a sensitive attribute.",
                    confidence=1.0,
                    is_confirmed_by_user=True,
                    tag=EvidenceTag.OBSERVED
                )
            )
            continue

        # Check keyword matches
        for cat, keywords in SENSITIVE_KEYWORDS.items():
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', col_lower) or kw in col_lower:
                    matched_cat = cat
                    matched_reasoning = f"Column name '{col}' matches sensitive category pattern '{cat}' (keyword match: '{kw}')."
                    break
            if matched_cat:
                break

        if matched_cat:
            candidates.append(
                SensitiveAttributeCandidate(
                    column_name=str(col),
                    category=matched_cat,
                    reasoning=f"Potentially sensitive attribute identified: {col}. {matched_reasoning}",
                    confidence=0.85,
                    is_confirmed_by_user=False,
                    tag=EvidenceTag.INFERRED
                )
            )

    return candidates
