# 🧬 LLM Fine-Tuning Forge — UI Design Specification

**Page:** `pages/9_🧠_LLM_Fine_Tuning.py (wrapper for src/views/llm_fine_tuning/)`  
**Layout:** Wide  
**Theme:** Dark Glassmorphism

---

## Page Layout Overview

```
┌──────────────────────────────────────────────────────────────────┐
│  🧠 LLM Fine-Tuning Forge                        [st.title]     │
│  "Fine-tune open-source models on fraud data..." [st.caption]   │
├──────────────────────────────────────────────────────────────────┤
│  [ 📚 Dataset ] [ 🔥 Fine-Tune ] [ 🆚 Compare ] [ 💾 Checkpoints] │  ← 4 tabs
├──────────────────────────────────────────────────────────────────┤
│  [Tab content area]                                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## Tab 1 — 📚 Dataset Curation

```
┌────────────────────────┬─────────────────────────────────────────┐
│  Source Files          │  📝 Generated Examples                  │
│  [multi-select ▾]      │  ────────────────────────────────────── │
│                        │  [Editable JSONL table]                 │
│  # Examples: [─●─] 50  │  Row │ Prompt             │ Completion  │
│                        │  1   │ "Investigate..."   │ "Based..."  │
│  [▶ Generate Examples] │  2   │ ...                │ ...         │
│  [primary full-width]  │                                         │
│                        │  Row count: 50 ✅                       │
│  ── Manual Entry ──    │  Duplicates: 0                         │
│  Prompt: [text area]   │                                         │
│  Completion: [text]    │  [💾 Export JSONL]                      │
│  [📝 Add Example]      │  [📁 Save Dataset Version]             │
└────────────────────────┴─────────────────────────────────────────┘
```

| Element | Spec |
|---|---|
| Source file picker | `st.multiselect("Source Files", indexed_files)` |
| Example count slider | `st.slider("# Examples to Generate", 20, 500, 50)` |
| Generate button | `st.button("▶ Generate Training Examples", type="primary")` |
| Manual prompt | `st.text_area("Prompt", height=80)` |
| Manual completion | `st.text_area("Completion", height=80)` |
| Add button | `st.button("📝 Add Example")` |
| Dataset table | `st.data_editor(df)` — editable, full-width |
| Quality warning | `st.warning("⚠️ Dataset has < 50 examples. Quality may be limited.")` |
| Export button | `st.download_button("💾 Export JSONL", jsonl_bytes, "train.jsonl")` |

---

## Tab 2 — 🔥 Fine-Tune

```
┌──────────────────────┬─────────────────────────────────────────┐
│  Configuration       │  Training Progress                      │
│  ─────────────────── │  ─────────────────────────────────────  │
│  Base Model ▾        │  [▶ Start Fine-Tuning]  [full-width]   │
│  ○ Llama 3 8B        │                                         │
│  ● Mistral 7B        │  Epoch 2/5 · loss: 1.247               │
│                      │  [██████░░░░░░░░░░░░] 40%               │
│  Method ▾            │                                         │
│  ● LoRA  ○ QLoRA     │  [Live training loss chart]            │
│                      │  loss                                   │
│  Rank (r): [─●─] 16  │  2.1 │ ╲                               │
│  Alpha: [─●──] 32    │  1.0 │  ╲____                          │
│  Epochs: [●─] 3      │  0.5 │       ────                      │
│  LR: 0.0002          │      └──────────── epoch               │
│  Batch: [─●─] 4      │                                         │
│                      │  🎉 Training complete! (on success)     │
│  Dataset Version ▾   │                                         │
└──────────────────────┴─────────────────────────────────────────┘
```

| Element | Spec |
|---|---|
| Base model radio | `st.radio("Base Model", ["Llama 3 8B", "Mistral 7B"])` |
| Method radio | `st.radio("Method", ["LoRA", "QLoRA"], horizontal=True)` |
| Rank slider | `st.slider("Rank (r)", 4, 64, 16)` |
| Alpha slider | `st.slider("Alpha", 8, 128, 32)` |
| Epochs slider | `st.slider("Epochs", 1, 10, 3)` |
| LR input | `st.number_input("Learning Rate", value=2e-4, format="%.5f")` |
| Batch size | `st.slider("Batch Size", 1, 16, 4)` |
| Start button | `st.button("▶ Start Fine-Tuning", type="primary", use_container_width=True)` |
| Loss chart | `st.line_chart(loss_history)` — live updating |
| Success | `st.balloons()` + `st.success("🎉 Fine-tuning complete!")` |

---

## Tab 3 — 🆚 Compare

```
┌──────────────────────────────────────────────────────────────────┐
│  Base Model ▾         Fine-Tuned Checkpoint ▾                    │
│  Mistral 7B           mistral_fraud_v2                           │
├────────────────────────────────┬────────────────────────────────┤
│  Base Model Response           │  Fine-Tuned Response           │
│  ─────────────────────────     │  ─────────────────────────     │
│  "I don't have specific        │  "Based on the transaction     │
│   information about fraud      │   pattern, this exhibits       │
│   detection methods..."        │   card-not-present fraud       │
│                                │   characteristics: multiple    │
│                                │   small amounts in 24h,        │
│                                │   different merchant cats..."  │
├────────────────────────────────┴────────────────────────────────┤
│  Test Prompt: [text area — full width]                           │
│  [▶ Compare]  [primary button]                                   │
├──────────────────────────────────────────────────────────────────┤
│  Evaluation: Quality [★★★★☆]  Domain [★★★★★]  Length [longer]  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Tab 4 — 💾 Checkpoint Management

```
┌──────────────────────────────────────────────────────────────────┐
│  📋 Saved Checkpoints                                            │
│  ─────────────────────────────────────────────────────────────  │
│  Name               │ Created     │ Examples │ Epochs │ Actions │
│  mistral_fraud_v1   │ 2026-02-10  │ 200      │ 3      │ Load 🗑  │
│  mistral_fraud_v2   │ 2026-02-18  │ 350      │ 5      │ Load 🗑  │
│  llama3_custom_v1   │ 2026-02-20  │ 100      │ 3      │ Load 🗑  │
│                                                                  │
│  [📤 Export Checkpoint]  →  downloads `.safetensors` file       │
└──────────────────────────────────────────────────────────────────┘
```

| Element | Spec |
|---|---|
| Table | `st.dataframe(checkpoints_df, use_container_width=True)` |
| Load button | Inline `st.button("Load")` per row |
| Delete button | Inline `st.button("🗑")` per row — red confirm dialog |
| Export button | `st.download_button("📤 Export .safetensors", ...)` |

---

## Colour Summary

| Element | Colour |
|---|---|
| Loss curve | `#ff4b4b` red (decreasing) |
| Training progress bar | `#2ecc71` green fill |
| LoRA active highlight | `#61affe` blue |
| Check comparison left | Neutral dark surface |
| Check comparison right | `rgba(34,164,78,0.08)` subtle green tint |
