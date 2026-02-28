# 🎨 Sentinel Pro — UI Design Documentation Index

**Application:** Fraud Investigation Workbench Pro  
**Design Theme:** Dark Glassmorphism · Premium AI Workbench  
**Last Updated:** 2026-02-22

---

## Quick Navigation

| File | Component / Page | Access |
|---|---|---|
| [00_Design_System.md](./00_Design_System.md) | 🎨 Global Design System (palette, typography, tokens) | Reference |
| [01_Sidebar.md](./01_Sidebar.md) | 🗂️ Sidebar (global component) | All users |
| [02_Home_Dashboard.md](./02_Home_Dashboard.md) | 🏠 Home / Dashboard | All users |
| [03_Data_Hub.md](./03_Data_Hub.md) | 📁 Data Hub | Authenticated |
| [04_SQL_RAG_Assistant.md](./04_SQL_RAG_Assistant.md) | 🧠 SQL RAG Assistant | Authenticated |
| [05_Graph_RAG_Assistant.md](./05_Graph_RAG_Assistant.md) | 🕸️ Graph RAG Assistant | Authenticated |
| [06_Multimodal_RAG_Assistant.md](./06_Multimodal_RAG_Assistant.md) | 🎥 Multimodal RAG Assistant | Authenticated |
| [07_Trends_and_Insights.md](./07_Trends_and_Insights.md) | 📈 Trends & Insights | Authenticated |
| [08_ML_Workflow.md](./08_ML_Workflow.md) | 🔄 ML Workflow | data_scientist / admin |
| [09_LLM_Fine_Tuning.md](./09_LLM_Fine_Tuning.md) | 🧬 LLM Fine-Tuning Forge | data_scientist / admin |
| [10_API_Integration_Hub.md](./10_API_Integration_Hub.md) | 🔌 API Integration Hub | Authenticated |
| [11_Admin_Console.md](./11_Admin_Console.md) | 🛡️ Admin Console | admin only |

---

## Design System Summary

### Colour Palette

| Token | Hex | Usage |
|---|---|---|
| Background | `#0d0d0d` | Page root |
| Surface gradient | `#1a1a1a → #0d0d0d` | Radial gradient |
| Sidebar | `rgba(15,15,15,0.95)` | Glassmorphism panel |
| Brand Red | `#ff4b4b` | Logo, borders, accents |
| Success Green | `#22a44e → #2ecc71` | CTA, success states |
| Warning Orange | `#f39c12` | Auth badges, warnings |
| Error Red | `#e74c3c` | Errors, delete actions |
| Text Primary | `#e0e0e0` | Body text |
| Text Muted | `#a0a0a0` | Captions, secondary |
| Glass Card | `rgba(255,255,255,0.05)` | Card surfaces |

### Component Method Badges (API Hub)
| Method | Colour |
|---|---|
| POST | `#49cc90` green |
| GET | `#61affe` blue |
| PATCH | `#50e3c2` teal |
| DELETE | `#f93e3e` red |

---

## Common UI Patterns

### Glassmorphism Card
```css
background: rgba(255, 255, 255, 0.05);
border: 1px solid rgba(255, 75, 75, 0.3);
border-radius: 16px;
padding: 1.5rem;
backdrop-filter: blur(10px);
```

### Page Structure (all pages)
1. `st.title()` — emoji + page name
2. `st.caption()` — one-line description
3. **Main content** — tabbed or single-column layout
4. Auto-injected sidebar via `render_global_sidebar()`

### Tab Pattern
All multi-function pages use `st.tabs([...])` for primary navigation:
- Each tab = distinct functional module
- Inner sub-tabs used sparingly (Admin Console, API Hub, LLM Fine-Tuning only)

### Form Pattern
All forms use `st.form()` with `st.form_submit_button()` — prevents stale state on re-renders.

### Response / Feedback Pattern
```
st.spinner(...)      ← during request
st.success(...)      ← on success
st.error(...)        ← on failure
st.warning(...)      ← on partial / auth issue
st.info(...)         ← informational
```

---

## Animation & Interaction Summary

| Interaction | Animation |
|---|---|
| Logo hover | `scale(1.05)` + glow intensify |
| Module card hover | `translateY(-2px)` + `box-shadow` glow |
| Green CTA hover | Gradient shift + stronger shadow pulse |
| Training success | `st.balloons()` confetti |
| Demo install success | `st.balloons()` confetti |
| Spinner | Streamlit default (`st.spinner()`) |
| Toast notifications | `st.toast()` bottom-right |

---

## File Cross-Reference

| Source File | Design Doc |
|---|---|
| `app.py` | [02_Home_Dashboard.md](./02_Home_Dashboard.md) |
| `components/sidebar.py` | [01_Sidebar.md](./01_Sidebar.md) |
| `pages/1_��_Data_Hub.py (wrapper for src/views/data_hub/)` | [03_Data_Hub.md](./03_Data_Hub.md) |
| `pages/2_🧠_SQL_RAG_Assistant.py` | [04_SQL_RAG_Assistant.md](./04_SQL_RAG_Assistant.md) |
| `pages/3_🕸️_Graph_RAG_Assistant.py` | [05_Graph_RAG_Assistant.md](./05_Graph_RAG_Assistant.md) |
| `pages/4_🎥_Multimodal_RAG_Assistant.py (wrapper for src/views/multimodal_rag/)` | [06_Multimodal_RAG_Assistant.md](./06_Multimodal_RAG_Assistant.md) |
| `pages/5_📈_Trends_and_Insights.py (wrapper for src/views/trends_insights/)` | [07_Trends_and_Insights.md](./07_Trends_and_Insights.md) |
| `pages/6_🔄_ML_Workflow.py (wrapper for src/views/ml_workflow/)` | [08_ML_Workflow.md](./08_ML_Workflow.md) |
| `pages/9_🧠_LLM_Fine_Tuning.py (wrapper for src/views/llm_fine_tuning/)` | [09_LLM_Fine_Tuning.md](./09_LLM_Fine_Tuning.md) |
| `pages/10_🔌_API_Interaction.py (wrapper for src/views/api_interaction/)` | [10_API_Integration_Hub.md](./10_API_Integration_Hub.md) |
| `pages/11_🛡️_Admin_Console.py (wrapper for src/views/admin_console/)` | [11_Admin_Console.md](./11_Admin_Console.md) |
