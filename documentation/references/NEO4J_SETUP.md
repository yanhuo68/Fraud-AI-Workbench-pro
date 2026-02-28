# 🕸️ Neo4j Standalone Setup Guide

To ensure high stability and fast development cycles, the Neo4j Graph Store has been decoupled from the main application stack. This prevents slow plugin initialization (GDS/APOC) from bottlenecking your work.

## 🚀 One-Time Setup

Run the provided infrastructure script from the project root:

```bash
chmod +x setup_infra.sh
./setup_infra.sh
```

This will:
1. Create the persistent `fraud_network`.
2. Start the `fraud_neo4j` container in the background.
3. Keep it running even when you rebuild the main application.

---

## 🛠️ Maintenance Commands

### Restarting Neo4j
If the database becomes unresponsive:
```bash
docker compose -f docker-compose.neo4j.yml restart
```

### Viewing Database Logs
To watch the plugin initialization progress:
```bash
docker logs -f fraud_neo4j
```

### Stopping Database
```bash
docker compose -f docker-compose.neo4j.yml down
```

---

## ✅ Prerequisite for Main App
Once the database is running (it takes about 60s for the first run), you can start the workbench as usual:
```bash
docker compose up --build
```
