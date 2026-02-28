# 🗂️ Sidebar — User Manual

**Component:** Global Sidebar (`components/sidebar.py`)  
**Visible on:** Every page of the application  
**Behaviour:** Content changes depending on your login state and role

---

## Overview

The **Sentinel sidebar** is the always-visible navigation and configuration panel on the left side of every page. It provides:

- Branding and platform identity
- User session management (login / register / logout)
- Password reset and forgot-password flows
- One-click demo data installation (for new users)
- Global LLM selection (applies to all RAG modules)
- Session-scoped API key overrides
- Background task notifications
- Role-filtered navigation links

---

## Sidebar States

The sidebar renders differently depending on whether you are logged in:

```
┌─────────────────────────────┐
│ 🛡️ SENTINEL                 │
│ Fraud Detection AI Workbench│
├─────────────────────────────┤
│ [GUEST STATE]               │  ← not logged in
│   🔒 Login / Register /     │
│      Forgot Password tabs   │
│   ⚡ Quick Install Demo Data │
├─────────────────────────────┤
│ [AUTH STATE]                │  ← logged in
│   Logged in as: username    │
│   Role: guest / data_sci /  │
│         admin               │
│   🚪 Logout                  │
└─────────────────────────────┘
│ ⚙️ Global Configuration      │
│   🔑 API Key overrides       │
│   Select Active LLM         │
├─────────────────────────────┤
│ 🔔 Task Notification Hub    │
├─────────────────────────────┤
│ 🚀 Navigation               │
│   (role-filtered page links)│
└─────────────────────────────┘
```

---

## Section 1 — Branding

At the very top of the sidebar:
- **Logo** — the Sentinel shield icon with red glow effect
- **SENTINEL** — platform name in red
- **Fraud Detection AI Workbench** — edition subtitle

The logo has a hover animation (subtle scale + glow intensification).

---

## Section 2 — 👤 User Session

This section changes based on your login state.

---

### 2a — When Not Logged In

Three authentication modes are available via a horizontal radio selector:

#### 🔐 Login
| Field | Description |
|---|---|
| **Username** | Your Sentinel account username |
| **Password** | Your account password |

Click **Login** to authenticate. On success:
- Your username and role are displayed in the sidebar
- All page navigation links allowed for your role become visible
- You remain on the current page (no forced redirect for the sidebar login)

#### 📝 Register
| Field | Required | Notes |
|---|---|---|
| **New Username** | ✅ | Must be unique across all users |
| **Email Address** | ✅ | Used for password reset |
| **New Password** | ✅ | Minimum 6 characters |

New accounts are always created with the **guest** role. Contact an admin to upgrade your access level.

After registration, switch to the **Login** tab to sign in.

#### 🔑 Forgot Password
1. Select **Forgot Password** from the radio tabs.
2. Enter your registered **email address**.
3. Click **Send Reset Link**.
4. A reset link is sent to your email (if SMTP is configured) or logged to the server console (mock mode).
5. Click the link in the email — you will be redirected to the platform with a `?reset_token=...` URL parameter.
6. The sidebar automatically enters **Reset Password Mode** when a reset token is detected in the URL.

#### 🔑 Reset Password Mode *(URL-triggered)*

This mode activates automatically when you open a password reset link from your email.

| Field | Notes |
|---|---|
| **New Password** | Minimum 8 characters |
| **Confirm Password** | Must match |

Click **Reset Password** to save. After success, you are redirected to the login form.  
Click **Cancel Reset** to dismiss without changing your password.

---

### 2b — When Logged In

Displays:
- **"Logged in as: `{username}`"**
- **"Role: `{role}`"** — your current access level

**🚪 Logout** button:
- Clears your session token and user data
- Clears any pending URL query parameters (e.g. reset tokens)
- Returns you to the not-logged-in state
- The page refreshes automatically

**🛡️ Admin Session Active** — shown as a caption if your role is `admin`.

**🔧 Debug line** — shown when logged in: `Role=X, Perms=N` displays your current role and number of permitted pages. This is a diagnostic aid.

---

## Section 3 — ⚡ Quick Install Demo Data *(Guest users only)*

A green glowing button appears in the sidebar **only when:**
1. You are **not logged in**
2. The demo installer is enabled in Admin Console → Onboarding Settings
3. Demo data has **not** already been installed

**What the Quick Install does:**
1. Creates 3 demo user accounts (guest, data_scientist, admin)
2. Executes 5 SQL seed scripts with sample fraud transaction data
3. Uploads 2 fraud CSV datasets to the Data Hub
4. Marks the installation as complete

**Steps:**
1. Click **⚡ Quick Install Demo Data** in the sidebar.
2. You are redirected to the Home page where the installer runs.
3. A progress log shows each installation step in real time.
4. On success, 🎉 balloons animation plays and demo accounts are ready.

**Demo credentials after install:**

| Username | Password | Role |
|---|---|---|
| `yanhuo68` | `yanhuo68ottawa` | admin |
| `david@ontario` | `david2026` | data_scientist |
| `stephane@qubec` | `stephane2026` | guest |

After install, the green button disappears and does not reappear (unless reset by an admin).

---

## Section 4 — ⚙️ Global Configuration

*(Visible when logged in)*

### 🔑 API Keys (expandable)

Override the system-configured LLM API keys for the current browser session only. These are **session-scoped** — they are cleared on page reload and do not persist to the database.

| Key | Provider |
|---|---|
| OpenAI API Key | GPT-4o, GPT-4o-mini |
| DeepSeek API Key | DeepSeek Chat |
| Google API Key | Gemini 1.5 Pro / Flash |
| Anthropic API Key | Claude 3.5 Sonnet |

> **Note:** To persist API keys permanently, use **Admin Console → API Keys** instead.

---

### 🤖 Select Active LLM

A dropdown that sets the **global default LLM** used across all RAG modules (SQL RAG, Graph RAG, Multimodal RAG, Trends & Insights) that do not have their own LLM selector.

**Options include:**
- Cloud models: `openai:gpt-4o-mini`, `openai:gpt-4o`, `anthropic:claude-3-5-sonnet-20241022`, `google:gemini-1.5-pro`, `deepseek:deepseek-chat`
- Local models: `local_ollama:llama3`, `local_ollama:mistral`, and any other Ollama models pulled via Admin Console

**🔄 Refresh button** (next to the dropdown):  
Scans for locally-running Ollama / LM Studio models and adds them to the list.  
Use this after pulling a new model with **Admin Console → Local LLM Manager**.

**Active Model** caption below the dropdown confirms which model is currently active.

---

## Section 5 — 🔔 Task Notification Hub

Displays the status of background tasks running on the platform (e.g. LLM fine-tuning, large file ingestion).

| Task Status | Display |
|---|---|
| ⏳ In Progress | Progress bar with task name |
| ✅ Complete | Green success banner + **Dismiss** button |
| ❌ Failed | Red error banner + **Dismiss** button |

If no tasks are running: `"No active background tasks."` is shown.  
Click **Dismiss** on a completed or failed task to remove it from the list.

---

## Section 6 — 🚀 Navigation

A list of page links filtered by your current role's permissions. You only see links to pages you are authorized to access.

**Full navigation list** (shown to admin):

| Link | Page |
|---|---|
| 🏠 Home | Home Dashboard |
| 📁 Data Hub | Data Hub |
| 🧠 SQL RAG | SQL RAG Assistant |
| 🕸️ Graph RAG | Graph RAG Assistant |
| 🎥 Multimodal RAG | Multimodal RAG Assistant |
| 📈 Trends | Trends & Insights |
| 🔄 ML Workflow | ML Workflow |
| 🧠 LLM Fine Tuning | LLM Fine-Tuning Forge |
| 🔌 API Hub | API Integration Hub |
| 🛡️ Admin Console | Admin Console *(admin only)* |

Pages not in your permissions are **not displayed** — they are silently hidden, not shown as disabled.

> **Tip:** If a page you expect to see is missing, ask your admin to add it to your role's permissions via **Admin Console → Role Management**.

---

## Authentication Wall (Protected Pages)

When you navigate to a protected page without being logged in, the main content area is replaced with a full-screen **Authentication Required** overlay.

**Buttons in the auth wall:**

| Button | Action |
|---|---|
| 🏠 Back to Portal | Returns to the Home page |
| 🔐 Login | Opens an inline login form |
| 📝 Register | Opens an inline registration form |
| ⚡ Quick Install Demo Data | Starts the one-click demo installer *(guest-only, when enabled)* |

After a successful login via the auth wall, you are redirected to the **Home page** (not the blocked page). This prevents permission errors on refresh.

---

## Access Restricted Screen

If you are logged in but your role does not include the page you navigated to, an **Access Restricted** screen is shown instead of the page content:

```
🚫 Access Restricted
Your current identity (data_scientist) is not authorized for this page.
Please contact your Sentinel Administrator to request advanced Clearance levels.
[🏠 Back to Home]
```

---

## Tips

- **Switch LLM without reloading** — change the LLM dropdown in the sidebar to affect all subsequent RAG queries in the same session.
- **Session-only API keys** — if you need to test with a personal API key without changing system settings, enter it in the API Keys expander.
- **Forgot password without email** — in development/demo mode (Mock SMTP), the reset token is printed in the FastAPI container logs. Run `docker compose logs fastapi | grep reset_token` to find it.
- **Quick Install appears once** — after demo installation, the green button is hidden permanently. Reset it via **Admin Console → Onboarding Settings → Reset Install Status**.
