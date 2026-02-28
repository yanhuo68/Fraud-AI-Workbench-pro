# 🎥 Multimodal RAG Assistant — User Manual

**Page:** Multimodal RAG Assistant (`pages/4_🎥_Multimodal_RAG_Assistant.py (wrapper for src/views/multimodal_rag/)`)  
**Access Level:** Authenticated Users

---

## Overview

The **Multimodal RAG Assistant** lets investigators chat with physical evidence: documents, images, audio recordings, and video files. The assistant reads file content and answers questions combining evidence from multiple sources.

---

## Supported File Types

| Type | Extensions | How It's Processed |
|---|---|---|
| Documents | `.pdf`, `.txt`, `.md` | Full text extraction → Knowledge Base |
| Images | `.png`, `.jpg`, `.jpeg` | Vision model analysis + OCR |
| Audio | `.mp3`, `.wav`, `.m4a` | Whisper transcription → text |
| Video | `.mp4`, `.mov` | Frame sampling + audio transcription |

---

## Interface Layout

```
┌───────────────────┬────────────────────────────────────┐
│ Sidebar            │ Chat area (history + input)        │
│ - File selector    │                                    │
│ - LLM selector     │ File preview pane (right)          │
│ - Suggest questions│                                    │
└───────────────────┴────────────────────────────────────┘
```

---

## Step-by-Step Usage

### Step 1 — Select Files to Chat With

In the sidebar, use the **File Selector** multi-select dropdown to choose which uploaded files to include as context.

> Files must first be uploaded via the **📁 Data Hub**. The Multimodal RAG Assistant reads from the indexed Knowledge Base.

### Step 2 — Choose Your LLM

Select from cloud models (OpenAI, Anthropic, Google) or local Ollama models. For image analysis, a vision-capable model (GPT-4o, Claude 3.5, Gemini 1.5 Pro) is recommended.

### Step 3 — Get Suggested Questions *(Optional)*

Click **💡 Suggest Questions** in the sidebar to get AI-generated questions based on the selected files. Click a suggestion to pre-fill the chat input.

### Step 4 — Ask a Question

Type your question in the chat input, for example:
- *"What does this receipt show?"*
- *"Summarize the key points from the uploaded PDF."*
- *"What is said in the audio recording between 2:30 and 3:00?"*
- *"Does the image contain any license plate numbers?"*
- *"Compare the transaction amounts in the document with what's in our SQL data."*

### Step 5 — Review the Response

The assistant returns a detailed answer with:
- Excerpts from the relevant document/file sections
- Image descriptions or transcriptions if applicable
- Language-matched response (the assistant replies in the same language as your question)

---

## Key Features

### 🌐 Multilingual Support

The assistant detects the language of your question and replies in the same language, making it suitable for international fraud investigations.

### 🔒 Hallucination Guards

The system prompt includes explicit instructions to:
- Only cite information found in the provided files
- Say "I don't know" rather than fabricating answers
- Flag uncertainty when evidence is unclear

### 📄 Cross-Source Correlation

You can ask questions that span multiple file types, for example:
- *"Does the name on the receipt match any customer in our database?"*
- *"Confirm the payment amount from the audio memo matches the transaction CSV."*

---

## Sidebar Options

| Option | Description |
|---|---|
| **File Selector** | Choose which indexed files to include as context |
| **LLM** | Language model for answering |
| **Suggest Questions** | Auto-generate questions from selected files |
| **Max Context Chunks** | Number of Knowledge Base chunks to retrieve (1–10) |

---

## Tips

- For large PDFs, increase **Max Context Chunks** to include more content per answer.
- Video files are processed by sampling frames every N seconds — expect longer ingestion times.
- If a file isn't appearing in the selector, go to **Data Hub** and re-upload it.
- Image analysis quality depends on the LLM — GPT-4o and Claude 3.5 have the best vision capabilities.
