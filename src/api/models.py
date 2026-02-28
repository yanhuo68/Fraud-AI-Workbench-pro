from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AgentQueryRequest(BaseModel):
    """Request for full multi-agent RAG query."""
    question: str
    llm_id: str = "openai:gpt-4o-mini"
    k_candidates: int = 3
    rebuild_kb: bool = False
    bypass_agents: bool = False # If true, skips explanation, recon, and synthesis for speed

class AgentQueryResponse(BaseModel):
    """Response from agentic query."""
    sql: str
    explanation: str
    reconciliation: str
    synthesis: str
    results_preview: List[Dict[str, Any]]
    total_rows: int
    columns: List[str]
    anomalies: Optional[List[Dict[str, Any]]] = None
    fraud_risk_report: Optional[str] = None

class ModelScoreRequest(BaseModel):
    """Request for model scoring."""
    model_id: str = Field(..., description="Registered model ID (e.g., 'expert:ID', 'fine-tuned:ID')")
    input_data: Dict[str, Any]

class ModelScoreResponse(BaseModel):
    """Response from model scoring."""
    prediction: Any
    metadata: Dict[str, Any]

class ReportGenerateRequest(BaseModel):
    """Request for report generation."""
    analysis_type: str = "full" # full, summary, fraud
    data_context: Optional[Dict[str, Any]] = None
    format: str = "pdf" # pdf, docx

# --- Authentication Models ---

class UserRegister(BaseModel):
    username: str
    password: str
    email: Optional[str] = None   # Optional — leave blank for demo/service accounts
    role: str = "guest"  # guest or admin

class UserResponse(BaseModel):
    username: str
    role: str
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: int
    username: str
    role: str
    email: Optional[str] = None
