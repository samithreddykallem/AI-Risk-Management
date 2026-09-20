import os
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from scipy import stats

from app.tools.base import BaseTool, ToolOutput
from app.schemas.dataset import EvidenceTag
from services.dataset_profiler import profile_dataset
from services.proxy_analyzer import detect_proxy_attributes

logger = logging.getLogger("ai_engine.statistical_tools")


def load_dataframe_from_kwargs(kwargs: Dict[str, Any]) -> pd.DataFrame:
    """Helper to safely load pandas DataFrame from dataset_path argument."""
    dataset_path = kwargs.get("dataset_path")
    if not dataset_path or not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset path not found: {dataset_path}")
    
    ext = os.path.splitext(dataset_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(dataset_path)
    elif ext in [".xlsx", ".xls"]:
        return pd.read_excel(dataset_path)
    elif ext == ".json":
        return pd.read_json(dataset_path)
    else:
        return pd.read_csv(dataset_path)


class DatasetProfileTool(BaseTool):
    """Tool to generate a comprehensive profile of a dataset."""
    name: str = "dataset_profile_tool"
    description: str = "Generates a full statistical profile of a dataset including shape, column types, missingness, target candidate, and sensitive candidates."

    def execute(self, **kwargs) -> ToolOutput:
        try:
            dataset_path = kwargs.get("dataset_path")
            prof = profile_dataset(dataset_path)
            return ToolOutput(
                success=True,
                data=prof.model_dump(),
                observation=f"Dataset '{prof.file_name}' contains {prof.row_count} rows and {prof.column_count} columns across {len(prof.columns)} features."
            )
        except Exception as e:
            return ToolOutput(success=False, data={}, observation=f"Dataset profiling failed: {str(e)}")


class MissingnessAnalysisTool(BaseTool):
    """Tool to analyze missing data patterns across columns."""
    name: str = "missingness_analysis_tool"
    description: str = "Analyzes missing-value patterns, missingness percentages, and correlations in missingness across features."

    def execute(self, **kwargs) -> ToolOutput:
        try:
            df = load_dataframe_from_kwargs(kwargs)
            missing_counts = df.isnull().sum().to_dict()
            total_rows = len(df)
            missing_stats = {
                col: {
                    "count": int(cnt),
                    "percentage": round(float(cnt / total_rows * 100), 2)
                }
                for col, cnt in missing_counts.items() if cnt > 0
            }

            obs = (
                f"Found missing values in {len(missing_stats)} columns out of {len(df.columns)}. "
                + ", ".join([f"{col}: {info['count']} ({info['percentage']}%)" for col, info in list(missing_stats.items())[:5]])
                if missing_stats else "No missing values observed in dataset."
            )
            return ToolOutput(success=True, data={"missing_stats": missing_stats, "total_rows": total_rows}, observation=obs)
        except Exception as e:
            return ToolOutput(success=False, data={}, observation=f"Missingness analysis failed: {str(e)}")


class ClassDistributionTool(BaseTool):
    """Tool to analyze target variable class balance and representation."""
    name: str = "class_distribution_tool"
    description: str = "Computes class balance, proportions, and imbalance ratios for the target outcome column."

    def execute(self, **kwargs) -> ToolOutput:
        try:
            df = load_dataframe_from_kwargs(kwargs)
            target_col = kwargs.get("target_column") or kwargs.get("target_col")
            if not target_col or target_col not in df.columns:
                return ToolOutput(success=False, data={}, observation=f"Target column '{target_col}' not found in dataset.")

            counts = df[target_col].value_counts(dropna=False).to_dict()
            total = len(df)
            proportions = {str(k): round(float(v / total), 4) for k, v in counts.items()}

            obs = f"Class distribution for '{target_col}': " + ", ".join([f"Group '{k}': {v} ({round(proportions[str(k)]*100, 1)}%)" for k, v in counts.items()])
            return ToolOutput(success=True, data={"target_column": target_col, "counts": {str(k): int(v) for k, v in counts.items()}, "proportions": proportions}, observation=obs)
        except Exception as e:
            return ToolOutput(success=False, data={}, observation=f"Class distribution analysis failed: {str(e)}")


class GroupDistributionTool(BaseTool):
    """Tool to evaluate subgroup outcome rates across sensitive categories."""
    name: str = "group_distribution_tool"
    description: str = "Compares target outcome rates across subgroups of a sensitive attribute (e.g., approval rate by gender)."

    def execute(self, **kwargs) -> ToolOutput:
        try:
            df = load_dataframe_from_kwargs(kwargs)
            sensitive_col = kwargs.get("sensitive_column")
            target_col = kwargs.get("target_column")

            if not sensitive_col or sensitive_col not in df.columns:
                return ToolOutput(success=False, data={}, observation=f"Sensitive column '{sensitive_col}' not found in dataset.")
            if not target_col or target_col not in df.columns:
                return ToolOutput(success=False, data={}, observation=f"Target column '{target_col}' not found in dataset.")

            # Compute subgroup rates
            grouped = df.groupby(sensitive_col)[target_col]
            group_stats = {}
            for g_name, g_data in df.groupby(sensitive_col):
                g_str = str(g_name)
                total_cnt = len(g_data)
                
                # Check for positive outcome (binary or string match)
                pos_vals = [v for v in g_data[target_col] if str(v).lower() in ["1", "true", "y", "yes", "approved", "positive", "1.0"]]
                if not pos_vals:
                    # Fallback to majority value if binary
                    val_counts = g_data[target_col].value_counts()
                    pos_cnt = int(val_counts.iloc[0]) if len(val_counts) > 0 else 0
                else:
                    pos_cnt = len(pos_vals)

                rate = round(float(pos_cnt / total_cnt), 4) if total_cnt > 0 else 0.0
                group_stats[g_str] = {
                    "total_count": total_cnt,
                    "positive_count": pos_cnt,
                    "positive_rate": rate
                }

            rates_str = ", ".join([f"Group '{k}': {info['positive_rate']*100:.1f}% approval ({info['positive_count']}/{info['total_count']})" for k, info in group_stats.items()])
            obs = f"Subgroup outcome rates for target '{target_col}' by sensitive attribute '{sensitive_col}': {rates_str}."
            return ToolOutput(success=True, data={"sensitive_column": sensitive_col, "target_column": target_col, "group_stats": group_stats}, observation=obs)
        except Exception as e:
            return ToolOutput(success=False, data={}, observation=f"Group distribution tool failed: {str(e)}")


class ProxyAnalysisTool(BaseTool):
    """Tool to analyze proxy relationships for sensitive attributes."""
    name: str = "proxy_analysis_tool"
    description: str = "Computes statistical association strength between sensitive attributes and candidate proxy features."

    def execute(self, **kwargs) -> ToolOutput:
        try:
            df = load_dataframe_from_kwargs(kwargs)
            sens_col = kwargs.get("sensitive_column")
            target_col = kwargs.get("target_column")
            sens_list = [sens_col] if sens_col else [c for c in df.columns if str(c).lower() in ["gender", "age", "race", "zip", "zipcode"]]
            
            candidates = detect_proxy_attributes(df, sens_list, target_col)
            cand_dicts = [c.model_dump() for c in candidates]

            if candidates:
                top = candidates[0]
                obs = f"Proxy analysis identified top candidate '{top.proxy_column}' associated with '{top.sensitive_column}' ({top.association_type} = {top.strength_score})."
            else:
                obs = "Proxy analysis found no strong feature proxy associations above threshold (0.25)."

            return ToolOutput(success=True, data={"proxy_candidates": cand_dicts}, observation=obs)
        except Exception as e:
            return ToolOutput(success=False, data={}, observation=f"Proxy analysis tool failed: {str(e)}")


class ControlledSubgroupComparisonTool(BaseTool):
    """Tool to perform controlled subgroup analysis holding confounding variables constant."""
    name: str = "controlled_subgroup_comparison_tool"
    description: str = "Compares outcome rates across sensitive subgroups while controlling for confounding variables (e.g. income or credit score bands)."

    def execute(self, **kwargs) -> ToolOutput:
        try:
            df = load_dataframe_from_kwargs(kwargs)
            sensitive_col = kwargs.get("sensitive_column")
            target_col = kwargs.get("target_column")
            control_col = kwargs.get("control_column") or kwargs.get("confounding_column")

            if not sensitive_col or sensitive_col not in df.columns:
                return ToolOutput(success=False, data={}, observation=f"Sensitive column '{sensitive_col}' not found.")
            if not target_col or target_col not in df.columns:
                return ToolOutput(success=False, data={}, observation=f"Target column '{target_col}' not found.")
            if not control_col or control_col not in df.columns:
                # Pick a numeric or categorical feature if not provided
                num_cols = [c for c in df.columns if c not in [sensitive_col, target_col] and pd.api.types.is_numeric_dtype(df[c])]
                control_col = num_cols[0] if num_cols else df.columns[0]

            # Bin control column if continuous numeric
            work_df = df.copy()
            if pd.api.types.is_numeric_dtype(work_df[control_col]) and work_df[control_col].nunique() > 5:
                work_df["control_bin"] = pd.qcut(work_df[control_col], q=3, duplicates="drop").astype(str)
                bin_col = "control_bin"
            else:
                bin_col = control_col

            results = {}
            summary_lines = []

            for bin_val, sub_df in work_df.groupby(bin_col):
                bin_str = str(bin_val)
                g_stats = {}
                for g_name, g_data in sub_df.groupby(sensitive_col):
                    total_cnt = len(g_data)
                    pos_vals = [v for v in g_data[target_col] if str(v).lower() in ["1", "true", "y", "yes", "approved", "positive", "1.0"]]
                    pos_cnt = len(pos_vals) if pos_vals else (int(g_data[target_col].value_counts().iloc[0]) if len(g_data) > 0 else 0)
                    rate = round(float(pos_cnt / total_cnt), 4) if total_cnt > 0 else 0.0
                    g_stats[str(g_name)] = {"total": total_cnt, "positive": pos_cnt, "rate": rate}

                results[bin_str] = g_stats
                group_rates = [f"{k}: {v['rate']*100:.1f}%" for k, v in g_stats.items()]
                summary_lines.append(f"In stratum '{bin_str}' ({control_col}): " + ", ".join(group_rates))

            obs = f"Controlled subgroup analysis for '{sensitive_col}' controlling for '{control_col}': " + " | ".join(summary_lines[:3]) + "."
            return ToolOutput(
                success=True,
                data={
                    "sensitive_column": sensitive_col,
                    "target_column": target_col,
                    "control_column": control_col,
                    "controlled_strata_results": results
                },
                observation=obs
            )
        except Exception as e:
            return ToolOutput(success=False, data={}, observation=f"Controlled subgroup comparison failed: {str(e)}")


class GroupPerformanceAnalysisTool(BaseTool):
    """Tool to compute model performance metrics by subgroup when predictions are provided (Mode B/C)."""
    name: str = "group_performance_analysis_tool"
    description: str = "Computes accuracy, precision, recall, and error rate disparities across sensitive subgroups when model predictions are provided."

    def execute(self, **kwargs) -> ToolOutput:
        try:
            df = load_dataframe_from_kwargs(kwargs)
            sensitive_col = kwargs.get("sensitive_column")
            target_col = kwargs.get("target_column")
            pred_col = kwargs.get("prediction_column") or "prediction"

            if pred_col not in df.columns:
                # Try finding prediction column candidates
                p_cands = [c for c in df.columns if "pred" in str(c).lower() or "output" in str(c).lower()]
                if p_cands:
                    pred_col = p_cands[0]
                else:
                    return ToolOutput(success=False, data={}, observation="No prediction column found for Mode B performance analysis.")

            perf_by_group = {}
            for g_name, g_data in df.groupby(sensitive_col):
                y_true = g_data[target_col].astype(str).values
                y_pred = g_data[pred_col].astype(str).values
                acc = float(np.mean(y_true == y_pred)) if len(y_true) > 0 else 0.0
                perf_by_group[str(g_name)] = {
                    "sample_size": len(g_data),
                    "accuracy": round(acc, 4)
                }

            obs = f"Subgroup performance evaluation using prediction column '{pred_col}': " + ", ".join([f"Group '{k}': Acc = {v['accuracy']*100:.1f}%" for k, v in perf_by_group.items()])
            return ToolOutput(success=True, data={"group_performance": perf_by_group}, observation=obs)
        except Exception as e:
            return ToolOutput(success=False, data={}, observation=f"Group performance analysis failed: {str(e)}")


class ErrorRateAnalysisTool(BaseTool):
    """Tool to compute false positive and false negative rates across subgroups."""
    name: str = "error_rate_analysis_tool"
    description: str = "Computes False Positive Rates (FPR) and False Negative Rates (FNR) across subgroups to identify error disparities."

    def execute(self, **kwargs) -> ToolOutput:
        try:
            df = load_dataframe_from_kwargs(kwargs)
            sensitive_col = kwargs.get("sensitive_column")
            target_col = kwargs.get("target_column")
            pred_col = kwargs.get("prediction_column") or "prediction"

            if pred_col not in df.columns:
                p_cands = [c for c in df.columns if "pred" in str(c).lower() or "output" in str(c).lower()]
                if p_cands:
                    pred_col = p_cands[0]
                else:
                    return ToolOutput(success=False, data={}, observation="No prediction column found for error rate analysis.")

            error_stats = {}
            for g_name, g_data in df.groupby(sensitive_col):
                y_true = g_data[target_col].astype(str).str.lower()
                y_pred = g_data[pred_col].astype(str).str.lower()
                
                pos_val = "1"
                fp = np.sum((y_true != pos_val) & (y_pred == pos_val))
                tn = np.sum((y_true != pos_val) & (y_pred != pos_val))
                fn = np.sum((y_true == pos_val) & (y_pred != pos_val))
                tp = np.sum((y_true == pos_val) & (y_pred == pos_val))

                fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
                fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

                error_stats[str(g_name)] = {
                    "fpr": round(fpr, 4),
                    "fnr": round(fnr, 4),
                    "sample_size": len(g_data)
                }

            obs = f"Error rate breakdown by '{sensitive_col}': " + ", ".join([f"Group '{k}': FPR={v['fpr']*100:.1f}%, FNR={v['fnr']*100:.1f}%" for k, v in error_stats.items()])
            return ToolOutput(success=True, data={"error_rates": error_stats}, observation=obs)
        except Exception as e:
            return ToolOutput(success=False, data={}, observation=f"Error rate analysis failed: {str(e)}")
