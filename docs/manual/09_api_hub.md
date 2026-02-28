# 09. API Interaction Hub

The **API Hub** is the technical bridge between the Sentinel UI and its underlying FastAPI microservices. It is used for health monitoring, API key management, and direct endpoint testing.

## 🔌 1. Integration Workspace

- **API Discovery**: The system automatically detects and lists all registered FastAPI endpoints.
- **Dynamic Testing**: Select an endpoint (e.g., `/ingest/file` or `/agents/query`), provide the necessary JSON parameters or files, and execute a live request directly from the UI.
- **Response Viewer**: Inspect raw JSON responses, status codes, and headers to debug integrations.

## 🔑 2. API Key Management

For external applications needing access to Sentinel's intelligence:
1. Generate **Technical API Keys** with specific scopes (Read-Only vs Full Access).
2. Monitor key usage and last-access timestamps.
3. Revoke keys instantly if compromised.

## 🛡️ 3. System Health

- **Service Status**: Verify that the Database, Vector Store, and LLM Routers are online and responding within acceptable latency limits.
- **Log Stream**: View real-time technical logs from the investigative agents to troubleshoot complex RAG failures.

> [!NOTE]
> All requests made through the API Hub are subject to the same Role-Based Access Control (RBAC) as the UI. Ensure your JWT token is valid.
