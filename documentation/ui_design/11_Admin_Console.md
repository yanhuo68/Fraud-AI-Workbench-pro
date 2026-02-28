# 🛡️ Admin Console — UI Design Specification

**Page:** `pages/11_🛡️_Admin_Console.py (wrapper for src/views/admin_console/)`  
**Layout:** Wide  
**Access:** admin role only  
**Theme:** Dark Glassmorphism

---

## Page Layout Overview

```
┌──────────────────────────────────────────────────────────────────┐
│  🛡️ Admin Console                              [st.title]       │
│  "System administration and configuration..."  [st.caption]    │
├──────────────────────────────────────────────────────────────────┤
│  [ 👥 Users ] [ 🎭 Roles ] [ 🔑 API Keys ] [ 💬 SMTP ] [ ⚡ Onboarding ] │  ← 5 tabs
├──────────────────────────────────────────────────────────────────┤
│  [Tab content area]                                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## Tab 1 — 👥 User Management

```
┌──────────────────────────────────────┬──────────────────────────┐
│  👥 All Users                        │  ➕ Create New User       │
│  ──────────────────────────────────  │  ─────────────────────── │
│  Username │ Role  │ Email  │ Actions │  Username: [────────────]│
│  yanhuo68 │ admin │ y@d.c  │ ✏️ 🗑   │  Password: [────────────]│
│  stephane │ guest │ s@d.c  │ ✏️ 🗑   │  Email:    [────────────]│
│  david    │ data_ │ d@d.c  │ ✏️ 🗑   │  Role:     [▾ guest   ] │
│           │       │        │        │  [Create User btn]       │
│  [🔄 Refresh Users list]            │  ─────────────────────── │
│                                      │  PATCH User              │
│                                      │  [User ▾] [Field ▾]      │
│                                      │  New value: [──────────] │
│                                      │  [Update User btn]       │
└──────────────────────────────────────┴──────────────────────────┘
```

### User Table
| Property | Spec |
|---|---|
| Render | `st.dataframe(users_df)` — all users, `use_container_width=True` |
| Columns | Username, Role, Email (masked), Created At, Actions |
| Edit action | `st.button("✏️")` → opens inline PATCH form |
| Delete action | `st.button("🗑")` → `st.warning(confirm)` + confirm delete button |

### Create User Form
- `st.form("create_user_form")` — right column
- Fields: Username, Password, Email, Role (selectbox: guest/data_scientist/admin)

### PATCH User Form
- Select user dropdown + field dropdown (role / email / username / password)
- New value text input (password masked)
- `st.button("Update User", type="primary")`

---

## Tab 2 — 🎭 Role Management

```
┌──────────────────────────────────────┬──────────────────────────┐
│  🎭 Current Roles                    │  ➕ Create / Update Role  │
│  ──────────────────────────────────  │  ─────────────────────── │
│  Role Name     │ Pages Permitted     │  Role name: [──────────] │
│  admin         │ [all 10 pages]      │  Pages:                  │
│  data_scientist│ [7 pages]           │  [✅ Data Hub]           │
│  guest         │ [3 pages]           │  [✅ SQL RAG]            │
│                │                     │  [  ] Graph RAG          │
│  [🔄 Refresh]  │                     │  [  ] Multimodal         │
│                │                     │  [  ] Trends             │
│                │                     │  [✅ ML Workflow]        │
│                │                     │  [  ] Fine Tuning        │
│  [🗑 Delete Role]                    │  [  ] API Hub            │
│  Role name: [────] [Delete btn]      │  [  ] Admin Console      │
│                                      │  [Create/Update btn]     │
└──────────────────────────────────────┴──────────────────────────┘
```

| Element | Spec |
|---|---|
| Roles table | `st.dataframe(roles_df)` — name, permitted pages (comma-joined) |
| Page checkboxes | `st.multiselect("Pages", all_pages, default=existing_pages)` |
| Create/Update button | `st.button("Create / Update Role", type="primary")` |
| Delete form | `st.text_input("Role Name to Delete")` + `st.button("🗑 Delete Role")` |

---

## Tab 3 — 🔑 API Keys

```
┌──────────────────────────────────────────────────────────────────┐
│  🔑 LLM Provider API Key Configuration                          │
│  ──────────────────────────────────────────────────────────────  │
│  OpenAI API Key:      [●●●●●●●●●●●●●●●●●●] [👁 Show]  [💾 Save] │
│  DeepSeek API Key:    [●●●●●●●●●●●●●●●●●●]             [💾 Save] │
│  Google API Key:      [●●●●●●●●●●●●●●●●●●]             [💾 Save] │
│  Anthropic API Key:   [●●●●●●●●●●●●●●●●●●]             [💾 Save] │
│                                                                  │
│  🤖 Local LLM (Ollama) Manager                                  │
│  ──────────────────────────────────────────────────────────────  │
│  Ollama Host: [http://ollama:11434      ]  [🔗 Test Connection] │
│  Pull Model:  [llama3:8b               ]  [⬇ Pull Model]       │
│  [Model list table — currently pulled models]                   │
└──────────────────────────────────────────────────────────────────┘
```

| Element | Spec |
|---|---|
| Key inputs | `st.text_input(..., type="password")` + optional show/hide toggle |
| Save buttons | Inline per-row `st.button("💾 Save")` |
| Ollama host | `st.text_input("Ollama Host", value="http://ollama:11434")` |
| Test connection | `st.button("🔗 Test")` → `st.success()` / `st.error()` |
| Pull model | `st.text_input("Model to Pull")` + `st.button("⬇ Pull")` → `st.progress()` |
| Pulled models | `st.dataframe(ollama_models_df)` |

---

## Tab 4 — 💬 SMTP Configuration

```
┌────────────────────────────────┬──────────────────────────────────┐
│  SMTP Settings                 │  📧 Test Email                    │
│  ─────────────────────────     │  ──────────────────────────────   │
│  Server:   [──────────────]    │  To:      [────────────────────]  │
│  Port:     [587          ]     │  Subject: [Test Email          ]  │
│  Username: [──────────────]    │  Body:    [────────────────────]  │
│  Password: [●●●●●●●●●●●●●]    │                                   │
│  From:     [──────────────]    │  [📤 Send Test Email]             │
│  TLS:      [✅ enabled    ]    │                                   │
│            [💾 Save SMTP]      │  Status: ✅ Sent (mock log)       │
└────────────────────────────────┴──────────────────────────────────┘
```

| Element | Spec |
|---|---|
| Server input | `st.text_input("SMTP Server")` |
| Port | `st.number_input("Port", value=587)` |
| TLS toggle | `st.checkbox("Enable TLS", value=True)` |
| Save button | `st.button("💾 Save SMTP Configuration", type="primary")` |
| Test form | `st.form("test_smtp_form")` — 3 fields + submit |
| Result | `st.success("✅ Email sent")` or `st.info("📋 Logged to console (Mock mode)")` |

---

## Tab 5 — ⚡ Onboarding Settings

```
┌──────────────────────────────────────────────────────────────────┐
│  ⚡ Quick Install Demo Data Settings                             │
│  ──────────────────────────────────────────────────────────────  │
│  Feature Enabled:  [✅ Toggle ON/OFF]                           │
│  Install Status:   [✅ Installed] / [⏳ Not yet installed]      │
│  [🔄 Reset Install Status]   ← secondary button               │
│  [💾 Save Settings]          ← primary button                  │
│                                                                  │
│  ── Demo Accounts Preview ──                                    │
│  Username         │ Password      │ Role                        │
│  yanhuo68         │ yanhuo68ottawa│ admin                       │
│  david@ontario    │ david2026     │ data_scientist              │
│  stephane@qubec   │ stephane2026  │ guest                       │
└──────────────────────────────────────────────────────────────────┘
```

| Element | Spec |
|---|---|
| Enable toggle | `st.toggle("Enable Quick Install button", value=True)` |
| Status | `st.success("✅ Demo installed")` / `st.warning("⏳ Not yet installed")` |
| Reset button | `st.button("🔄 Reset Install Status")` — secondary |
| Save button | `st.button("💾 Save Settings", type="primary")` |
| Preview table | Markdown table with demo user credentials |

---

## Admin Console Specific CSS

```css
/* Red accent for admin-only elements */
[admin-badge] {
  background: rgba(231, 76, 60, 0.15);
  border: 1px solid rgba(231, 76, 60, 0.4);
  border-radius: 8px;
  padding: 0.5rem;
}
```

---

## Colour Summary

| Element | Colour |
|---|---|
| Admin-only border | `rgba(231,76,60,0.4)` red |
| Active toggle | `#2ecc71` green |
| Danger (delete) | `#e74c3c` red |
| Save success | `#2ecc71` green |
| User table header | `rgba(255,75,75,0.1)` subtle red tint |
