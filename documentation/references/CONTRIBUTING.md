# Contributing to Fraud Investigation Workbench Pro

Thank you for your interest in contributing to the Fraud Investigation Workbench Pro! This platform handles sensitive data schemas and relies on multiple interconnected AI agents. To ensure the highest level of stability, we enforce a strict testing policy.

## 🛠️ Development Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Fraud-AI-Workbench-pro
   ```

2. **Set up a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install pytest flake8
   ```

3. **Configure your environment:**
   Copy `.env.example` to `.env` and fill in necessary keys (at minimum, an LLM API key).

## 🧪 Testing Policy

**CRITICAL:** You must run and pass the test suite before opening a Pull Request. Our CI/CD pipeline (GitHub Actions) will reject any PR that fails the test suite.

We have three levels of tests located in the `tests/` directory:

### 1. Unit Tests (`tests/unit/`)
Unit tests cover isolated logic like SQL validation, data prep, and agent behavior. 
- **Requirement:** New features or agents *must* include corresponding unit tests.
- **Run them locally:**
  ```bash
  PYTHONPATH=src pytest tests/unit/ -v
  ```

### 2. Integration Tests (`tests/integration/`)
These test the FastAPI backend endpoints.
- **Requirement:** If you modify an API route in `src/api/routers/`, you must update or add an integration test.
- **Run them locally:** You MUST have the backend running.
  ```bash
  # 1. Start the stack
  docker-compose up -d
  # 2. Run the tests against localhost:8000
  PYTHONPATH=src pytest tests/integration/ -v
  ```

### 3. End-to-End Tests (`tests/e2e/`)
Ensures critical user workflows (like data ingestion followed by ML training) work in sequence.

---

## 🚀 The CI/CD Pipeline

Our GitHub Repo utilizes **GitHub Actions**. Every time you push to `main` or open a PR, the [CI Pipeline](.github/workflows/ci.yml) will trigger:

1. **Linting Check:** Ensures your Python code has no major syntax errors using `flake8`.
2. **Unit Test Job:** Sets up a temporary Python environment and runs the `tests/unit/` suite.
3. **Integration Job (Dockerized):** If unit tests pass, the Action spins up the full `docker-compose.yml` stack (FastAPI + Streamlit + Neo4j) and executes the `tests/integration/` and `tests/e2e/` suites against the live containers.

### How to Fix CI Failures
If the GitHub Action fails:
1. Click into the Action logs in GitHub.
2. Identify if it failed on Linting, Unit, or Integration.
3. Run that specific test locally using the commands above to replicate the failure.
4. Push your fix to the same branch; the Action will re-run automatically.
