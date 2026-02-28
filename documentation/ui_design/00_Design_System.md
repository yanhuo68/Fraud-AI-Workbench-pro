# 🎨 Sentinel Pro — Global Design System

**Version:** 2026.02  
**Theme:** Dark Glassmorphism · Premium AI Workbench

---

## Design Philosophy

Sentinel Pro uses a **dark premium glassmorphism** aesthetic inspired by cybersecurity dashboards and professional AI tooling. The design prioritises:

1. **Legibility on dark backgrounds** — high-contrast text on near-black surfaces
2. **Spatial hierarchy** — cards, dividers, and whitespace guide the eye
3. **Micro-interactivity** — hover glows, scale transforms, and transitions make the UI feel alive
4. **Role-clarity** — colour-coded badges (red = admin, orange = warning, green = success) keep status instantly readable

---

## Colour Palette

| Role | Hex | Usage |
|---|---|---|
| **Background** | `#0d0d0d` | Page root background |
| **Surface** | `#1a1a1a → #0d0d0d` | Radial gradient applied to `.stApp` |
| **Sidebar** | `rgba(15,15,15,0.95)` | Glassmorphism sidebar panel |
| **Accent Red** | `#ff4b4b` | Brand colour — SENTINEL logo, borders |
| **Accent Green** | `#22a44e → #2ecc71` | Success, Quick Install CTA, positive status |
| **Accent Orange** | `#f39c12` | Warning badges, auth-required indicators |
| **Text Primary** | `#e0e0e0` | Body text |
| **Text White** | `#ffffff` | Headings inside cards and sidebar |
| **Text Muted** | `#a0a0a0` | Captions, timestamps, secondary labels |
| **Border Subtle** | `rgba(255,75,75,0.2)` | Sidebar right-border, card borders |
| **Card Glass** | `rgba(255,255,255,0.05)` | Glassmorphism card surface |

---

## Typography

| Element | Font | Size | Weight | Colour |
|---|---|---|---|---|
| Page title (`st.title`) | System default (Inter/Streamlit) | 2rem | Bold | `#ffffff` |
| Section header (`st.header`) | System default | 1.5rem | Semi-bold | `#ffffff` |
| Sub-header (`st.subheader`) | System default | 1.2rem | Semi-bold | `#ffffff` |
| Body text (`st.write`) | System default | 1rem | Regular | `#e0e0e0` |
| Caption (`st.caption`) | System default | 0.82rem | Regular | `#a0a0a0` |
| Code / Monospace | `monospace` | 0.88rem | Regular | `#e0e0e0` |
| Endpoint badge | `monospace` | 0.88rem | Bold | White on colour |

---

## Spacing & Layout

| Token | Value |
|---|---|
| Page padding | Streamlit default (`1rem` horizontal) |
| Card padding | `1.5rem` |
| Card border-radius | `12px – 20px` |
| Divider margin | `0.5rem` vertical |
| Column gap | `1rem` (Streamlit default) |
| Section gap | `st.divider()` or `st.markdown("---")` |

---

## Card Component (Glassmorphism)

Used for module tiles on the Home page and info panels:

```css
background: rgba(255, 255, 255, 0.05);
border: 1px solid rgba(255, 75, 75, 0.3);
border-radius: 16px;
padding: 1.5rem;
backdrop-filter: blur(10px);
transition: transform 0.2s ease, box-shadow 0.2s ease;

/* Hover state */
transform: translateY(-2px);
box-shadow: 0 8px 32px rgba(255, 75, 75, 0.2);
```

---

## Button Styles

### Primary (default Streamlit)
- Background: Streamlit theme blue → overridden to red where needed
- Used for: main form submits, "Run", "Login" CTAs

### Secondary
- Background: transparent with border
- Used for: "Cancel", "Back", destructive confirmations

### Green CTA (Quick Install)
```css
background: linear-gradient(135deg, #1a7a3c 0%, #22a44e 100%);
color: #ffffff;
border: 1px solid #27ae60;
font-weight: 700;
box-shadow: 0 0 18px rgba(34,164,78,0.6);
/* Hover */
background: linear-gradient(135deg, #22a44e 0%, #2ecc71 100%);
box-shadow: 0 0 32px rgba(34,164,78,0.95);
```

---

## Status / Badge Colours

| Status | Background | Usage |
|---|---|---|
| ✅ Success (2xx) | `#2ecc71` | API response OK, completed tasks |
| ⚠️ Warning (4xx) | `#f39c12` | Auth missing, bad input |
| ❌ Error (5xx / 0) | `#e74c3c` | Server error, unreachable |
| 🔵 Info | `#3498db` | Informational banners |
| 🟡 Pending | `#f1c40f` | In-progress states |

---

## Endpoint Method Badges (API Hub)

```css
/* POST */   background: #49cc90; color: white;
/* GET */    background: #61affe; color: white;
/* PATCH */  background: #50e3c2; color: #333;
/* DELETE */ background: #f93e3e; color: white;
```

---

## Sidebar Glassmorphism

```css
background-color: rgba(15, 15, 15, 0.95);
backdrop-filter: blur(15px);
border-right: 1px solid rgba(255, 75, 75, 0.2);
```

Logo image:
```css
filter: drop-shadow(0 0 12px rgba(255, 75, 75, 0.5));
border-radius: 10px;
transition: transform 0.3s ease;
/* Hover */
transform: scale(1.05);
filter: drop-shadow(0 0 18px rgba(255, 75, 75, 0.7));
```

---

## Responsive Behaviour

The application runs inside Docker and is accessed via web browser. Streamlit's default responsive grid is used:

- **3 columns** — stats bars, module cards, health probes
- **2 columns** — form + info panel pattern across RAG pages
- **Full-width** — tables, code blocks, chat areas
- **Mobile** — Streamlit collapses to single column; sidebar becomes a hamburger menu

---

## Iconography

All icons are emoji-based (no external icon library dependency):

| Domain | Emoji Set |
|---|---|
| Navigation | 🏠 📁 🧠 🕸️ 🎥 📈 🔄 🧬 🔌 🛡️ |
| Status | ✅ ⚠️ ❌ 🔴 🟢 🟡 |
| Actions | ▶ 🔄 📥 📤 🗑 🔍 💾 📋 |
| Auth | 🔐 🔑 📝 🚪 👤 🛡️ |
| Data | 🗄️ 📄 📊 🕸️ 📋 |
| System | ⚙️ 🔔 📡 🧬 |
