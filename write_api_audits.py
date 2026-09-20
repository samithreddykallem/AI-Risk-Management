import os

target = r"c:\Users\yerra\OneDrive\Desktop\AI-Risk-Management\app\api\audits.py"
content = '''from typing import Optional, List, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.audit import AuditCreate, AuditResponse
from app.services.audit_service import (
    create_audit,
    get_audit,
    get_audits
)
from app.services.ai_engine_service import run_ai_engine_audit

router = APIRouter(
    prefix="/api/audits",
    tags=["Audits"]
)


class ProjectPayload(BaseModel):
    project_name: str
    description: str
    github_url: Optional[str] = None
    documentation: Optional[str] = None
    sample_inputs: Optional[List[Any]] = []
    sample_outputs: Optional[List[Any]] = []


class AuditRunRequest(BaseModel):
    project: Optional[ProjectPayload] = None
    project_name: Optional[str] = None
    description: Optional[str] = None
    github_url: Optional[str] = None
    documentation: Optional[str] = None
    sample_inputs: Optional[List[Any]] = []
    sample_outputs: Optional[List[Any]] = []
    available_tools: Optional[List[str]] = ["analysis_tool", "model_tool", "repository_tool"]
    max_iterations: Optional[int] = 3


@router.post(
    "",
    response_model=AuditResponse
)
def create(
    audit: AuditCreate,
    db: Session = Depends(get_db)
):
    return create_audit(db, audit)


@router.post(
    "/run",
    summary="Run AI Engine Audit"
)
def run_audit(payload: AuditRunRequest):
    """Proxies an audit request to the AI Engine service and returns the complete audit trace result."""
    try:
        if payload.project:
            proj_dict = payload.project.model_dump()
        else:
            proj_dict = {
                "project_name": payload.project_name or "Unnamed Project",
                "description": payload.description or "",
                "github_url": payload.github_url,
                "documentation": payload.documentation or "",
                "sample_inputs": payload.sample_inputs or [],
                "sample_outputs": payload.sample_outputs or []
            }

        result = run_ai_engine_audit(
            project_data=proj_dict,
            available_tools=payload.available_tools,
            max_iterations=payload.max_iterations or 3
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get(
    "",
    response_model=list[AuditResponse]
)
def get_all(
    db: Session = Depends(get_db)
):
    return get_audits(db)


@router.get(
    "/{audit_id}",
    response_model=AuditResponse
)
def get_one(
    audit_id: int,
    db: Session = Depends(get_db)
):
    audit = get_audit(db, audit_id)

    if not audit:
        raise HTTPException(
            status_code=404,
            detail="Audit not found"
        )

    return audit
'''

os.makedirs(os.path.dirname(target), exist_ok=True)
with open(target, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated app/api/audits.py successfully")
