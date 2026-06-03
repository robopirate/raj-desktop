═══════════════════════════════════════════════════════════════════
  RAJ v4.4 -- CLAYMORPHISM UI UPGRADE
  Drop 1 file, add 3 lines. That's it.
═══════════════════════════════════════════════════════════════════

WHAT YOU GET:
─────────────
  - Soft 3D clay cards (no more flat dark boxes)
  - Pill-shaped buttons (rounded, soft colors)
  - Batch cards with progress bars (same on Dashboard + Batches)
  - KPI summary cards at top (Running, Scheduled, Completed)
  - Pipeline day cards (D1-D10 with visual progress)
  - Everything synced and matching

═══════════════════════════════════════════════════════════════════

STEP 1: Drop the file
─────────────────────
Copy raj_clay_ui.py into:
  C:\Users\itsom\OneDrive\Documents\GitHub\raj-desktop\

STEP 2: Open raj_chat.py
────────────────────────
Right-click raj_chat.py → Open with Notepad

STEP 3: Add the import
──────────────────────
Find this line (near the top, after other imports):
  C_TEXT_DIM = "#888888"

Add these lines RIGHT AFTER it:

  # === CLAYMORPHISM UI ===
  try:
      from raj_clay_ui import ClayUI, CLAY
      CLAY_AVAILABLE = True
  except ImportError:
      CLAY_AVAILABLE = False

STEP 4: Find the view builders
──────────────────────────────
Press Ctrl+F and search for:
  _build_batches_view

You'll find a line like:
  self._build_batches_view()

Replace that ENTIRE LINE with:

  if CLAY_AVAILABLE:
      ClayUI.build_clay_batches(self)
  else:
      self._build_batches_view()

STEP 5: Find dashboard builder
──────────────────────────────
Press Ctrl+F and search for:
  _build_dashboard_view

Replace that line with:

  if CLAY_AVAILABLE:
      ClayUI.build_clay_dashboard(self)
  else:
      self._build_dashboard_view()

STEP 6: Save + Push
───────────────────
Save (Ctrl+S)

GitHub Desktop → check "raj_clay_ui.py" → commit "Add claymorphism UI v4.4" → Push

═══════════════════════════════════════════════════════════════════

WHAT CHANGES:
─────────────

BEFORE (flat, ugly):
  ┌─────────────────────┐
  │ a-D10        DRAFT  │
  │ Sequence: SCHOOL     │
  │ Progress: 0/28 sent  │
  │ [Start] [Delete] [D]│  ← flat colored squares
  └─────────────────────┘

AFTER (claymorphism):
  ╭────────────────────────────────╮
  │ a-D10              ⏳ Scheduled │
  │  ● SCHOOL                      │
  │  0/28 sent              0%     │
  │  ░░░░░░░░░░░░░░░░░░░░░░░░░    │  ← progress bar
  │  ▶ Start  🗑 Delete  📋 Details│  ← pill buttons
  ╰────────────────────────────────╯

═══════════════════════════════════════════════════════════════════

STEP 7: Run
───────────
Double-click START.bat
Click Dashboard → see clay cards
Click Batches → see clay cards (same style!)
Click Charts → still works

═══════════════════════════════════════════════════════════════════
