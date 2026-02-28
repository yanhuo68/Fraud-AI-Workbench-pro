# 🗂️ Sidebar — UI Design Specification

**Component:** `components/sidebar.py`  
**Width:** Streamlit default (`21rem`)  
**Theme:** Dark Glassmorphism

---

## Layout Structure

```
┌─────────────────────────────────────┐
│ [Logo 60px] │ SENTINEL (red h1)      │  ← Branding row (2-col)
│             │ Fraud Detection AI...  │
├─────────────────────────────────────┤
│              ── divider ──           │
├─────────────────────────────────────┤
│ 👤 User Session                      │  ← Section header
│                                      │
│  [GUEST]                             │
│  ⚠️ Not Logged In (warning)          │
│  ┌──────────────────────────────┐   │
│  │ Login │ Register │ Forgot Pw │   │  ← Horizontal radio tabs
│  └──────────────────────────────┘   │
│  [Active form below radio]           │
│                                      │
│  [LOGGED IN]                         │
│  Logged in as: username (bold)       │
│  🎭 Role: admin (caption)            │
│  [🚪 Logout] full-width button       │
│  🛡️ Admin Session Active (caption)  │
│  🔧 Debug: Role=X, Perms=N          │
├─────────────────────────────────────┤
│              ── divider ──           │
├─────────────────────────────────────┤
│ ⚙️ Global Configuration              │  ← Section header
│  ▶ 🔑 API Keys [expander]           │
│  [LLM dropdown] [🔄 scan btn]       │
│  Active Model: model_name (caption)  │
├─────────────────────────────────────┤
│              ── divider ──           │
├─────────────────────────────────────┤
│ 🔔 Task Notification Hub            │  ← Section header
│  [Task cards or "No active tasks"]  │
├─────────────────────────────────────┤
│              ── divider ──           │
├─────────────────────────────────────┤
│ 🚀 Navigation                        │  ← Section header
│  🏠 Home                             │  ← page_link items
│  📁 Data Hub                         │
│  🧠 SQL RAG                          │
│  🕸️ Graph RAG                        │
│  🎥 Multimodal RAG                   │
│  📈 Trends                           │
│  🔄 ML Workflow                      │
│  🧠 LLM Fine Tuning                  │
│  🔌 API Hub                          │
│  🛡️ Admin Console                    │
│              ── divider ──           │
│  ✨ First time? Set up instantly!    │  ← Only when guest
│  [⚡ Quick Install Demo Data] green  │
└─────────────────────────────────────┘
```

---

## Branding Row

| Property | Value |
|---|---|
| **Layout** | 2 columns (`[1, 4]` ratio) |
| **Logo** | `data/assets/logo.png`, width `60px` |
| **Logo effect** | `drop-shadow(0 0 12px rgba(255,75,75,0.5))`, `border-radius: 10px` |
| **Logo hover** | `scale(1.05)` + stronger glow |
| **Title** | `<h1>SENTINEL</h1>` — `color: #ff4b4b`, `margin-bottom: 0` |
| **Subtitle** | `st.caption("Fraud Detection AI Workbench")` |

---

## User Session Panel

### Not Logged-In State

| Element | Spec |
|---|---|
| Warning banner | `st.warning("⚠️ Not Logged In")` — amber Streamlit warning box |
| Mode selector | `st.radio(horizontal=True)` with options: Login / Register / Forgot Password |
| Form container | `st.form()` — renders below radio based on selection |

**Login form fields:**
- `Username` — text input
- `Password` — password input (masked)
- Submit: `Login` — full-width button

**Register form fields:**
- `New Username` — text input
- `Email Address` — text input
- `New Password` — password input
- Submit: `Register` — full-width button

**Forgot Password form:**
- `Email Address` — text input
- Submit: `Send Reset Link` — full-width button
- Feedback: success (`st.success`) or error (`st.error`)

**Reset Password Mode** *(URL-triggered only)*:
- Warning: `st.warning("🔐 Reset Password Mode")`
- `New Password` — password input
- `Confirm Password` — password input
- Submit: `Reset Password`
- Link: `Cancel Reset` button

### Logged-In State

| Element | Spec |
|---|---|
| Username line | `st.markdown("**Logged in as:** username")` |
| Role badge | `st.caption("🎭 Role: {role}")` |
| Logout button | Full-width `st.button("🚪 Logout")` |
| Admin caption | `st.caption("🛡️ Admin Session Active")` — only for admin role |
| Debug caption | `st.caption("🔧 Debug: Role=X, Perms=N")` — always when logged in |
| Auth error | `st.error(...)` — only when `auth_error` is in session state |

---

## Global Configuration Panel

### API Keys Expander

- Render: `st.expander("🔑 API Keys", expanded=False)`
- Contains 4 `st.text_input(..., type="password")` fields:
  - OpenAI API Key
  - DeepSeek API Key
  - Google API Key
  - Anthropic API Key
- Caption: `"Notice: Local session-based overrides."`

### LLM Selector Row

| Element | Spec |
|---|---|
| Layout | 2 columns `[4, 1]` |
| Dropdown | `st.selectbox("Select Active LLM", available_llms)` — defaults to `openai:gpt-4o-mini` |
| Refresh button | `st.button("🔄")` icon-only, tooltip: `"Scan for local LLMs (Ollama/LM Studio)"` |
| Active model | `st.caption(f"Active Model: **{selected_llm}**")` below the row |

---

## Task Notification Hub

- Header: `st.subheader("🔔 Task Notification Hub")`
- Empty state: `st.info("No active background tasks.")`
- Per task: `st.expander(f"{emoji} {task_name}", expanded=True)`
  - Running: progress bar + `"Status: ⏳ In Progress..."`
  - Completed: `st.success(result)` + `Dismiss` button
  - Failed: `st.error(error)` + `Dismiss` button

---

## Navigation Links

- Header: `st.subheader("🚀 Navigation")`
- Per permitted page: `st.page_link(path, label=label)`
- Hidden links: pages not in the user's permissions are silently omitted (no disabled state shown)
- Default Streamlit nav (`stSidebarNav`) is **hidden** via CSS injection:

```css
[data-testid="stSidebarNav"] { display: none; }
```

---

## Quick Install CTA (Guest-Only)

| Property | Value |
|---|---|
| Visibility | Only when not logged in AND demo enabled AND not yet installed |
| Label text | `"✨ First time? Set up instantly!"` |
| Font | `0.82rem`, `#22a44e`, `font-weight: 600`, centred |
| Button label | `"⚡ Quick Install Demo Data"` |
| Button style | Green gradient (see Design System) |
| On click | Redirects to `app.py` with `_trigger_demo_install_home = True` |

---

## Global Sidebar CSS Summary

```css
/* Panel */
[data-testid="stSidebar"] {
  background-color: rgba(15, 15, 15, 0.95);
  backdrop-filter: blur(15px);
  border-right: 1px solid rgba(255, 75, 75, 0.2);
}

/* All text white */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label { color: #ffffff !important; }

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #ffffff !important; }
```
