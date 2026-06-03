# FRONTEND SPECIFICATION
## Raj AI Gmail Agent v5.0
### RoboPirate Technologies | 2026-06-03

---

## 1. DESIGN SYSTEM (LOCKED)

### 1.1 Brand Colors
```
┌─────────────────────────────────────────────┐
│  PRIMARY COLORS                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ #59ced9  │  │ #febe32  │  │ #6d45a5  │  │
│  │  CYAN    │  │  GOLD    │  │  PURPLE  │  │
│  │  School  │  │   CSR    │  │  Accent  │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│                                              │
│  SEMANTIC COLORS                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ #34c759  │  │ #ff3b30  │  │ #ff9500  │  │
│  │ Success  │  │  Danger  │  │  Warning │  │
│  │  Sent    │  │  Bounce  │  │  Pending │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│                                              │
│  NEUTRAL COLORS                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ #0A1628  │  │ #111D2E  │  │ #8B949E  │  │
│  │   BG     │  │  Panel   │  │   Dim    │  │
│  │ #0f0f1a  │  │ #1a1a2e  │  │ #e0e0e0  │  │
│  │ Alt BG   │  │ AltPanel │  │  Text    │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│                                              │
│  BORDER: #2a2a4e                            │
└─────────────────────────────────────────────┘
```

### 1.2 Typography
```
Font Family: "Segoe UI" (system UI font)
Hierarchy:
  H1: 24-28px, Bold          → Section headers
  H2: 18-20px, Bold          → Card titles
  H3: 14-16px, Bold          → Subsection
  Body: 13px, Regular        → Content
  Caption: 11px, Regular     → Metadata
  KPI: 28px, Bold            → Numbers
```

### 1.3 Spacing
```
Base unit: 8px
Card padding: 16-20px
Card gap: 12-16px
Section gap: 24px
Sidebar width: 200px
Content max-width: 1200px
Border radius (cards): 10-12px
Border radius (buttons): 8px
Border radius (pills): 999px
```

### 1.4 Component Patterns
```
Cards:
  Background: #111D2E
  Border: 1px solid #2a2a4e
  Border-radius: 10px
  Hover: border-color rgba(89,206,217,0.3)

Buttons (Primary):
  Background: #59ced9
  Text: #0A1628 (dark on light)
  Font: 12px Bold
  Height: 36px
  Border-radius: 8px
  Hover: #4ab8c4

Buttons (Secondary):
  Background: #2a2a4e
  Text: #E6EDF3
  Font: 12px Bold
  Height: 36px
  Border-radius: 8px
  Hover: rgba(255,255,255,0.1)

Status Pills:
  Padding: 4px 10px
  Border-radius: 999px
  Font: 10px Bold
  Completed: bg rgba(52,199,89,0.15), text #34c759
  Running:   bg rgba(88,166,255,0.15), text #58a6ff
  Scheduled: bg rgba(210,153,34,0.15), text #d29922
  Draft:     bg rgba(139,148,158,0.15), text #8B949E
  Bounced:   bg rgba(255,59,48,0.15), text #ff3b30
  Replied:   bg rgba(89,206,217,0.15), text #59ced9
```

---

## 2. SCREEN SPECIFICATIONS

### 2.1 Desktop UI (customtkinter)

#### Layout
```
┌──────────────────────────────────────────────────┐
│  🏴‍☠  RoboPirate Raj    v4.3    [—] [□] [×]    │
├──────────┬───────────────────────────────────────┤
│          │                                       │
│  📊 Dash │  CONTENT AREA                         │
│  💬 Chat │  (switches based on sidebar)         │
│  📁 Imp  │                                       │
│  📝 Tmpl │                                       │
│  🚀 Batch│                                       │
│  💌 Reply│                                       │
│  🚫 Bl   │                                       │
│  ⚙  Set  │                                       │
│          │                                       │
└──────────┴───────────────────────────────────────┘
Sidebar: 200px wide, #0f0f1a background
Content: Fill remaining, #0A1628 background
```

#### Sidebar Navigation
```
Items (top to bottom):
  1. 📊 Dashboard    → KPI cards + summary
  2. 💬 Chat         → Raj AI chat interface
  3. 📁 Import       → File upload + smart import
  4. 📝 Templates    → Template viewer + sync
  5. 🚀 Batches      → Batch list + controls
  6. 💌 Replies      → Reply inbox + sentiment
  7. 🚫 Blacklist    → Blocked emails list
  8. 📊 Charts       → Analytics dashboard (v4.3)
  9. ⚙  Settings     → Configuration

Active state: bg rgba(89,206,217,0.12), text #59ced9, bold
Inactive state: text #8B949E, regular
Hover state: bg rgba(255,255,255,0.05)
```

### 2.2 Dashboard View
```
┌──────────────────────────────────────────────────┐
│  📊 Dashboard                                     │
├──────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ TOTAL    │ │  SENT    │ │ REPLIED  │          │
│  │ 1,247    │ │   892    │ │    73    │          │
│  └──────────┘ └──────────┘ └──────────┘          │
│                                                    │
│  ┌──────────────────────────────────────────┐     │
│  │  ACTIVE BATCHES                          │     │
│  │  ┌────────────────────────────────────┐  │     │
│  │  │ Batch-23  [RUNNING]  45/100  ████░░│  │     │
│  │  └────────────────────────────────────┘  │     │
│  └──────────────────────────────────────────┘     │
│                                                    │
│  ┌──────────────────────────────────────────┐     │
│  │  RECENT ACTIVITY                         │     │
│  │  ● D1  school  principal@...  sent      │     │
│  │  ● D3  csr     manager@...    replied   │     │
│  └──────────────────────────────────────────┘     │
└──────────────────────────────────────────────────┘
```

### 2.3 Charts View (v4.3 — NEW)
```
┌──────────────────────────────────────────────────┐
│  📊 Campaign Analytics              [🔄 Refresh] │
├──────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────┐│
│  │ 1,247   │ │   892    │ │    73    │ │ 8.2%││
│  │  LEADS  │ │   SENT   │ │ REPLIED  │ │ RATE││
│  └──────────┘ └──────────┘ └──────────┘ └─────┘│
│                                                    │
│  ┌──────────────────────┐ ┌──────────────────┐  │
│  │  SEND TRENDS (14d)   │ │ REPLY SENTIMENT  │  │
│  │                      │ │                  │  │
│  │    ████████          │ │    ┌──────┐      │  │
│  │   ██        ██       │ │    │  65% │      │  │
│  │  ██   SCHOOL  ██     │ │    │Positive│    │  │
│  │ ██████████████████   │ │    └──────┘      │  │
│  │       CSR            │ │    ┌──────┐      │  │
│  └──────────────────────┘ └──────────────────┘  │
│                                                    │
│  ┌──────────────────────┐ ┌──────────────────┐  │
│  │ SEQUENCE COMPARE     │ │ RECENT ACTIVITY  │  │
│  │  SCHOOL ████████     │ │ ● D1 school sent │  │
│  │    CSR  ██████       │ │ ● D3 csr replied │  │
│  └──────────────────────┘ └──────────────────┘  │
└──────────────────────────────────────────────────┘
```

### 2.4 Chat View
```
┌──────────────────────────────────────────────────┐
│  💬 Chat with Raj                                 │
├──────────────────────────────────────────────────┤
│                                                    │
│  🤖 Raj: Good morning! How can I help you        │
│          with your campaigns today?               │
│                                                    │
│  👤 You: Show me yesterday's stats               │
│                                                    │
│  🤖 Raj: Yesterday you sent 34 emails...         │
│          School: 20, CSR: 14                     │
│          3 replies received (all positive)        │
│                                                    │
├──────────────────────────────────────────────────┤
│  [Type your message...]              [Send]      │
└──────────────────────────────────────────────────┘
```

### 2.5 Batches View
```
┌──────────────────────────────────────────────────┐
│  🚀 Batches                    [+ From Pool]     │
├──────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────┐     │
│  │ Name     Seq    Status   Progress        │     │
│  ├──────────────────────────────────────────┤     │
│  │ Batch-23 SCHOOL RUNNING  ████████░░ 73%  │     │
│  │ Batch-24 CSR    SCHED    ░░░░░░░░░░ 0%   │     │
│  │ Batch-22 SCHOOL COMPLETE ██████████ 100% │     │
│  └──────────────────────────────────────────┘     │
└──────────────────────────────────────────────────┘
```

---

## 3. RESPONSIVE BEHAVIOR

### 3.1 DPI Awareness
```python
# Current implementation in raj_chat.py:
ctk.set_widget_scaling(1.0)  # Auto-detected
ctk.set_window_scaling(1.0)   # Auto-detected
```

### 3.2 Window Sizes
```
Default:  1100x750
Minimum:  900x600
Maximum:  Fullscreen
Charts:   1200x800 (optimal for matplotlib)
```

### 3.3 Scaling Rules
```
< 1000px width  → Sidebar collapses to icons only
< 800px width   → Stack charts vertically
< 600px height  → Hide activity feed
High DPI (>150%) → Scale all widgets 1.5x
```

---

## 4. ANIMATION & FEEDBACK

### 4.1 Loading States
```
Button click    → Slight opacity dim (0.8)
Data loading    → Spinner or "Loading..." text
Chart refresh   → Fade transition (0.3s)
Batch send      → Progress bar animation
```

### 4.2 Success/Error Feedback
```
Success: Green checkmark flash (0.5s) + status text
Error:   Red shake animation + error message
Warning: Orange border pulse + tooltip
Info:    Cyan dot indicator
```

---

## 5. CHART SPECIFICATIONS (v4.3)

### 5.1 KPI Cards
```
Size:     Equal width, 85px height
Border:   Top color bar (3px, sequence color)
Layout:   Title (top) + Value (center, large)
Colors:   School=#59ced9, CSR=#febe32, Total=#34c759, Rate=#6d45a5
Font:     Value=22px Bold, Title=9px Regular
Spacing:  8px gap between cards
```

### 5.2 Send Trends (Area Chart)
```
Type:     Matplotlib AreaChart
X-axis:   Dates (last 14 days)
Y-axis:   Email count
Series:   School (cyan fill + line), CSR (gold fill + line)
Fill:     25% opacity
Markers:  Circle, size 3
Grid:     Dashed, #2a2a4e, 20% opacity
Legend:   Upper-left, panel background
```

### 5.3 Sentiment Pie
```
Type:     Matplotlib PieChart
Colors:   Positive=#34c759, Neutral=#8B949E, Hostile=#ff3b30, Unknown=#6d45a5
Labels:   Sentiment name + percentage
Start:    140 degrees
Empty:    "No reply data" text centered
```

### 5.4 Sequence Comparison (Bar Chart)
```
Type:     Matplotlib Grouped Bar
X-axis:   SCHOOL, CSR
Groups:   Sent (cyan), Replied (green), Bounced (red)
Width:    0.25 per bar, grouped
Grid:     Horizontal only, 20% opacity
```

### 5.5 Activity Feed
```
Height:   Scrollable, max 20 items
Row:      26px height
Content:  Status dot + Day badge + Sequence + Email + Status pill
Colors:   Sent=green, Replied=cyan, Bounced=red
Scroll:   Customtkinter scrollbar
```

---

## 6. ICONOGRAPHY

| Icon | Unicode | Usage |
|------|---------|-------|
| 🤖 | U+1F916 | Raj avatar |
| 👤 | U+1F464 | User avatar |
| 📊 | U+1F4CA | Dashboard, Charts |
| 💬 | U+1F4AC | Chat |
| 📁 | U+1F4C1 | Import |
| 📝 | U+1F4DD | Templates |
| 🚀 | U+1F680 | Batches |
| 💌 | U+1F48C | Replies |
| 🚫 | U+1F6AB | Blacklist |
| ⚙ | U+2699 | Settings |
| 🔄 | U+1F504 | Refresh |
| ✅ | U+2705 | Success |
| ❌ | U+274C | Error |
| 🏴‍☠ | U+1F3F4 | RoboPirate logo |

---

## 7. ACCESSIBILITY

### 7.1 Keyboard Shortcuts
```
Ctrl+Space  → Launch Raj (via AutoHotkey)
Ctrl+R      → Refresh current view
Ctrl+S      → Save settings
Ctrl+Q      → Quit application
Tab         → Navigate between controls
Enter       → Activate focused button
```

### 7.2 Color Contrast
```
All text meets WCAG AA (4.5:1 ratio)
Status colors have text labels (not color-only)
Focus indicators visible on all interactive elements
```

---

**Document Owner:** Om (RoboPirate)
**Last Updated:** 2026-06-03
**Status:** APPROVED
