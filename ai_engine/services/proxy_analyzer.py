import logging
from typing import List, Optional
import pandas as pd
import numpy as np
from scipy import stats

from app.schemas.dataset import ProxyCandidate, EvidenceTag

logger = logging.getLogger("ai_engine.proxy_analyzer")


def cramers_v(contingency_table: pd.DataFrame) -> float:
    """Calculates Cramer's V statistic for categorical-categorical association."""
    try:
        chi2 = stats.chi2_contingency(contingency_table)[0]
        n = contingency_table.sum().sum()
        if n == 0:
            return 0.0
        phi2 = chi2 / n
        r, k = contingency_table.shape
        phi2corr = max(0, phi2 - ((k-1)*(r-1))/(n-1))
        rcorr = r - ((r-1)**2)/(n-1)
        kcorr = k - ((k-1)**2)/(n-1)
        min_dim = min((kcorr-1), (rcorr-1))
        if min_dim <= 0:
            return 0.0
        return float(np.sqrt(phi2corr / min_dim))
    except Exception as e:
        logger.debug(f"Cramer's V calculation error: {e}")
        return 0.0


def detect_proxy_attributes(
    df: pd.DataFrame,
    sensitive_columns: List[str],
    target_column: Optional[str] = None
) -> List[ProxyCandidate]:
    """
    Scans dataset to discover potential proxy features for identified sensitive attributes.
    Uses Cramer's V, ANOVA F-test, and Pearson correlation.
    """
    proxy_candidates: List[ProxyCandidate] = []
    if not sensitive_columns or df.empty:
        return proxy_candidates

    cols_to_check = [c for c in df.columns if c not in sensitive_columns and c != target_column]

    for sens_col in sensitive_columns:
        if sens_col not in df.columns:
            continue

        sens_series = df[sens_col].dropna()
        if len(sens_series) < 10:
            continue

        for col in cols_to_check:
            if col not in df.columns:
                continue

            feature_series = df[col].dropna()
            if len(feature_series) < 10:
                continue

            # Align series
            common_idx = sens_series.index.intersection(feature_series.index)
            if len(common_idx) < 10:
                continue

            s_vals = sens_series.loc[common_idx]
            f_vals = feature_series.loc[common_idx]

            s_is_num = pd.api.types.is_numeric_dtype(s_vals) and s_vals.nunique() > 10
            f_is_num = pd.api.types.is_numeric_dtype(f_vals) and f_vals.nunique() > 10

            assoc_type = ""
            strength = 0.0
            description = ""

            try:
                if not s_is_num and not f_is_num:
                    # Categorical vs Categorical: Cramer's V
                    ct = pd.crosstab(s_vals, f_vals)
                    strength = cramers_v(ct)
                    assoc_type = "Cramer's V (Categorical Association)"
                elif s_is_num and f_is_num:
                    # Numerical vs Numerical: Pearson Correlation
                    corr, _ = stats.pearsonr(s_vals, f_vals)
                    strength = abs(float(corr))
                    assoc_type = "Pearson Correlation"
                else:
                    # Numerical vs Categorical: ANOVA F-test / Eta-squared proxy
                    num_s = f_vals if s_is_num else s_vals
                    cat_s = s_vals if s_is_num else f_vals
                    groups = [group.values for _, group in num_s.groupby(cat_s) if len(group) > 2]
                    if len(groups) > 1:
                        f_stat, p_val = stats.f_oneway(*groups)
                        # Normalize f_stat to [0,1] range proxy score
                        strength = min(1.0, float(f_stat / (f_stat + len(common_idx)))) if not np.isnan(f_stat) else 0.0
                        assoc_type = "ANOVA F-test Group Variance"

                # Filter meaningful proxy candidates (strength >= 0.25)
                if strength >= 0.25:
                    description = (
                        f"Potential proxy candidate: '{col}' shows a noticeable statistical association "
                        f"({assoc_type} = {round(strength, 3)}) with potentially sensitive attribute '{sens_col}'."
                    )
                    hypothesis_text = (
                        f"Feature '{col}' may act as a proxy pathway for sensitive attribute '{sens_col}' "
                        f"affecting system evaluations or outcomes."
                    )

                    proxy_candidates.append(
                        ProxyCandidate(
                            sensitive_column=sens_col,
                            proxy_column=col,
                            association_type=assoc_type,
                            strength_score=round(strength, 3),
                            description=description,
                            hypothesis_text=hypothesis_text,
                            tag=EvidenceTag.INFERRED
                        )
                    )
            except Exception as e:
                logger.debug(f"Proxy test error for ({sens_col}, {col}): {e}")

    # Sort proxy candidates by strength score descending
    proxy_candidates.sort(key=lambda x: x.strength_score, reverse=True)
    return proxy_candidates
