# 03. SQL RAG Assistant

The **SQL RAG Assistant** allows you to perform deep investigations of your structured transaction data using straightforward English questions. By combining LLM-powered SQL generation with a Retrieval-Augmented Generation (RAG) pipeline, it bridges the gap between simple data retrieval and expert fraud analysis.

## 🧠 1. Core Workflow

1. **Question Input**: Enter your query in the text area (e.g., *"Which customer has the most frequent high-value transfers?"*).
2. **Multi-Agent Reasoning**:
   - **Planner Agent**: Generates multiple SQL candidates.
   - **Validator Agent**: Checks for security risks and syntax errors.
   - **Reconciliation Agent**: Compares results across candidates to ensure accuracy.
3. **Synthesis**: A senior fraud analyst agent combines the raw data with domain knowledge (retrieved from the RAG knowledge base) to provide a polished narrative report.

## 🛠️ 2. Advanced Controls

- **Bypass Agents (Fast Mode)**: If checked, the system will skip the multi-agent reconciliation and synthesis steps to provide raw SQL results much faster. Recommended for simple counts or data exports.
- **LLM Selection**: You can choose between specialized models (Ollama, LM Studio, or OpenAI) to power your analysis. Special models like "Expert Prompt" versions are tuned for complex SQL joins.

## 📄 3. Report Generation

Once your analysis is complete, you can generate a professional **Fraud Analysis PDF**. This report includes:
- The original question and AI-generated narrative.
- The optimized SQL query used for the investigation.
- A preview of the transaction records.
- Risk scoring and anomaly detection metrics.

> [!TIP]
> Use the **Schema Inspector** in the sidebar to remind yourself of available columns and table relationships before crafting your question.
