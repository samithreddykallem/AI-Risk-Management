from fastapi.testclient import TestClient
from app.main import app
from app.core.llm import get_llm_client

client = TestClient(app)


def test_llm_client_instantiation():
    llm = get_llm_client()
    assert llm is not None
    response = llm.generate_text("Test prompt")
    assert isinstance(response, str)
    assert len(response) > 0


def test_post_engine_test_llm():
    response = client.post("/engine/test-llm", json={"message": "Say hello"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert isinstance(data["response"], str)
