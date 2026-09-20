import os

target = r"c:\Users\yerra\OneDrive\Desktop\AI-Risk-Management\app\main.py"
content = '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.models.project import Project
from app.models.audit import Audit

from app.api.projects import router as project_router
from app.api.audits import router as audit_router, run_audit, AuditRunRequest


# Create database tables
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database init warning: {str(e)}")


app = FastAPI(
    title="AI Risk Manager API",
    version="1.0.0"
)

# Enable CORS for local dev frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Project routes
app.include_router(project_router)

# Register Audit routes
app.include_router(audit_router)


@app.post("/engine/audit", summary="Proxy Audit Request to AI Engine")
def engine_audit_proxy(payload: AuditRunRequest):
    """Proxy endpoint for POST /engine/audit."""
    return run_audit(payload)


@app.get("/")
def root():
    return {
        "message": "AI Risk Manager Backend is running"
    }
'''

os.makedirs(os.path.dirname(target), exist_ok=True)
with open(target, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated team app/main.py successfully")
