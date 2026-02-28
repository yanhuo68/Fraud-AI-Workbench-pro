# 🎥 Multimodal RAG Assistant — UI Design Specification

**Page:** `pages/4_🎥_Multimodal_RAG_Assistant.py (wrapper for src/views/multimodal_rag/)`  
**Layout:** Wide  
**Theme:** Dark Glassmorphism

---

## Page Layout Overview

```
┌────────────────────┬─────────────────────────────────────────────┐
│   SIDEBAR EXTRAS   │  🎥 Multimodal RAG Assistant  [st.title]   │
│                    │  "Chat with evidence files..." [st.caption] │
│  [File selector ▾] ├──────────────────────────────┬──────────────┤
│  (multi-select)    │                              │              │
│  [LLM ▾]           │  [Chat message history]      │ [File        │
│  [Max chunks ─●─]  │                              │  Preview     │
│  [💡 Suggest Qs]   │  ┌────────────────────────┐  │  Panel]      │
│                    │  │ 👤 "What is in PDF?"   │  │              │
│  ── Suggestions ── │  │ 🤖 "The document       │  │  [Image /    │
│  • Suggested Q 1   │  │    shows..."           │  │   PDF viewer │
│  • Suggested Q 2   │  │ [Source citations]     │  │   / audio    │
│  • Suggested Q 3   │  └────────────────────────┘  │   player]    │
│                    │                              │              │
│                    ├──────────────────────────────┴──────────────┤
│                    │  [st.chat_input "Ask about your evidence..."]│
└────────────────────┴─────────────────────────────────────────────┘
```

---

## Sidebar Controls

| Element | Spec |
|---|---|
| File selector | `st.multiselect("Evidence Files", indexed_files)` — multi-select |
| LLM dropdown | `st.selectbox("LLM", available_llms)` |
| Max chunks slider | `st.slider("Context Chunks", 1, 10, 4)` |
| Suggest button | `st.button("💡 Suggest Questions")` |
| Suggestion pills | 3–5 `st.button(q)` — click pre-fills chat input |

### File Selector Design
- Shows filename with extension icon prefix
- Multi-select allows combining multiple files as context
- Badge counter: `"3 files selected"`

---

## Chat Message Area

### User Message
```
┌─────────────────────────────────────────────┐
│  👤  "Does the receipt image match the       │
│       transaction in our CSV?"               │
└─────────────────────────────────────────────┘
```

### Assistant Message
```
┌─────────────────────────────────────────────┐
│  🤖  Based on the uploaded receipt (receipt │
│       _scan.jpg), the merchant name is      │
│       "TechMart" and the amount shown is    │
│       $1,247.99...                          │
│                                             │
│  📎 Sources:                                │
│    • receipt_scan.jpg [chunk 1]            │
│    • transactions.csv [row 42]             │
└─────────────────────────────────────────────┘
```

| Element | Spec |
|---|---|
| User message | `st.chat_message("user")` |
| Assistant message | `st.chat_message("assistant")` |
| Source citations | `st.caption("📎 Sources: ...")` below answer |
| Confidence note | `st.caption("⚠️ Verify with original files")` when uncertain |

---

## File Preview Panel (Right Column)

Renders a preview of the selected file(s):

| File Type | Preview Widget |
|---|---|
| Image (PNG/JPG) | `st.image(file, use_column_width=True)` |
| PDF | Embedded PDF viewer via `<iframe>` or page-by-page `st.image()` |
| Audio (MP3/WAV) | `st.audio(file)` — built-in HTML5 player |
| Video (MP4) | `st.video(file)` — built-in HTML5 player |
| Text/Markdown | `st.text_area(content, height=300, disabled=True)` |

```
┌─────────────────────────┐
│  📄 receipt_scan.jpg    │
│  ─────────────────────  │
│  [Image thumbnail]      │
│  640 × 480 · JPEG       │
│                         │
│  📄 invoice_audio.mp3   │
│  ─────────────────────  │
│  [▶ Audio player]       │
│  Duration: 3:42         │
└─────────────────────────┘
```

---

## Language Detection Indicator

When a non-English question is detected:
```
st.info("🌐 Responding in French (detected from question)")
```

---

## Hallucination Guard Indicators

| State | Display |
|---|---|
| High confidence | No indicator |
| Medium confidence | `st.caption("⚠️ Partially supported by source material")` |
| Not found in files | `st.warning("ℹ️ This information was not found in the selected files.")` |

---

## Colour Reference

| Element | Colour |
|---|---|
| File preview border | `rgba(255,255,255,0.1)` subtle |
| Audio/video player | Streamlit default (slate) |
| Source citation text | `#a0a0a0` muted |
| Uncertainty warning | `#f39c12` amber |
| Language detection info | `#3498db` blue |
