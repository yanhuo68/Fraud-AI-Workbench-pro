@echo off
REM ============================================================
REM  setup_infra.bat
REM  Windows setup script for Neo4j Graph Store infrastructure.
REM  Run this ONCE before starting the main application stack.
REM
REM  Requirements:
REM    - Docker Desktop for Windows (running)
REM    - GRAPH_STORE_PASSWORD set in .env file
REM
REM  Usage:
REM    Double-click this file, OR run from CMD / PowerShell:
REM      > setup_infra.bat
REM ============================================================

echo.
echo ==========================================================
echo   Sentinel Infrastructure Setup (Windows)
echo ==========================================================
echo.

REM ── 1. Ensure Docker is running ───────────────────────────────
docker info >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker Desktop is not running.
    echo         Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM ── 2. Create shared Docker network (idempotent) ──────────────
echo [1/4] Ensuring fraud_network Docker network exists...
docker network create fraud_network 2>nul
REM Exit code 1 just means it already exists -- that's fine
echo       Done.

REM ── 3. Clear stale Neo4j PID file (handles unclean shutdown) ──
echo [2/4] Checking for stale Neo4j PID file...
SET PID_FILE=data\neo4j\data\server.pid
IF EXIST "%PID_FILE%" (
    echo       Removing stale PID file: %PID_FILE%
    del /f "%PID_FILE%"
) ELSE (
    echo       No stale PID file found.
)

REM ── 4. Create Neo4j data directories if missing ───────────────
echo [3/4] Ensuring Neo4j data directories exist...
IF NOT EXIST "data\neo4j\data"   mkdir "data\neo4j\data"
IF NOT EXIST "data\neo4j\logs"   mkdir "data\neo4j\logs"
IF NOT EXIST "data\neo4j\import" mkdir "data\neo4j\import"
echo       Done.

REM ── 5. Start Neo4j container ──────────────────────────────────
echo [4/4] Starting Neo4j container (docker-compose.neo4j.yml)...
docker compose -f docker-compose.neo4j.yml up -d
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to start Neo4j. Check docker-compose.neo4j.yml and your .env file.
    pause
    exit /b 1
)

echo.
echo ==========================================================
echo   Neo4j is starting in the background.
echo.
echo   - Plugins (GDS/APOC) take ~60 seconds to initialize.
echo   - Watch logs:   docker logs -f fraud_neo4j
echo   - Neo4j Browser: http://localhost:7474
echo     (login: neo4j / your GRAPH_STORE_PASSWORD from .env)
echo.
echo   Once healthy, start the application:
echo     docker compose up --build
echo ==========================================================
echo.
pause
