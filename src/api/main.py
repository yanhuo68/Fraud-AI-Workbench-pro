from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

from api.routers import ml, rag, ingest, health, agents, models, reports, auth, keys, admin
from config.settings import settings
from config.logging_conf import setup_logging
from scripts.setup.init_users import init_user_db

# Initialize logging
setup_logging(log_file=settings.log_file, level=settings.log_level)
logger = logging.getLogger(__name__)

# Initialize user database & roles
try:
    init_user_db()
except Exception as e:
    logger.error(f"Failed to initialize user database: {e}")

# Debug settings
logger.info(f"Loaded Settings: URI={settings.graph_store_uri}, User={settings.graph_store_user}")

from contextlib import asynccontextmanager
import asyncio

async def _verify_neo4j_connectivity():
    max_retries = 10
    retry_delay = 10
    connected = False
    
    logger.info("📡 Checking Neo4j Graph Store connectivity in background...")
    for i in range(max_retries):
        try:
            driver = settings.graph_driver
            driver.verify_connectivity()
            logger.info("✅ Neo4j connection verified.")
            connected = True
            break
        except Exception as e:
            logger.warning(f"⏳ Neo4j not ready (attempt {i+1}/{max_retries}): {e}")
            if i < max_retries - 1:
                await asyncio.sleep(retry_delay)
    
    if not connected:
        logger.error("❌ Could not connect to Neo4j. Graph features will be disabled or unstable.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start Neo4j Connectivity check as a background task
    asyncio.create_task(_verify_neo4j_connectivity())
    
    yield
    # Shutdown logic (optional)
    try:
        settings.graph_driver.close()
    except Exception:
        pass

app = FastAPI(title="Fraud Analytics API", version="1.1", lifespan=lifespan)

# Enable CORS with restricted origins from settings
allowed_origins = settings.get_allowed_origins_list()
logger.info(f"CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# Register routers
app.include_router(health.router)
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(keys.router, prefix="/keys", tags=["API Keys"])
app.include_router(rag.router, prefix="/rag", tags=["RAG"])
app.include_router(ml.router, prefix="/ml", tags=["Scoring (Legacy ML)"])
app.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])
app.include_router(agents.router, prefix="/agents", tags=["Agentic RAG"])
app.include_router(models.router, prefix="/models", tags=["Model Registry & Scoring"])
app.include_router(reports.router, prefix="/reports", tags=["Reporting"])

# Admin endpoints for maintenance
app.include_router(admin.router, prefix="/admin", tags=["Admin"])


@app.get("/")
def root():
    return {"message": "Fraud Analytics API Running", "version": "1.0"}

