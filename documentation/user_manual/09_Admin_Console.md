# 🛡️ Admin Console — User Manual

**Page:** Admin Console (`pages/11_🛡️_Admin_Console.py (wrapper for src/views/admin_console/)`)  
**Access Level:** Admin Role Required

---

## Overview

The **Admin Console** is the central administration panel for the Sentinel platform. It provides full control over API keys, user management, role-based access control (RBAC), external credentials, local LLM management, system statistics, email configuration, and onboarding settings.

---

## Access Requirements

This page is only visible to users with the **admin** role. If you reach this page without admin rights, you will see a "Permission Denied" message.

**Default admin account (after demo install):**
- Username: `yanhuo68`
- Password: `yanhuo68ottawa`

---

## Tab Structure

```
🔑 API Keys  |  👥 Users  |  🎭 Roles  |  🔐 Credentials  |  🤖 LLMs  |  ⚙️ System  |  📧 SMTP  |  🚀 Onboarding
```

---

## Tab 1 — 🔑 API Keys

Manage LLM provider API keys used by the backend for cloud model access.

**Adding a key:**
1. Select a provider (OpenAI, Anthropic, Google, DeepSeek, etc.) from the dropdown.
2. Paste the API key into the text field.
3. Click **💾 Save Key**.

**Key storage:**  
Keys are stored encrypted in the SQLite database and passed to backend agents at runtime. They are never exposed in the UI after saving.

**Listing / revoking:**
- Active keys are listed with provider name, creation date, and masked value.
- Click **🗑 Revoke** next to any key to delete it.

---

## Tab 2 — 👥 User Management

Full CRUD interface for all registered user accounts.

### View Users
A table displays all users: ID, username, email, role, and registration date.

### Create User
Fill in:
- **Username** (unique)
- **Email** (optional — stored as NULL if blank)
- **Password** (minimum 8 characters)
- **Role**: `guest`, `data_scientist`, or `admin`

### Update User
For any existing user:

| Action | Form |
|---|---|
| Change role | Role dropdown + **Update Role** |
| Update email | Email input + **Update Email** |
| Update username | New username input + **Update Username** |
| Reset password | New password input + **Reset Password** |

### Delete User
Click **🗑 Delete** on any row. A confirmation prompt appears before deletion.

---

## Tab 3 — 🎭 Role Management

Configure **Role-Based Access Control (RBAC)** — which pages each role can access.

### Default Roles

| Role | Access Level |
|---|---|
| `guest` | Home page only |
| `data_scientist` | All analysis pages (no Admin Console) |
| `admin` | Full access to all pages |

### Custom Roles
1. Enter a **Role Name** (lowercase, no spaces).
2. Select **Pages** from the multi-select list of all available pages.
3. Click **💾 Save Role**.

### Editing Roles
Click on any existing role to edit its page access. Changes take effect immediately on next login for affected users.

### Deleting Roles
Click **🗑 Delete** next to any custom role. Built-in roles (`guest`, `data_scientist`, `admin`) cannot be deleted.

---

## Tab 4 — 🔐 External Credentials

Manage credentials for external data source connectors.

### Kaggle
- **Username**: Kaggle account username
- **API Key**: Kaggle API key (from `kaggle.com/account`)
- Click **Save Kaggle Credentials**

### GitHub
- **Personal Access Token**: GitHub PAT with `repo` scope
- Click **Save GitHub Token**

These credentials are used by the **Data Hub → External Connectors** tab.

---

## Tab 5 — 🤖 Local LLM Manager (Ollama)

Manage locally-running Ollama models.

### View Available Models
A table lists all currently pulled Ollama models with name, size, and modification date.

### Pull a New Model
1. Enter the model name (e.g. `llama3`, `mistral`, `qwen2.5`).
2. Click **⬇ Pull Model** — a progress spinner shows download status.
3. On completion, the model appears in the list and becomes selectable in all RAG assistants.

### Delete a Model
Click **🗑 Delete** next to any model to remove it from local storage.

---

## Tab 6 — ⚙️ System Stats

Real-time platform metrics:

| Metric | Description |
|---|---|
| Uptime | Time since last server restart |
| Registered Users | Total user count |
| Uploaded Files | Documents in the uploads directory |
| Active Sessions | Current active Streamlit sessions |
| Database Size | SQLite database file size |
| Knowledge Base Size | FAISS index size |
| Graph Store | Node and relationship counts |

---

## Tab 7 — 📧 SMTP Configuration

Configure real email delivery for password reset functionality.

### Settings

| Field | Description |
|---|---|
| **SMTP Server** | Mail server hostname (e.g. `smtp.gmail.com`) |
| **Port** | Usually `587` (TLS) or `465` (SSL) |
| **Username** | Email account username |
| **Password** | Email account password (app password recommended) |
| **From Address** | Sender address shown in reset emails |
| **TLS** | Enable STARTTLS (recommended) |

### Testing
Click **📧 Send Test Email** to send a test message to the admin email address and verify delivery.

### Mock Mode
If SMTP is not configured, password reset tokens are logged to the **FastAPI container console** instead of being emailed. This is suitable for development/demo environments.

---

## Tab 8 — 🚀 Onboarding Settings

Control the Quick Install Demo Data feature.

### Enable / Disable Quick Install Button
Toggle **Show Quick Install Demo Data button** on or off. When disabled, the green button disappears from:
- The sidebar for non-logged-in users
- The Authentication Required overlay
- The Home page guest banner

### Re-run Demo Installer
If demo installation failed or you want to reset:
1. Click **🔄 Reset Install Status** to mark the demo as "not installed".
2. Click **▶ Run Demo Installer** to trigger the installation process.

### Demo User Credentials

| Username | Password | Email | Role |
|---|---|---|---|
| `stephane@qubec` | `stephane2026` | `stephane@demo.local` | guest |
| `david@ontario` | `david2026` | `david@demo.local` | data_scientist |
| `yanhuo68` | `yanhuo68ottawa` | `yanhuo68@demo.local` | **admin** |

---

## Tips

- Keep API keys and credentials in the Admin Console — never hardcode them in application files.
- After pulling a new Ollama model, click **🔄 Refresh LLMs** in the sidebar of any RAG page to make it available.
- If email delivery fails, check that your provider allows SMTP access (Gmail requires an App Password, not your regular password).
- Use **Role Management** to create restricted roles for contractors or temporary analysts who should only see specific pages.
