#!/bin/bash
# ============================================================
#  setup_infra.sh
#  Mac / Linux setup script for Neo4j Graph Store infrastructure.
#  Run this ONCE before starting the main application stack.
#
#  Requirements:
#    - Docker Desktop (Mac) or Docker Engine (Linux) running
#    - GRAPH_STORE_PASSWORD set in .env file
#
#  Usage:
#    chmod +x setup_infra.sh
#    ./setup_infra.sh
# ============================================================

set -e

echo ""
echo "=========================================================="
echo "  Sentinel Infrastructure Setup (Mac / Linux)"
echo "=========================================================="
echo ""

# ── 1. Ensure Docker is running ───────────────────────────────
if ! docker info > /dev/null 2>&1; then
    echo "[ERROR] Docker is not running."
    echo "        Please start Docker Desktop and try again."
    exit 1
fi

# ── 2. Create shared Docker network (idempotent) ──────────────
echo "[1/4] Ensuring fraud_network Docker network exists..."
docker network create fraud_network 2>/dev/null || true
echo "      Done."

# ── 3. Clear stale Neo4j PID file (handles unclean shutdown) ──
echo "[2/4] Checking for stale Neo4j PID file..."
PID_FILE="data/neo4j/data/server.pid"
if [ -f "$PID_FILE" ]; then
    echo "      Removing stale PID file: $PID_FILE"
    rm "$PID_FILE"
else
    echo "      No stale PID file found."
fi

# ── 4. Create Neo4j data directories if missing ───────────────
echo "[3/4] Ensuring Neo4j data directories exist..."
mkdir -p data/neo4j/data data/neo4j/logs data/neo4j/import
echo "      Done."

# ── 5. Start Neo4j container ──────────────────────────────────
echo "[4/4] Starting Neo4j container (docker-compose.neo4j.yml)..."
docker compose -f docker-compose.neo4j.yml up -d

echo ""
echo "=========================================================="
echo "  Neo4j is starting in the background."
echo ""
echo "  - Plugins (GDS/APOC) take ~60 seconds to initialize."
echo "  - Watch logs:    docker logs -f fraud_neo4j"
echo "  - Neo4j Browser: http://localhost:7474"
echo "    (login: neo4j / your GRAPH_STORE_PASSWORD from .env)"
echo ""
echo "  Once healthy, start the application:"
echo "    docker compose up --build"
echo "=========================================================="
echo ""
