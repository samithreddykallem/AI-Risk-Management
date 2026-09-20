import os

target = r"c:\Users\yerra\OneDrive\Desktop\AI-Risk-Management\app\services\ai_engine_service.py"
content = '''import os
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any

logger = logging.getLogger("app.services.ai_engine_service")

AI_ENGINE_URL = os.getenv("AI_ENGINE_URL", "http://127.0.0.1:8000").rstrip("/")


def run_ai_engine_audit(
    project_data: Dict[str, Any],
    available_tools: list = None,
    max_iterations: int = 3
) -> Dict[str, Any]:
    """
    Sends HTTP POST request to AI Engine endpoint: POST ${AI_ENGINE_URL}/engine/audit
    Returns the complete audit result JSON.
    """
    target_url = f"{AI_ENGINE_URL}/engine/audit"
    logger.info("Calling AI Engine audit service at: %s", target_url)

    payload = {
        "project": {
            "project_name": project_data.get("project_name") or project_data.get("name") or "Unnamed Project",
            "description": project_data.get("description") or "",
            "github_url": project_data.get("github_url"),
            "documentation": project_data.get("documentation") or "",
            "sample_inputs": project_data.get("sample_inputs") or [],
            "sample_outputs": project_data.get("sample_outputs") or []
        },
        "available_tools": available_tools or ["analysis_tool", "model_tool", "repository_tool"],
        "max_iterations": max_iterations or 3
    }

    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        target_url,
        data=data_bytes,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            resp_body = response.read().decode("utf-8")
            result = json.loads(resp_body)
            logger.info("Successfully received audit response from AI Engine (audit_id: %s)", result.get("audit_id"))
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else str(e)
        logger.error("AI Engine HTTP error (%d): %s", e.code, error_body)
        raise RuntimeError(f"AI Engine HTTP Error {e.code}: {error_body}") from e
    except urllib.error.URLError as e:
        logger.error("Failed to connect to AI Engine at %s: %s", target_url, str(e))
        raise RuntimeError(f"Could not connect to AI Engine service at {target_url}. Ensure AI Engine is running.") from e
    except Exception as e:
        logger.error("Unexpected error communicating with AI Engine: %s", str(e))
        raise RuntimeError(f"AI Engine Communication Error: {str(e)}") from e
'''

os.makedirs(os.path.dirname(target), exist_ok=True)
with open(target, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated ai_engine_service.py successfully")
