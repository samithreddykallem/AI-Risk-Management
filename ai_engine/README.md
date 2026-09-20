# AI Risk Manager - AI Engine

The AI Engine for AI Risk Manager is an adaptive ethical auditor for AI systems.

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and set your API key:
```bash
cp .env.example .env
```

### 3. Run the AI Engine Server
Run uvicorn from the `ai_engine/` root directory:
```bash
python -m uvicorn app.main:app --reload
```

The server will start at `http://127.0.0.1:8000`.

## Endpoints

- `GET /`: Service identification status
- `GET /health`: Server health check
- `POST /engine/test-llm`: LLM integration test
- `POST /engine/analyze-project`: System Profile analysis for AI projects
