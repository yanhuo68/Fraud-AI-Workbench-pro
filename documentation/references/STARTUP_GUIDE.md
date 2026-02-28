# 🚀 Starting the Fraud Detection AI Workbench

This guide will walk you through setting up the Fraud Detection AI Workbench on your local machine.


## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.9+**
- **Docker & Docker Compose** (Recommended)
- **Git**

## 🏗️ Architecture Overview

The system operates as a microservices architecture:
1. **Streamlit Frontend** (Port 8504): Investigative UI and dashboards.
2. **FastAPI Backend** (Port 8000): Multi-agent reasoning, RAG engines, and ML inference.
3. **Neo4j** (Port 7474/7687): Graph database for fraud ring discovery.

---

## ⚡ Quick Start (Docker - Recommended)

The easiest way to run the entire stack is using Docker Compose.

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-repo/fraud-tab-b7-v1.git
    cd fraud-tab-b7-v1
    ```

2.  **Environment Setup:**
    ```bash
    cp .env.example .env
    # Edit .env and add your OPENAI_API_KEY and DEEPSEEK_API_KEY
    ```

3.  **Launch the System:**
    ```bash
    docker-compose up --build
    ```

4.  **Access the workbench:**
    - **UI**: [http://localhost:8504](http://localhost:8504)
    - **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠️ Manual Setup (Development)

If you prefer to run services manually for debugging:

### 1. Backend Setup
1. **Create Virtual Environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # .venv\Scripts\activate  # Windows
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize Databases:**
   ```bash
   # Initialize transaction data
   python rag_sql/db_init.py

   # Initialize user accounts and roles (Default: admin/admin123)
   python src/scripts/setup/init_users.py
   ```

4. **Start FastAPI:**

   ```bash
   uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### 2. Frontend Setup
In a new terminal:
```bash
streamlit run app.py
```

### 3. Neo4j Setup (External)
Ensure Neo4j is running locally or in a container with **APOC** and **GDS** plugins installed. Update `GRAPH_STORE_URI` and credentials in your `.env` file.

---

## 🔐 Environment Variables

Key variables required in `.env`:
- `OPENAI_API_KEY`: Required for agentic reasoning and synthesis.
- `DEEPSEEK_API_KEY`: Alternative LLM support.
- `GRAPH_STORE_PASSWORD`: Password for the Neo4j instance.
- `SECRET_KEY`: Used for JWT token generation.

See [.env.example](file:///.env.example) for the full list of configuration options.

---

## 🔍 Troubleshooting

### 1. Connection Refused (Port 8000)
**Cause**: Streamlit cannot find the FastAPI backend.
**Fix**: Ensure the backend is running by visiting `http://localhost:8000/health`. Check logs in Docker or terminal.

### 2. Neo4j Plugin Errors
**Cause**: Graph RAG requires APOC and Graph Data Science plugins.
**Fix**: If using Docker, these are included in the `docker-compose.yml`. If manual, ensure these `.jar` files are in your Neo4j `plugins` folder.

### 3. Port Already in Use (8504/8000)
**Fix**: 
```bash
lsof -i :8504  # Find PID
kill -9 <PID>  # Stop process
```

---

## 📜 Logs & Monitoring
- **App Logs**: Located in `logs/run.log`.
- **Docker Logs**: Run `docker-compose logs -f`.
- **Health Check**: Endpoint available at `/health`.

