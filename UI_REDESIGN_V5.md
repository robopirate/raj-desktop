# Raj Email Command Center — UI Redesign v5.0
## Architecture & Design Document

---

## 1. EXECUTIVE SUMMARY

**Current Problem:** The existing tkinter/customtkinter UI looks dated, has visibility issues (user said "i cant see"), and lacks modern UX patterns.

**Solution:** A complete UI overhaul using a **web-based frontend** (HTML/CSS/JS) served from a lightweight local server, embedded in a desktop window via `webview` or similar. This gives us:
- Real modern design (Tailwind CSS, glassmorphism, animations)
- Dark/Light mode toggle
- Responsive layout
- Professional look matching robopirate.in brand

**Alternative (if webview is too complex):** Aggressive customtkinter theming with proper spacing, contrast, and visual hierarchy.

---

## 2. TECHNOLOGY STACK

### Recommended: Hybrid Approach
```
Backend: Python (existing engine.py, db.py, gmail.py)
Frontend: HTML/CSS/JS served via Flask/FastAPI
Desktop: pywebview or native browser window
Communication: REST API + WebSocket for real-time updates
```

### Why This Stack?
- **HTML/CSS/JS** = Real modern UI (not tkinter limitations)
- **Flask/FastAPI** = Lightweight Python server
- **WebSocket** = Real-time dashboard updates without polling
- **pywebview** = Desktop app feel without Electron bloat

---

## 3. DESIGN SYSTEM

### 3.1 Color Palette (RoboPirate Brand)

```css
/* Light Mode */
--bg-primary: #F8FAFC;
--bg-secondary: #FFFFFF;
--bg-card: #FFFFFF;
--bg-sidebar: #FFFFFF;
--border: #E2E8F0;
--text-primary: #0F172A;
--text-secondary: #64748B;
--text-muted: #94A3B8;
--accent-teal: #0D9488;
--accent-teal-hover: #0F766E;
--accent-gold: #F59E0B;
--accent-gold-hover: #D97706;
--success: #10B981;
--danger: #EF4444;
--warning: #F59E0B;

/* Dark Mode */
--bg-primary: #0F172A;
--bg-secondary: #1E293B;
--bg-card: #1E293B;
--bg-sidebar: #1E293B;
--border: #334155;
--text-primary: #F1F5F9;
--text-secondary: #94A3B8;
--text-muted: #64748B;
--accent-teal: #2DD4BF;
--accent-teal-hover: #14B8A6;
```

### 3.2 Typography
```css
--font-family: 'Inter', 'Plus Jakarta Sans', system-ui, sans-serif;
--font-xs: 12px;
--font-sm: 14px;
--font-base: 16px;
--font-lg: 18px;
--font-xl: 24px;
--font-2xl: 32px;
--font-bold: 700;
--font-semibold: 600;
--font-medium: 500;
```

### 3.3 Spacing System
```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
--radius-sm: 6px;
--radius-md: 10px;
--radius-lg: 16px;
--radius-xl: 24px;
```

### 3.4 Shadows & Effects
```css
--shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
--shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1);
--shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1);
--shadow-glow-teal: 0 0 20px rgba(13,148,136,0.15);
--glass-bg: rgba(255,255,255,0.8);
--glass-border: rgba(255,255,255,0.3);
```

---

## 4. LAYOUT ARCHITECTURE

### 4.1 Overall Structure
```
┌─────────────────────────────────────────────────────────────┐
│  Sidebar (240px)  │  Main Content Area (flexible)           │
│                   │                                         │
│  🤖 RAJ           │  ┌─────────────────────────────────┐   │
│  Command Center   │  │  Header + Breadcrumbs           │   │
│                   │  └─────────────────────────────────┘   │
│  ─────────────    │  ┌─────────────────────────────────┐   │
│  📊 Dashboard     │  │                                 │   │
│  📈 Analytics     │  │  Content (Dashboard/            │   │
│  📧 Chat          │  │  Batches/Templates/etc)         │   │
│  📥 Import        │  │                                 │   │
│  📝 Templates     │  │                                 │   │
│  🚀 Batches       │  │                                 │   │
│  💬 Replies       │  │                                 │   │
│  🚫 Blacklist     │  │                                 │   │
│  ⚙️ Settings      │  │                                 │   │
│                   │  └─────────────────────────────────┘   │
│  ─────────────    │                                         │
│  🌓 Toggle Theme  │                                         │
│                   │                                         │
│  ● Running    ⏸ 🔍│                                         │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Sidebar Spec
- **Width:** 240px fixed
- **Background:** White (light) / #1E293B (dark)
- **Border-right:** 1px solid var(--border)
- **Logo Area:**
  - Robot emoji (🤖) at 32px, teal color
  - "RAJ" text: 24px bold, teal
  - "Command Center" text: 12px, muted
  - Padding: 24px
- **Nav Items:**
  - Height: 44px
  - Border-radius: 10px
  - Padding: 12px 16px
  - Icon + Label layout
  - **Active state:** Background #F0FDFA (light) / #134E4A (dark), text teal, bold
  - **Hover state:** Background #F8FAFC (light) / #334155 (dark)
  - **Transition:** 200ms ease
- **Bottom Status Bar:**
  - Height: 60px
  - Background: slightly darker than sidebar
  - Green dot + "Running" text
  - Pause (⏸) and Scan (🔍) buttons

### 4.3 Main Content Area
- **Background:** #F8FAFC (light) / #0F172A (dark)
- **Padding:** 32px
- **Max-width:** 1400px centered
- **Scroll:** Vertical when content overflows

---

## 5. PAGE DESIGNS

### 5.1 DASHBOARD PAGE

#### Header Section
```
┌──────────────────────────────────────────────────────────────┐
│  Dashboard                              [Refresh] [Export]   │
│  Overview of your email campaigns                            │
└──────────────────────────────────────────────────────────────┘
```

#### Stats Cards (4-column grid)
```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  📧 TOTAL    │  │  🏫 SCHOOL   │  │  🤝 CSR      │  │  🚫 BLACKLIST│
│              │  │              │  │              │  │              │
│  1,247       │  │  523         │  │  412         │  │  18          │
│  leads       │  │  leads       │  │  leads       │  │  blocked     │
│              │  │              │  │              │  │              │
│  ↑ 12%       │  │  ↑ 8%        │  │  ↑ 15%       │  │  ↓ 2%        │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```
- Card: White bg, rounded-16, shadow-md, padding 24px
- Number: 32px bold, primary text
- Label: 14px, muted
- Trend: Small badge with arrow

#### Pipeline Table
```
┌─────────────────────────────────────────────────────────────────────┐
│  📅 Email Pipeline                                                  │
├──────────┬────────┬────────┬──────────┬──────────┬────────────────┤
│  Day     │  Total │  Sent  │  Bounced │  Replied │  Status        │
├──────────┼────────┼────────┼──────────┼──────────┼────────────────┤
│  Day 1   │  245   │  245   │  3       │  12      │  ✅ Completed  │
│  Day 3   │  245   │  180   │  2       │  8       │  ⏳ In Progress│
│  Day 5   │  245   │  0     │  0       │  0       │  ⏸ Pending     │
│  Day 7   │  245   │  0     │  0       │  0       │  ⏸ Pending     │
│  Day 10  │  245   │  0     │  0       │  0       │  ⏸ Pending     │
└──────────┴────────┴────────┴──────────┴──────────┴────────────────┘
```
- Table: White bg, rounded-16, shadow-sm
- Header: 12px uppercase, muted, bg slightly darker
- Row hover: bg #F8FAFC
- Status badges: Green (completed), Blue (in progress), Gray (pending)

#### Active Batches
```
┌─────────────────────────────────────────────────────────────────────┐
│  🚀 Active Campaigns                                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Pune Schools Batch              SCHOOL    3/5 days    ████████░░  │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                          │
│  │ D1  │ │ D3  │ │ D5  │ │ D7  │ │ D10 │                          │
│  │Done │ │Send │ │Queue│ │Queue│ │Queue│                          │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘                          │
│                                                                     │
│  CSR WSL Campaign                CSR-WSL   1/5 days    ██░░░░░░░░  │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                          │
│  │ D1  │ │ D3  │ │ D5  │ │ D7  │ │ D10 │                          │
│  │Done │ │Sched│ │Queue│ │Queue│ │Queue│                          │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```
- Campaign card: White bg, rounded-16, shadow-md
- Header: Campaign name (bold), sequence badge, progress bar
- Day pills: 5 equal columns, colored by status
  - Done: Green bg, white text
  - Sending: Teal bg, white text, subtle pulse animation
  - Scheduled: Gold bg, dark text
  - Queue: Gray bg, muted text
- Progress bar: 120px wide, 6px height, rounded

---

### 5.2 BATCHES PAGE

#### Create Campaign Form
```
┌─────────────────────────────────────────────────────────────────────┐
│  🎯 New Campaign                                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Campaign Name                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  e.g., "Pune Schools June 2026"                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Pull From: [Leads ▼]    Sequence: [CSR-WSL-5 ▼]                   │
│                                                                     │
│  Sub-Pool: [(All) ▼]                                               │
│                                                                     │
│  Size: [50  ]    Day: [1 ▼]    Schedule: [2026-06-20 10:00 ▼]     │
│                                                                     │
│  [🚀 CREATE BATCH FROM POOL]                                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```
- Form card: White bg, rounded-16, shadow-lg
- Inputs: 44px height, rounded-10, border 1px
- Focus state: Border teal, subtle glow
- Button: Full width, 48px height, teal bg, white text, bold, rounded-12
- Hover: Darker teal, slight lift (translateY -1px)

#### Active Campaigns List
(Same as Dashboard but with more detail and actions)

---

### 5.3 IMPORT PAGE

#### Lead Import Section
```
┌─────────────────────────────────────────────────────────────────────┐
│  📥 Import Leads                                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  [Drag & drop CSV/Excel files here]                                 │
│  or click to browse                                                 │
│                                                                     │
│  ───────────── OR ─────────────                                     │
│                                                                     │
│  Paste emails (one per line):                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  principal@school1.edu                                      │   │
│  │  principal@school2.edu                                      │   │
│  │  ...                                                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Assign to Pool: [School ▼]    Sub-Pool: [Pune ▼]                  │
│                                                                     │
│  [📥 IMPORT 247 LEADS]                                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```
- Drag-drop zone: Dashed border, centered text, icon
- On drag: Border teal, bg teal-50
- Textarea: 200px height, monospace font
- Import button: Shows count dynamically

---

### 5.4 TEMPLATES PAGE

#### Template Editor
```
┌─────────────────────────────────────────────────────────────────────┐
│  📝 Email Templates                                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  [School ▼]  [Day 1 ▼]  [HTML ▼]                                    │
│                                                                     │
│  Subject:                                                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Introducing WE Smart Lab for Your School                   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Body:                                                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  <html>...                                                  │   │
│  │  Rich text editor with formatting toolbar                   │   │
│  │  ...                                                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  [💾 Save Template]  [👁 Preview]  [📧 Test Send]                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```
- Sequence tabs: Horizontal, pill-style
- Day selector: 1, 3, 5, 7, 10 as buttons
- Format toggle: HTML / Plain Text
- Editor: Monaco-like or simple textarea with toolbar

---

## 6. COMPONENT LIBRARY

### 6.1 Buttons
```
Primary:   bg-teal-600, text-white, rounded-10, h-44, px-24, hover:bg-teal-700
Secondary: bg-white, border, text-gray-700, rounded-10, h-44, hover:bg-gray-50
Danger:    bg-red-500, text-white, rounded-10, h-44, hover:bg-red-600
Ghost:     bg-transparent, text-gray-600, hover:bg-gray-100
Icon:      w-36, h-36, rounded-8, bg-gray-100, hover:bg-gray-200
```

### 6.2 Cards
```
Base:      bg-white, rounded-16, shadow-md, p-24
Hover:     shadow-lg, translateY(-2px), transition 200ms
Bordered:  + border 1px solid gray-200
```

### 6.3 Badges
```
Success:   bg-green-100, text-green-800, rounded-full, px-12, py-4
Warning:   bg-yellow-100, text-yellow-800, rounded-full, px-12, py-4
Danger:    bg-red-100, text-red-800, rounded-full, px-12, py-4
Info:      bg-blue-100, text-blue-800, rounded-full, px-12, py-4
Teal:      bg-teal-100, text-teal-800, rounded-full, px-12, py-4
```

### 6.4 Inputs
```
Base:      bg-white, border 1px gray-300, rounded-10, h-44, px-16
Focus:     border-teal-500, ring-2 teal-100
Error:     border-red-500, bg-red-50
Disabled:  bg-gray-100, text-gray-400
```

### 6.5 Progress Indicators
```
Bar:       h-6, rounded-full, bg-gray-200, fill: teal
Circle:    48px diameter, stroke 4px, teal
Spinner:   24px, teal, animated rotate
```

---

## 7. ANIMATIONS & INTERACTIONS

### 7.1 Page Transitions
- Duration: 200ms
- Easing: ease-out
- Effect: Fade in + slight translateY (10px → 0)

### 7.2 Card Hover
- Duration: 200ms
- Effect: shadow-lg, translateY(-2px)

### 7.3 Button Press
- Duration: 100ms
- Effect: scale(0.98)

### 7.4 Loading States
- Skeleton screens for data loading
- Spinner for actions
- Progress bar for batch operations

### 7.5 Toast Notifications
- Position: Top-right, stacked
- Duration: 3s
- Types: Success (green), Error (red), Info (blue), Warning (yellow)
- Animation: Slide in from right, fade out

---

## 8. RESPONSIVE BREAKPOINTS

```
Desktop:  >= 1280px  (full layout)
Laptop:   >= 1024px  (slightly compressed sidebar)
Tablet:   >= 768px   (collapsible sidebar, 2-col grid)
Mobile:   < 768px    (bottom nav, single column, stacked cards)
```

---

## 9. API ENDPOINTS (Backend)

### 9.1 Dashboard
```
GET  /api/dashboard/summary       → Stats cards data
GET  /api/dashboard/pipeline      → Day-wise pipeline table
GET  /api/dashboard/batches       → Active batches list
```

### 9.2 Batches
```
POST /api/batches                 → Create new batch
GET  /api/batches                 → List all batches
GET  /api/batches/:id             → Batch details
POST /api/batches/:id/start       → Start batch
POST /api/batches/:id/pause       → Pause batch
DELETE /api/batches/:id           → Delete batch
```

### 9.3 Leads
```
POST /api/leads/import            → Import leads (CSV/paste)
GET  /api/leads                   → List leads
GET  /api/leads/pools             → List pools/sub-pools
```

### 9.4 Templates
```
GET  /api/templates/:seq/:day     → Get template
PUT  /api/templates/:seq/:day     → Update template
POST /api/templates/:seq/:day/test → Test send
```

### 9.5 Settings
```
GET  /api/settings                → Get all settings
PUT  /api/settings                → Update settings
```

### 9.6 Real-time (WebSocket)
```
WS   /ws                          → Live dashboard updates
  Events: batch_progress, new_reply, bounce_alert, etc.
```

---

## 10. FILE STRUCTURE

```
raj-desktop/
├── backend/
│   ├── __init__.py
│   ├── app.py              # Flask/FastAPI app
│   ├── engine.py           # Existing (modified for API)
│   ├── db.py               # Existing
│   ├── gmail.py            # Existing
│   ├── config.py           # Settings
│   └── websocket.py        # WebSocket handler
├── frontend/
│   ├── index.html
│   ├── css/
│   │   ├── main.css
│   │   ├── components.css
│   │   └── animations.css
│   ├── js/
│   │   ├── app.js
│   │   ├── api.js
│   │   ├── dashboard.js
│   │   ├── batches.js
│   │   ├── templates.js
│   │   └── websocket.js
│   └── assets/
│       ├── logo.svg
│       └── icons/
├── main.py                 # Entry point (starts backend + opens webview)
├── requirements.txt
└── README.md
```

---

## 11. IMPLEMENTATION PHASES

### Phase 1: Backend API (Week 1)
- [ ] Set up Flask/FastAPI server
- [ ] Create REST endpoints for all features
- [ ] Add WebSocket for real-time updates
- [ ] Test API with curl/Postman

### Phase 2: Frontend Core (Week 1-2)
- [ ] Set up HTML/CSS/JS structure
- [ ] Implement design system (colors, typography, components)
- [ ] Build sidebar navigation
- [ ] Build layout shell

### Phase 3: Pages (Week 2)
- [ ] Dashboard page
- [ ] Batches page (with sequence selector)
- [ ] Import page
- [ ] Templates page
- [ ] Settings page

### Phase 4: Polish (Week 3)
- [ ] Dark mode toggle
- [ ] Animations & transitions
- [ ] Toast notifications
- [ ] Loading states
- [ ] Error handling
- [ ] Responsive design

### Phase 5: Desktop Wrapper (Week 3)
- [ ] pywebview integration
- [ ] System tray icon
- [ ] Auto-start option
- [ ] Packaging (PyInstaller)

---

## 12. KEY FEATURES FOR OMkar

### 12.1 Sequence Selector (Critical)
- Dropdown in batch creation: school / csr / csr-wsl-5
- Visual badge showing selected sequence
- Ability to change sequence before launch

### 12.2 Plain Text Emails (Done in backend)
- Toggle in template editor: HTML / Plain Text
- Preview both versions
- Backend already supports multipart

### 12.3 Trial Run (Critical)
- "Test Campaign" button
- Sends all 5 emails to test address with 2-min gaps
- Shows preview of each email before sending

### 12.4 Batch Management
- Create batches from lead pools
- Pause/resume campaigns
- Delete families (return leads to pool)
- Clone families

### 12.5 Lead Import
- CSV/Excel upload
- Paste emails
- Smart deduplication
- Pool assignment

---

## 13. SCREENSHOTS / WIREFRAMES

### Dashboard (Light Mode)
```
+----------------------------------------------------------+
| 🤖 RAJ    |  Dashboard                           [🌓]    |
| Command   |  Overview of your campaigns                   |
| Center    |                                               |
|           |  +--------+ +--------+ +--------+ +--------+  |
| ────────  |  |  1,247 | |   523  | |   412  | |   18   |  |
| 📊 Dash   |  |  Total | | School | |  CSR   | | Blocked|  |
| 📈 Analyt |  |  leads | |  leads | | leads  | |        |  |
| 📧 Chat   |  +--------+ +--------+ +--------+ +--------+  |
| 📥 Import |                                               |
| 📝 Templ  |  📅 Email Pipeline                          |
| 🚀 Batch  |  +----------------------------------------+  |
| 💬 Replies|  | Day | Total | Sent | Bounced | Status   |  |
| 🚫 Black  |  |-----|-------|------|---------|----------|  |
| ⚙️ Settin |  | D1  |  245  | 245  |    3    | ✅ Done  |  |
|           |  | D3  |  245  | 180  |    2    | ⏳ Sending|  |
| 🌓 Toggle |  | D5  |  245  |   0  |    0    | ⏸ Pending|  |
|           |  | D7  |  245  |   0  |    0    | ⏸ Pending|  |
| ● Running |  | D10 |  245  |   0  |    0    | ⏸ Pending|  |
| ⏸  🔍     |  +----------------------------------------+  |
|           |                                               |
|           |  🚀 Active Campaigns                        |
|           |  +----------------------------------------+  |
|           |  | Pune Schools    [SCHOOL]  3/5 ████████░ |  |
|           |  | [D1✅][D3▶][D5⏸][D7⏸][D10⏸]          |  |
|           |  +----------------------------------------+  |
|           |  | CSR WSL         [CSR-WSL] 1/5 ██░░░░░░░ |  |
|           |  | [D1✅][D3⏰][D5⏸][D7⏸][D10⏸]         |  |
|           |  +----------------------------------------+  |
+----------------------------------------------------------+
```

---

## 14. NOTES FOR KIMI CODE

### What to preserve from existing code:
- `engine.py` — core logic (with text_body changes)
- `db.py` — database layer (with text_body migration)
- `gmail.py` — email sending (with multipart support)
- `raj_brain.py` — AI responses
- `analytics.py` — analytics

### What to replace:
- `raj_chat.py` — entire UI (keep only business logic calls)
- `main.py` — entry point (start web server + open browser/webview)

### Key integration points:
```python
# Backend API calls existing engine methods
from engine import CampaignEngine
from db import Database

engine = CampaignEngine(...)

@app.get("/api/dashboard/summary")
def get_summary():
    return engine.get_summary()

@app.post("/api/batches")
def create_batch(data: BatchCreate):
    return engine.create_batch_from_pool(**data.dict())
```

---

## 15. SUCCESS CRITERIA

- [ ] UI looks modern and professional (comparable to SaaS apps)
- [ ] Dark mode works perfectly
- [ ] All existing features work (no regression)
- [ ] Sequence selector is visible and functional
- [ ] Trial run feature works
- [ ] Plain text emails send correctly
- [ ] App starts without errors
- [ ] User says "this looks good"

---

**Document Version:** 1.0
**Author:** Architect (AI)
**Date:** 2026-06-13
**For:** Kimi Code Implementation
