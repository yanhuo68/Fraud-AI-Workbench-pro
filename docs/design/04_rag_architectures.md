# 04. Deep RAG Architectures

Sentinel implements three specialized Retrieval-Augmented Generation (RAG) pipelines, each optimized for a different forensic dimension.

## 📊 1. SQL RAG (Relational Intelligence)

- **Input**: Natural Language (e.g., *"Show me users with >10 transactions in 5 minutes"*).
- **Core Technology**: `sql_ranking_agent` + `sqlite3`.
- **Design Pattern**: **Text-to-SQL-to-Narrative**. 
- **Optimization**: The system uses a "Schema Context" builder that injects table descriptions and sample rows into the prompt to reduce hallucinations on column names.

## 🕸️ 2. Graph RAG (Network Intelligence)

- **Input**: Link-analysis questions (e.g., *"Find accounts sharing the same device ID as Fraudster-X"*).
- **Core Technology**: `neo4j` + `Cypher` optimization agents.
- **Design Pattern**: **Text-to-Cypher Recovery**.
- **Graph Projection**: Raw files are transformed into triples `(Entity)-[ACTION]->(Entity)` during ingestion.
- **Multi-Hop Retrieval**: Unlike SQL, the Graph RAG is optimized for N-degree relationship traversal without exponential performance degradation.

## 🎥 3. Multimodal RAG (Unstructured Evidence)

- **Input**: Images, Audio, Video, or Web URLs.
- **Core Technology**: GPT-4o Vision / Whisper / Markdown web scraping.
- **Design Pattern**: **Evidence-to-Knowledge-Base**.
- **Workflows**:
    1.  **Audio/Video**: Transcribed via Whisper, then indexed into ChromaDB.
    2.  **Vision**: Analyzed for OCR and visual anomalies (e.g., altered documents).
    3.  **Cross-Ref**: The Multimodal RAG can query the SQL RAG results to verify if visual evidence (a physical receipt) matches digital logs.

## 🔍 4. The Vector Store (Retriever Design)

- **Engine**: ChromaDB.
- **Embedding Model**: `text-embeddings-3-small` (default) or local HuggingFace embeddings.
- **Chunking Strategy**: Recursive Character Splitter with a 1000-character chunk size and 100-character overlap to preserve forensic context across segments.
