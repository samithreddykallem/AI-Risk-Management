import logging
from typing import Optional, List, Any
from fastapi import FastAPI, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import shutil


from app.schemas.project import ProjectInput, TestLLMRequest, TestLLMResponse, AuditRequest, AuditResponse
from app.schemas.dataset import DatasetProfile
from app.schemas.system_profile import SystemProfile
from app.schemas.hypothesis import HypothesisGenerationRequest, HypothesisGenerationResponse

from services.dataset_profiler import profile_dataset
from services.llm_roles import run_system_analyst_role, run_hypothesis_generator_role
from services.report_generator import generate_human_readable_report
from app.services.adaptive_agent import AdaptiveInvestigationAgent
from app.core.llm import get_llm_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_engine.app")

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="AI Risk Manager - AI Engine",
    description="Adaptive Ethical Auditor for AI Systems API Service",
    version="0.5.0"
)

# Enable CORS for local frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", status_code=status.HTTP_200_OK, summary="Root Service Identification")
async def root():
    return {
        "service": "AI Risk Manager - AI Engine",
        "status": "running"
    }


@app.get("/health", status_code=status.HTTP_200_OK, summary="Health Check")
async def health_check():
    return {
        "status": "healthy"
    }


@app.post(
    "/engine/upload-dataset",
    status_code=status.HTTP_200_OK,
    summary="Upload Dataset File (CSV, XLSX, JSON)"
)
async def upload_dataset_endpoint(file: UploadFile = File(...)):
    """Uploads a dataset file safely, stores it in uploads/ directory, and returns dataset path."""
    try:
        sanitized_filename = f"{uuid.uuid4().hex[:6]}_{os.path.basename(file.filename)}"
        saved_path = os.path.join(UPLOAD_DIR, sanitized_filename)
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info("Dataset uploaded successfully: %s -> %s", file.filename, saved_path)
        return {
            "status": "success",
            "file_name": file.filename,
            "dataset_path": saved_path
        }
    except Exception as e:
        logger.error("Error uploading dataset: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to upload dataset: {str(e)}")


@app.post(
    "/engine/profile-dataset",
    response_model=DatasetProfile,
    status_code=status.HTTP_200_OK,
    summary="Generate Comprehensive Dataset Profile"
)
async def profile_dataset_endpoint(
    dataset_path: str = Form(...),
    dataset_name: Optional[str] = Form(None),
    target_column: Optional[str] = Form(None)
):
    try:
        prof = profile_dataset(
            file_path=dataset_path,
            dataset_name=dataset_name,
            user_target_column=target_column
        )
        return prof
    except Exception as e:
        logger.error("Error profiling dataset: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to profile dataset: {str(e)}")


@app.post(
    "/engine/audit",
    response_model=AuditResponse,
    status_code=status.HTTP_200_OK,
    summary="Dataset-Driven End-to-End Adaptive AI Audit"
)
async def audit_endpoint(payload: AuditRequest):
    """
    Executes a complete adaptive ethical audit in one API call:
    Dataset Ingestion -> Profiling -> Sensitive & Proxy Discovery -> System Analyst Role ->
    Hypothesis Generation -> Adaptive Investigation Loop with Evidence Critic -> Markdown Report.
    """
    try:
        audit_id = f"AUDIT-{uuid.uuid4().hex[:8]}"
        logger.info("Starting complete adaptive audit [%s] for project: %s", audit_id, payload.project.project_name)

        # 1. Dataset Ingestion & Profiling if dataset_path provided
        dataset_prof: Optional[DatasetProfile] = payload.dataset_profile
        if not dataset_prof and payload.project.dataset_path and os.path.exists(payload.project.dataset_path):
            dataset_prof = profile_dataset(
                file_path=payload.project.dataset_path,
                dataset_name=payload.project.dataset_name,
                user_target_column=payload.project.target_column,
                user_sensitive_attributes=payload.project.sensitive_attributes,
                predictions_path=payload.project.predictions_path,
                model_artifact_path=payload.project.model_artifact_path
            )

        # 2. System Analyst Role -> System Profile
        profile = run_system_analyst_role(payload.project, dataset_prof)
        if dataset_prof:
            setattr(profile, "dataset_path", payload.project.dataset_path)
            setattr(profile, "dataset_name", payload.project.dataset_name)
            setattr(profile, "target_candidate", dataset_prof.target_candidate)
            setattr(profile, "sensitive_candidates", dataset_prof.sensitive_candidates)

        # 3. Hypothesis Generator Role
        hypotheses = run_hypothesis_generator_role(profile, dataset_prof)

        # 4. Adaptive Investigation Loop with Evidence Critic
        agent = AdaptiveInvestigationAgent()
        adaptive_result = agent.run_adaptive_loop(
            system_profile=profile,
            hypotheses=hypotheses,
            available_tools=payload.available_tools,
            max_iterations=payload.max_iterations or 3
        )

        # 5. Generate Human-Readable Markdown Audit Report
        report_md = generate_human_readable_report(
            project=payload.project,
            system_profile=profile,
            dataset_profile=dataset_prof,
            hypotheses=hypotheses,
            iterations=adaptive_result.iterations,
            final_evidence=adaptive_result.final_evidence,
            unresolved_questions=adaptive_result.unresolved_questions,
            limitations=adaptive_result.limitations
        )

        return AuditResponse(
            audit_id=audit_id,
            system_profile=profile,
            dataset_profile=dataset_prof,
            hypotheses=hypotheses,
            investigation_trace=adaptive_result.iterations,
            final_evidence=adaptive_result.final_evidence,
            unresolved_questions=adaptive_result.unresolved_questions,
            limitations=adaptive_result.limitations,
            audit_report_markdown=report_md,
            status=adaptive_result.status
        )

    except Exception as e:
        logger.error("Error executing dataset-driven audit: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Adaptive audit execution failed: {str(e)}"
        )




if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
