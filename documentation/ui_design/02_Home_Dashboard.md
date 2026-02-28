# 🏠 Home Dashboard — UI Design Specification

**Page:** `app.py`  
**Layout:** Wide (no sidebar page padding override)  
**Theme:** Dark Glassmorphism

---

## Page Layout Overview

```
┌──────────────────────────────────────────────────────────────────┐
│ [Hero Banner — full width]                                        │
├──────────────────────────────────────────────────────────────────┤
│ [Guest CTA banner — full width, conditional]                      │
├──────────────────────────────────────────────────────────────────┤
│   📊 stat │ 📊 stat │ 📊 stat │ 📊 stat │ 📊 stat │ 📊 stat    │  ← 6-col metrics
├───────────────────────────────────┬──────────────────────────────┤
│  LEFT COLUMN (module cards grid)  │  RIGHT COLUMN (chat + guide) │
│  3-up card grid (3 cols)          │  💬 Sentinel Operator Chat   │
│  [Module Card] [Card] [Card]      │  [Chat messages container]   │
│  [Module Card] [Card] [Card]      │  [st.chat_input at bottom]   │
│  [Admin Console Card] (admin)     │  [Clear Chat button]         │
│                                   ├──────────────────────────────┤
│                                   │  🚀 Quick-Start Guide        │
│                                   │  [Numbered step expander]    │
│                                   ├──────────────────────────────┤
│                                   │  🗺️ Architecture Table       │
└───────────────────────────────────┴──────────────────────────────┘
```

---

## Hero Banner

| Property | Spec |
|---|---|
| **Container** | Full-width `<div>` with `text-align: center` |
| **Background** | `linear-gradient(135deg, #1a0000 0%, #0d0d0d 60%, #001a00 100%)` |
| **Border** | `1px solid rgba(255,75,75,0.3)`, `border-radius: 20px` |
| **Padding** | `3rem` |
| **Main heading** | `🛡️ Sentinel Pro` — white, large |
| **Tagline** | `"AI-Powered Fraud Investigation..."` — `#f0f0f0`, `1.3rem` |
| **Badge pills** | `[🔬 Multi-Agent RAG]` `[🕸 Graph Intelligence]` `[🧠 LLM Fine-Tuning]` — inline HTML spans, red/green |

---

## Guest CTA Banner *(conditional — not logged in)*

| Property | Spec |
|---|---|
| **Visibility** | Only when `st.session_state.user` is None |
| **Background** | `linear-gradient(135deg, #003300 0%, #0d0d0d 100%)` |
| **Border** | `2px solid #22a44e`, `border-radius: 16px` |
| **Icon + heading** | `⚡ Get Started in 30 Seconds` — white |
| **Body text** | Instructions for Quick Install — `#c0ffc0` |
| **CTA highlight** | `⚡ Quick Install Demo Data` — bold green inline |

---

## Stats Bar

6 equal columns using `st.columns(6)`:

| Metric | Icon | Source |
|---|---|---|
| SQL Tables | 🗄️ | Live `COUNT(*)` on SQLite `sqlite_master` |
| Uploaded Files | 📄 | `os.listdir(settings.uploads_dir)` count |
| Registered Users | 👥 | Live `COUNT(*)` on `users` table |
| Demo Data | ⚡ | `is_demo_already_installed()` → `✅ Installed` / `⏳ Pending` |
| Email Mode | 📧 | `settings.smtp_server` → `SMTP ✅` or `Mock 📋` |
| Auth | 🔒 | Hardcoded `JWT + BCrypt` |

Each metric rendered with `st.metric(label, value)`.

---

## Main Content Columns

Split: `st.columns([3, 2])` — module grid left, operator panel right.

---

## Module Cards Grid (Left Column)

3-column grid: `st.columns(3)` for each row of cards.

### Card Design
```css
background: rgba(255, 255, 255, 0.05);
border: 1px solid rgba(255, 75, 75, 0.3);
border-radius: 16px;
padding: 1.5rem;
backdrop-filter: blur(10px);
transition: transform 0.2s ease, box-shadow 0.2s ease;
cursor: pointer;
/* Hover */
transform: translateY(-2px);
box-shadow: 0 8px 32px rgba(255, 75, 75, 0.2);
```

### Card Anatomy
```
┌─────────────────────┐
│  🧠  [Large emoji]  │
│  Module Name        │  ← bold, white
│  Short description  │  ← muted text, 0.9rem
│  ─────────────────  │
│  → Open [Module]    │  ← st.page_link styled as link
│  👁 Preview ▾       │  ← st.popover showing feature list
└─────────────────────┘
```

### Module Card Inventory (rows × 3)

**Row 1:**
- 📁 Data Hub
- 🧠 SQL RAG Assistant  
- 🕸️ Graph RAG Assistant

**Row 2:**
- 🎥 Multimodal RAG
- 📈 Trends & Insights
- 🔄 ML Workflow

**Row 3 (conditional):**
- 🧬 LLM Fine-Tuning Forge
- 🔌 API Integration Hub
- 🛡️ Admin Console *(admin only — spans 3 cols or 1 of 3)*

---

## Right Column — Operator Chat + Guide

### 💬 Sentinel Operator Chat

| Element | Spec |
|---|---|
| Header | `st.subheader("💬 Sentinel Operator Chat")` |
| Message history | `st.chat_message("user")` / `st.chat_message("assistant")` |
| Chat area height | CSS-constrained scrollable container (max ~400px) |
| Input | `st.chat_input("Ask me anything about the platform...")` — sticks to bottom |
| Clear button | `st.button("🗑 Clear Chat")` — secondary style, top-right of section |
| AI agent | `AppGuideAgent` streaming response |

### 🚀 Quick-Start Guide

Rendered as `st.expander("🚀 Quick-Start Guide — Steps 0–7")`:

| Step | Label | Icon |
|---|---|---|
| 0 | Quick Install (first-time) | ⚡ |
| 1 | Load data via Data Hub | 📁 |
| 2 | Query SQL in natural language | 🧠 |
| 3 | Explore fraud network (Graph RAG) | 🕸️ |
| 4 | Visualise and evaluate graph | 🔬 |
| 5 | Train a fraud classifier | 🔄 |
| 6 | Chat with multimodal evidence | 🎥 |
| 7 | Admin Configuration | 🛡️ |

### 🗺️ Architecture Table

`st.table()` or markdown table inside the right column:

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI + Uvicorn |
| SQL | SQLite |
| Graph | Neo4j |
| Vector KB | FAISS + HuggingFace |
| LLM Engine | Ollama · OpenAI · Anthropic · Google |
| Auth | JWT · BCrypt · RBAC |
| Onboarding | Demo Installer |
| Email | SMTP / Mock |
| Container | Docker Compose |

---

## Interaction States

| Trigger | UI Response |
|---|---|
| Hover module card | `translateY(-2px)` + red glow shadow |
| Chat submit | Spinner in chat area, assistant reply streams in |
| Stats bar load | Spinner until all DB queries complete |
| Guest banner visible | Green pulsing border on Quick Install mention |
