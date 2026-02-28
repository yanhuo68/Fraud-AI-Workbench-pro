# 🧬 LLM Fine-Tuning Forge — User Manual

**Page:** LLM Fine-Tuning Forge (`pages/9_🧠_LLM_Fine_Tuning.py (wrapper for src/views/llm_fine_tuning/)`)  
**Access Level:** Admin / Data Scientist

---

## Overview

The **LLM Fine-Tuning Forge** enables fine-tuning of open-source language models (Llama 3, Mistral) on your agency-specific fraud investigation data using LoRA / QLoRA techniques. It uses Apple MLX for efficient local training on Apple Silicon hardware, and includes a side-by-side comparison of base vs. fine-tuned model responses.

---

## System Requirements

| Requirement | Details |
|---|---|
| Hardware | Apple Silicon (M1/M2/M3) for MLX, or CUDA GPU |
| Base Models | Llama 3 (8B), Mistral 7B (via Ollama or local weights) |
| Framework | MLX (Apple) or Hugging Face PEFT |
| Storage | 8–20 GB free disk for model weights + checkpoints |

---

## Tab Structure

```
Tab 1: 📚 Dataset Curation  →  Tab 2: 🔥 Fine-Tune  →  Tab 3: 🆚 Compare  →  Tab 4: 💾 Checkpoints
```

---

## Tab 1 — 📚 Dataset Curation

### Creating a Training Dataset

Fine-tuning requires instruction-response pairs in JSONL format:
```json
{"prompt": "Investigate this transaction: ...", "completion": "The transaction is suspicious because..."}
```

**Auto-generation from uploaded notes:**
1. Select documents from the **Source Files** multi-select (investigation reports, case notes, PDFs).
2. Set the **number of examples** to generate.
3. Click **▶ Generate Training Examples** — the AI extracts question-answer pairs from the documents.

**Manual entry:**
- Use the **📝 Add Example** form to write prompt/completion pairs manually.
- Review and edit auto-generated examples in the table editor.

**Validation:**
- The dataset editor shows a row count and quality warning if fewer than 50 examples are present.
- Duplicate prompt detection highlights redundant rows.

**Export:**
- Click **💾 Export JSONL** to download the curated dataset.
- The dataset is automatically saved as a versioned dataset in the Model Registry.

---

## Tab 2 — 🔥 Fine-Tune

### Configuration

| Parameter | Description |
|---|---|
| **Base Model** | Llama 3 8B / Mistral 7B |
| **Method** | LoRA (low-rank adaptation) or QLoRA (quantized) |
| **Rank (r)** | LoRA rank — higher = more parameters (4–64) |
| **Alpha** | LoRA scaling factor (typically 2× rank) |
| **Epochs** | Training passes over the dataset (1–10) |
| **Learning Rate** | Step size (default: 2e-4) |
| **Batch Size** | Samples per gradient update |

### Starting Training

1. Select your **Dataset Version** from the dropdown.
2. Configure parameters.
3. Click **▶ Start Fine-Tuning**.
4. A **live training loss chart** updates every epoch.
5. Training completes when all epochs are done — a 🎉 success message is shown.

> **Note:** Training a 7B model for 3 epochs on 200 examples takes approximately 15–30 minutes on M2 Pro hardware.

---

## Tab 3 — 🆚 Side-by-Side Comparison

Compare the base model vs. fine-tuned model on your domain-specific prompts.

**How to use:**
1. Select the **base model** and **fine-tuned checkpoint** from the dropdowns.
2. Enter a test prompt (e.g., *"Analyze this transaction for fraud indicators: ..."*).
3. Click **▶ Compare** — both responses appear side-by-side.

**Evaluation dimensions shown:**
- Response quality (AI-judged score)
- Domain relevance (use of fraud-specific terminology)
- Response length

---

## Tab 4 — 💾 Checkpoint Management

Lists all saved model checkpoints with:
- Version name and creation timestamp
- Number of training examples and epochs
- Source dataset version
- **Load** / **Delete** actions

To share a checkpoint with another user, use the **📤 Export Checkpoint** button to download the LoRA adapter weights (`.safetensors` file).

---

## Tips

- Start with a small dataset (50–100 examples) to verify the training loop works before scaling up.
- QLoRA is recommended for machines with less than 32 GB RAM as it uses 4-bit quantization.
- Use the **Comparison** tab after every fine-tuning run to verify improvement before deploying.
- Fine-tuned model adapters don't replace the base model — they are lightweight additions (~100 MB).
