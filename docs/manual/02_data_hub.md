# 02. Data Hub (Upload Data)

The **Data Hub** is the foundation of your fraud investigation. It handles the secure ingestion of structured and unstructured data into the Sentinel ecosystem.

## 📁 1. File Ingestion

You can upload various file types to the backend for processing:
- **CSV**: Automatically converted into SQLite tables. The system detects headers and data types.
- **Documents (PDF, TXT, JSON, MD)**: Used for knowledge-base retrieval in RAG workflows.
- **SQL Scripts**: Upload `.sql` files to execute bulk schema changes or data migrations directly on the project database.

### How to upload:
1. Navigate to the **Data Hub**.
2. Use the **Upload file** widget to select your source data.
3. Click **Upload to Backend**. The system will provide a real-time status of the processing.

## 🎥 2. Media & Picture Repository

- **Media Uploads**: Save audio and video for manual review or future multimodal analysis. Files are stored in `data/mediauploads`.
- **Picture Uploads**: Store images (received receipts, suspicious identity documents) in `data/pictureuploads`.

## 💬 3. Interactive Data Chat

Before moving to the dedicated RAG assistants, you can use the **Chat with Uploaded Data** section for quick exploration.

- **Source Selection**: Choose between a specific uploaded file or an existing SQL table.
- **Sample Generation**: Click **Load & Generate Sample Questions** to let the AI analyze the data structure and provide starting points for your analysis.
- **Instant Analysis**: Chat directly with your data using an integrated Pandas or Text assistant.

## 🕸️ 4. Graph Architecture

The **Graph Store Visualization** section provides a high-level view of how your project data is linked.
- **Tables**: Represented as green nodes.
- **Documents**: Represented as wheat-colored nodes.
- **Relationships**: Automatically inferred links between your data sources.

## 🛡️ 5. Admin Utilities (Restricted)

Authorized administrators can access additional controls:
- **Clean DB**: Wipes and resets the SQLite data store.
- **Delete Uploads**: Clears the filesystem of ingestion artifacts.
- **Rebuild Graph**: Regenerates the Neo4j network from raw files.
- **Project Data to Graph**: Forces a sync from the SQLite relational DB to the Neo4j graph DB.

> [!WARNING]
> Administrative utilities like **Clean DB** are destructive. Ensure you have backups before proceeding.
