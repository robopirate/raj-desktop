"""
raj_chat.py — Raj Command Center GUI v4.2
Dashboard, Batch Manager, Pipeline View, Individual Blacklist Removal
RESPONSIVE: Auto-adjusts to screen size, DPI aware, resize-friendly.
FIXED: Thread-safe dashboard refresh (v4.2.1)
"""

# --- DPI Awareness for Windows (laptop ↔ monitor) ---
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)  # Per-monitor DPI aware
except Exception:
    pass
# --- End DPI Awareness ---

import re
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import time
import json
import webbrowser
import tempfile
import queue
from analytics import AnalyticsView
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from smart_importer import SmartImporter
    SMART_IMPORT_AVAILABLE = True
except ImportError:
    SMART_IMPORT_AVAILABLE = False
import os
from datetime import datetime, timedelta

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

C_BG = "#0f0f1a"
C_PANEL = "#1a1a2e"
C_ACCENT = "#00d4ff"
C_WARNING = "#ff9500"
C_DANGER = "#ff3b30"
C_SUCCESS = "#34c759"
C_TEXT = "#e0e0e0"
C_TEXT_DIM = "#888888"

class RajChatApp(ctk.CTk):
    def __init__(self, engine, brain):
        super().__init__()
        self.engine = engine
        self.brain = brain
        self.title("Raj — RoboPirate Command Center v4.2")

        # Responsive sizing: fit to screen with padding
        try:
            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()
            # Use 85% of screen, but cap at 1600x1000 and min 1000x700
            win_w = min(int(screen_w * 0.85), 1600)
            win_h = min(int(screen_h * 0.85), 1000)
            win_w = max(win_w, 1000)
            win_h = max(win_h, 700)
            x = (screen_w - win_w) // 2
            y = (screen_h - win_h) // 2
            self.geometry(f"{win_w}x{win_h}+{x}+{y}")
        except Exception:
            self.geometry("1400x900")

        self.minsize(1000, 700)  # Minimum usable size
        self.configure(fg_color=C_BG)

        # Bind resize event
        self.bind("<Configure>", self._on_window_resize)

        # Ctrl+Space to close the app gracefully
        self.bind("<Control-space>", lambda e: self._graceful_exit())
        self.protocol("WM_DELETE_WINDOW", self._graceful_exit)

        self.template_cards = {}
        self.nav_buttons = {}
        self.views = {}
        self.batch_frames = {}
        self._expanded_families = {}      # family_name -> True/False
        self._expanded_family_day = {}    # family_name -> day_code (e.g. "D1")
        self._family_card_widgets = {}     # family_name -> card widget
        self._family_days_cache = {}       # family_name -> days dict
        self._family_expanded_frames = {}  # family_name -> expanded frame widget
        self._ui_queue = queue.Queue()     # thread-safe UI update queue
        self._family_toggle_buttons = {}   # family_name -> toggle button widget
        self._cached_scale = 1.0
        self._scale_cache_time = 0
        self._current_view = "dashboard"
        self._current_view = "dashboard"
        # In-place update caches — avoid full rebuilds
        self._batch_pill_cache = {}        # (family_name, day_code) -> widget refs dict

        self._build_ui()
        self._poll_ui_queue()
        self._start_refresh_loop()
        self._last_win_width = self.winfo_width()
        self._resize_debounce = None
        self._log_activity("Raj v4.2 RoboPirate Brand Theme initialized")

    # ═══════════════════════════════════════════════════════════
    # RESPONSIVE SCALING HELPERS
    # ═══════════════════════════════════════════════════════════
    def _get_scale(self):
        """Return a scale factor based on current window width.
        Cached for 5s to avoid thousands of winfo_width() calls per render."""
        now = time.time()
        if now - self._scale_cache_time < 5.0:
            return self._cached_scale
        try:
            w = self.winfo_width()
            if w < 500:
                w = self._last_win_width if self._last_win_width > 500 else 1400
            scale = w / 1400.0
            scale = max(0.75, min(1.35, scale))
            self._cached_scale = scale
            self._scale_cache_time = now
            return scale
        except Exception:
            return self._cached_scale

    def _sf(self, px):
        """Scale a pixel value by current window scale."""
        return int(round(px * self._get_scale()))

    def _font(self, size, bold=False):
        """Build a scaled Segoe UI font tuple."""
        s = max(7, int(round(size * self._get_scale())))
        return ("Segoe UI", s, "bold") if bold else ("Segoe UI", s)

    def _build_ui(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color=C_PANEL)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self.sidebar.grid_propagate(False)

        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=80)
        logo_frame.pack(fill="x", padx=16, pady=(16, 8))
        logo_frame.pack_propagate(False)

        # Robot face logo
        robot_label = ctk.CTkLabel(logo_frame, text="🤖", font=("Segoe UI", 32), text_color=C_ACCENT)
        robot_label.pack(side="left")

        name_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
        name_frame.pack(side="left", padx=(8, 0))
        ctk.CTkLabel(name_frame, text="RAJ", font=("Segoe UI", 24, "bold"), text_color=C_ACCENT).pack(anchor="w")
        ctk.CTkLabel(name_frame, text="by RoboPirate", font=("Segoe UI", 10), text_color=C_TEXT_DIM).pack(anchor="w")

        # Navigation
        nav_items = [
            ("📊 Dashboard", "dashboard"),
            ("📈 Analytics", "analytics"),
            ("📧 Chat", "chat"),
            ("📥 Import", "import"),
            ("📝 Templates", "templates"),
            ("🚀 Batches", "batches"),
            ("💬 Replies", "replies"),
            ("🚫 Blacklist", "blacklist"),
            ("⚙️ Settings", "settings"),
        ]
        for text, key in nav_items:
            btn = ctk.CTkButton(self.sidebar, text=text, font=("Segoe UI", 12),
                                fg_color="transparent", anchor="w",
                                command=lambda k=key: self._show_view(k))
            btn.pack(fill="x", padx=10, pady=3)
            self.nav_buttons[key] = btn

        # ─── Status Bar ───
        status_panel = ctk.CTkFrame(self.sidebar, fg_color=C_PANEL, corner_radius=8,
                                    border_width=1, border_color="#2a2a4e")
        status_panel.pack(side="bottom", fill="x", padx=10, pady=10)

        # Top divider line
        ctk.CTkFrame(status_panel, fg_color="#2a2a4e", height=1).pack(fill="x", padx=0, pady=0)

        inner = ctk.CTkFrame(status_panel, fg_color="transparent")
        inner.pack(fill="x", padx=8, pady=8)

        # Left: status indicator
        self.status_dot = ctk.CTkLabel(inner, text="●", font=("Segoe UI", 16),
                                       text_color=C_SUCCESS)
        self.status_dot.pack(side="left")
        self.status_text = ctk.CTkLabel(inner, text="Running",
                                          font=("Segoe UI", 10, "bold"), text_color=C_SUCCESS)
        self.status_text.pack(side="left", padx=(4, 0))

        # Right: compact action icons
        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(side="right")

        self.btn_pause = ctk.CTkButton(btn_row, text="⏸", font=("Segoe UI", 10),
                                       width=28, height=28, corner_radius=6,
                                       fg_color=C_WARNING, hover_color="#cc7a00",
                                       command=self._pause_engine)
        self.btn_pause.pack(side="left", padx=(0, 4))

        self.btn_scan = ctk.CTkButton(btn_row, text="🔍", font=("Segoe UI", 10),
                                      width=28, height=28, corner_radius=6,
                                      fg_color=C_ACCENT, hover_color="#4ab8c4",
                                      command=self._scan_bounces_now)
        self.btn_scan.pack(side="left")

        # Content area
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        # Make main window responsive
        self.grid_columnconfigure(1, weight=1)  # content area expands
        self.grid_rowconfigure(0, weight=1)

        # Build all views
        self._build_dashboard_view()
        self._build_analytics_view()
        self._build_chat_view()
        self._build_import_view()
        self._build_templates_view()
        self._build_batches_view()
        self._build_replies_view()
        self._build_blacklist_view()
        self._build_settings_view()

        self._show_view("dashboard")

    # ═══════════════════════════════════════════════════════════
    # DASHBOARD VIEW
    # ═══════════════════════════════════════════════════════════
    def _build_dashboard_view(self):
        view = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        self.views["dashboard"] = view

        # Header
        ctk.CTkLabel(view, text="📊 Dashboard", font=self._font(28, bold=True),
                     text_color="white").pack(anchor="w", pady=(0, self._sf(20)))

        # Pipeline Overview Cards
        cards_frame = ctk.CTkFrame(view, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, self._sf(20)))
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.dashboard_cards = {}
        sequences = [("school", "SCHOOL", C_ACCENT), ("csr", "CSR", C_WARNING), ("csr-wsl-5", "CSR-WSL-5", C_WARNING),
                     ("leads", "GENERIC LEADS", C_TEXT_DIM), ("total", "TOTAL", C_SUCCESS), ("blacklist", "BLACKLIST", C_DANGER)]

        for col, (seq_id, label, color) in enumerate(sequences):
            card = ctk.CTkFrame(cards_frame, fg_color=C_PANEL, corner_radius=self._sf(12))
            card.grid(row=0, column=col, padx=self._sf(8), pady=self._sf(5), sticky="nsew")

            ctk.CTkLabel(card, text=label, font=self._font(14, bold=True),
                         text_color=color).pack(pady=(self._sf(15), self._sf(5)))

            stats = ctk.CTkFrame(card, fg_color="transparent")
            stats.pack(pady=(0, self._sf(15)))

            self.dashboard_cards[seq_id] = {}
            for metric in ["leads", "sent", "replied", "bounced", "pool"]:
                lbl = ctk.CTkLabel(stats, text=f"{metric.capitalize()}: 0",
                                   font=self._font(11), text_color=C_TEXT)
                lbl.pack(anchor="w", padx=self._sf(15))
                self.dashboard_cards[seq_id][metric] = lbl

        # Day-wise Pipeline
        ctk.CTkLabel(view, text="📅 Day-wise Pipeline", font=self._font(20, bold=True),
                     text_color="white").pack(anchor="w", pady=(self._sf(20), self._sf(10)))

        self.pipeline_table = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=self._sf(8))
        self.pipeline_table.pack(fill="x", pady=(0, self._sf(20)))

        # Headers
        headers = ["Day", "Total", "Sent", "Bounced", "Replied", "Status"]
        for col, h in enumerate(headers):
            ctk.CTkLabel(self.pipeline_table, text=h, font=self._font(11, bold=True),
                         text_color=C_ACCENT).grid(row=0, column=col, padx=self._sf(15), pady=self._sf(8))

        self.pipeline_rows = {}
        for row, day in enumerate([1, 3, 5, 7, 10], start=1):
            self.pipeline_rows[day] = {}
            for col, h in enumerate(headers):
                lbl = ctk.CTkLabel(self.pipeline_table, text="-" if col > 0 else f"Day {day}",
                                   font=self._font(10), text_color=C_TEXT)
                lbl.grid(row=row, column=col, padx=self._sf(15), pady=self._sf(5))
                self.pipeline_rows[day][h.lower()] = lbl

        # Active Batches
        ctk.CTkLabel(view, text="🚀 Active Batches", font=self._font(20, bold=True),
                     text_color="white").pack(anchor="w", pady=(self._sf(20), self._sf(10)))

        self.batches_frame = ctk.CTkFrame(view, fg_color="transparent")
        self.batches_frame.pack(fill="x", pady=(0, self._sf(20)))

    def _safe_after(self, delay, callback):
        """Thread-safe replacement for self.after(). Uses internal queue."""
        self._ui_queue.put((delay, callback))

    def _poll_ui_queue(self):
        """Poll UI queue from main thread. Call once at startup."""
        if not self.winfo_exists():
            return
        try:
            while True:
                delay, callback = self._ui_queue.get_nowait()
                self.after(delay, callback)
        except queue.Empty:
            pass
        self.after(50, self._poll_ui_queue)

    def _run_bg(self, task, on_ok, on_err):
        """Run task in background thread, then call on_ok/on_err on main thread."""
        q = queue.Queue()
        def _fetch():
            try:
                result = task()
                q.put(("ok", result))
            except Exception as e:
                q.put(("err", str(e)))
        def _poll():
            if not self.winfo_exists():
                return
            try:
                status, payload = q.get_nowait()
                if status == "ok":
                    on_ok(payload)
                else:
                    on_err(payload)
            except queue.Empty:
                self.after(100, _poll)
        threading.Thread(target=_fetch, daemon=True).start()
        _poll()

    def _refresh_dashboard(self):
        """Refresh all dashboard data — cards, day table, active batches.
        DB query runs in background thread so UI never blocks."""
        self._run_bg(
            lambda: self.engine.get_summary(),
            self._update_dashboard_ui,
            lambda msg: print(f"Dashboard fetch error: {msg}")
        )

    def _update_dashboard_ui(self, summary):
        """Apply summary data to dashboard widgets (must run on main thread)."""
        try:
            # ─── Overview Cards ───
            totals = {"leads": 0, "sent": 0, "replied": 0, "bounced": 0, "pool": 0}

            for seq_id in ["school", "csr", "csr-wsl-5", "leads"]:
                seq_data = summary.get("sequences", {}).get(seq_id, {})
                pipeline = seq_data.get("pipeline", {})
                pool_count = seq_data.get("pool_count", 0)

                totals["leads"] += pipeline.get("total", 0)
                totals["sent"] += pipeline.get("sent", 0)
                totals["replied"] += pipeline.get("replied", 0)
                totals["bounced"] += pipeline.get("bounced", 0)
                totals["pool"] += pool_count

                if seq_id in self.dashboard_cards:
                    self.dashboard_cards[seq_id]["leads"].configure(
                        text=f"Leads: {pipeline.get('total', 0)}", text_color="white")
                    self.dashboard_cards[seq_id]["sent"].configure(
                        text=f"Sent: {pipeline.get('sent', 0)}", text_color="white")
                    self.dashboard_cards[seq_id]["replied"].configure(
                        text=f"Replied: {pipeline.get('replied', 0)}", text_color="white")
                    self.dashboard_cards[seq_id]["bounced"].configure(
                        text=f"Bounced: {pipeline.get('bounced', 0)}", text_color="white")
                    if "pool" in self.dashboard_cards[seq_id]:
                        self.dashboard_cards[seq_id]["pool"].configure(
                            text=f"Pool: {pool_count}", text_color="white")

            # TOTAL card
            if "total" in self.dashboard_cards:
                self.dashboard_cards["total"]["leads"].configure(text=f"Leads: {totals['leads']}", text_color="white")
                self.dashboard_cards["total"]["sent"].configure(text=f"Sent: {totals['sent']}", text_color="white")
                self.dashboard_cards["total"]["replied"].configure(text=f"Replied: {totals['replied']}", text_color="white")
                self.dashboard_cards["total"]["bounced"].configure(text=f"Bounced: {totals['bounced']}", text_color="white")
                if "pool" in self.dashboard_cards["total"]:
                    self.dashboard_cards["total"]["pool"].configure(text=f"Pool: {totals['pool']}", text_color="white")

            # BLACKLIST card
            if "blacklist" in self.dashboard_cards:
                total_blacklist = summary.get("global", {}).get("blacklist_count", 0)
                self.dashboard_cards["blacklist"]["leads"].configure(text=f"Blocked: {total_blacklist}", text_color="white")

            # ─── Day-wise Pipeline Table (COMBINED SCHOOL + CSR + CSR-WSL-5) ───
            combined_day_wise = {}
            for seq_id in ["school", "csr", "csr-wsl-5"]:
                seq_data = summary.get("sequences", {}).get(seq_id, {})
                day_wise = seq_data.get("day_wise", {})
                for day, metrics in day_wise.items():
                    day = int(day)
                    if day not in combined_day_wise:
                        combined_day_wise[day] = {"total": 0, "sent": 0, "bounced": 0, "replied": 0}
                    combined_day_wise[day]["total"] += metrics.get("total", 0)
                    combined_day_wise[day]["sent"] += metrics.get("sent", 0)
                    combined_day_wise[day]["bounced"] += metrics.get("bounced", 0)
                    combined_day_wise[day]["replied"] += metrics.get("replied", 0)

            for day in [1, 3, 5, 7, 10]:
                if day in self.pipeline_rows:
                    metrics = combined_day_wise.get(day, {"total": 0, "sent": 0, "bounced": 0, "replied": 0})
                    self.pipeline_rows[day]["total"].configure(
                        text=str(metrics["total"]), text_color="white")
                    self.pipeline_rows[day]["sent"].configure(
                        text=str(metrics["sent"]), text_color=C_SUCCESS if metrics["sent"] > 0 else C_TEXT_DIM)
                    self.pipeline_rows[day]["bounced"].configure(
                        text=str(metrics["bounced"]), text_color=C_DANGER if metrics["bounced"] > 0 else C_TEXT_DIM)
                    self.pipeline_rows[day]["replied"].configure(
                        text=str(metrics["replied"]), text_color=C_ACCENT if metrics["replied"] > 0 else C_TEXT_DIM)

                    if metrics["total"] > 0 and metrics["sent"] >= metrics["total"]:
                        status_text = "✅ Done"
                        status_color = C_SUCCESS
                    elif metrics["sent"] > 0:
                        status_text = f"⏳ {metrics['sent']}/{metrics['total']}"
                        status_color = C_WARNING
                    else:
                        status_text = "⏳ Pending"
                        status_color = C_TEXT_DIM

                    self.pipeline_rows[day]["status"].configure(text=status_text, text_color=status_color)

            # ─── Active Batches (pipeline view) ───
            self._refresh_batch_list()

        except Exception as e:
            print(f"Dashboard UI update error: {e}")
            import traceback
            print(traceback.format_exc())

    def _refresh_dashboard_fonts(self):
        """Re-apply scaled fonts to dashboard static labels on resize."""
        try:
            scale = self._get_scale()
            # Overview card labels
            for seq_id in ["school", "csr", "csr-wsl-5", "total", "blacklist"]:
                if seq_id in self.dashboard_cards:
                    for metric, lbl in self.dashboard_cards[seq_id].items():
                        lbl.configure(font=self._font(11))
            # Pipeline table headers
            for h in ["Day", "Total", "Sent", "Bounced", "Replied", "Status"]:
                for day in [1, 3, 5, 7, 10]:
                    if h.lower() in self.pipeline_rows[day]:
                        self.pipeline_rows[day][h.lower()].configure(font=self._font(10, bold=(h=="Day")))
        except Exception:
            pass

    def _refresh_batch_list(self):
        """Refresh active batches — show pipeline rows for all batches."""
        for widget in self.batches_frame.winfo_children():
            widget.destroy()

        def _fetch():
            batches = self.engine.db.batch_get_all()
            if not batches:
                return None

            from collections import defaultdict
            groups = defaultdict(list)
            for b in batches:
                gn = self._extract_batch_group(b.get("name", str(b["id"])))
                groups[gn].append(b)

            families = {}
            for gn, batch_list in groups.items():
                families[gn] = self._deduplicate_batches_by_day(batch_list)

            running_families = {
                name: days for name, days in families.items()
                if any(
                    b and isinstance(b, dict) and str(b.get("status", "")).strip().upper() == "RUNNING"
                    for b in days.values()
                )
            }

            def _due_date(item):
                name, days = item
                dates = []
                for d in ["D1", "D3", "D5", "D7", "D10"]:
                    b = days.get(d)
                    if b and isinstance(b, dict) and b.get("scheduled_at"):
                        try:
                            dt = datetime.fromisoformat(b["scheduled_at"].replace("Z", "+00:00"))
                            dates.append(dt)
                        except:
                            pass
                return min(dates) if dates else datetime.max

            return sorted(running_families.items(), key=_due_date)

        self._run_bg(_fetch, self._build_batch_list_ui, self._show_batch_list_error)

    def _build_batch_list_ui(self, sorted_families):
        for widget in self.batches_frame.winfo_children():
            widget.destroy()
        if sorted_families is None:
            ctk.CTkLabel(self.batches_frame, text="No batches yet. Create one in Batches tab.",
                         font=("Segoe UI", 12), text_color=C_TEXT_DIM).pack(pady=30)
            return
        if not sorted_families:
            ctk.CTkLabel(self.batches_frame, text="No batches currently sending",
                         font=("Segoe UI", 12), text_color=C_TEXT_DIM).pack(pady=30)
            return
        for family_name, days in sorted_families:
            self._render_pipeline_card(family_name, days)

    def _show_batch_list_error(self, msg):
        for widget in self.batches_frame.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self.batches_frame, text=f"Error: {msg}", text_color=C_DANGER).pack(pady=20)

    def _group_batches_into_families(self, batches):
        """Group batches by family. Tries parent_batch_id first, falls back to name matching."""
        families = {}
        batch_map = {b["id"]: b for b in batches}
        assigned = set()

        # PASS 1: Group by parent_batch_id chain
        for b in batches:
            if b["id"] in assigned:
                continue

            root = b
            visited = set()
            while root.get("parent_batch_id") and root["parent_batch_id"] in batch_map:
                if root["id"] in visited:
                    break
                visited.add(root["id"])
                root = batch_map[root["parent_batch_id"]]

            family_name = self._extract_family_name(root.get("name", str(root["id"])))

            if family_name not in families:
                families[family_name] = {"D1": None, "D3": None, "D5": None, "D7": None, "D10": None}

            def add_to_family(batch_id, family_dict):
                if batch_id not in batch_map or batch_id in assigned:
                    return
                batch = batch_map[batch_id]
                assigned.add(batch_id)
                day = self._extract_day_from_name(batch.get("name", ""))
                # Place in preferred day slot, or first empty slot — never overwrite
                if family_dict.get(day) is None:
                    family_dict[day] = batch
                else:
                    for d in ["D1", "D3", "D5", "D7", "D10"]:
                        if family_dict.get(d) is None:
                            family_dict[d] = batch
                            break
                for child in batches:
                    if child.get("parent_batch_id") == batch_id and child["id"] not in assigned:
                        add_to_family(child["id"], family_dict)

            add_to_family(root["id"], families[family_name])
            if b["id"] not in assigned:
                add_to_family(b["id"], families[family_name])

        # PASS 2: Group remaining unassigned batches by name similarity
        remaining = [b for b in batches if b["id"] not in assigned]
        for b in remaining:
            family_name = self._extract_family_name(b.get("name", str(b["id"])))
            if family_name not in families:
                families[family_name] = {"D1": None, "D3": None, "D5": None, "D7": None, "D10": None}
            day = self._extract_day_from_name(b.get("name", ""))
            placed = False
            if families[family_name].get(day) is None:
                families[family_name][day] = b
                placed = True
            else:
                for d in ["D1", "D3", "D5", "D7", "D10"]:
                    if families[family_name].get(d) is None:
                        families[family_name][d] = b
                        placed = True
                        break
            if not placed:
                # Overflow family when all day slots are full
                overflow_num = 2
                while f"{family_name} #{overflow_num}" in families:
                    overflow_num += 1
                overflow_name = f"{family_name} #{overflow_num}"
                families[overflow_name] = {"D1": None, "D3": None, "D5": None, "D7": None, "D10": None}
                families[overflow_name][day] = b
            assigned.add(b["id"])

        return families

    def _extract_family_name(self, batch_name):
        """Extract family name from batch name. Handles all patterns."""
        if not batch_name:
            return "Unknown"

        name = batch_name.strip()

        # Pattern 1: Remove -D suffix (Day suffix like -D3, -D5)
        name = re.sub(r'[-_]D\d+$', '', name, flags=re.IGNORECASE)

        # Pattern 2: Remove -B suffix (Batch suffix like -B1, -B2)
        name = re.sub(r'[-_]B\d+$', '', name, flags=re.IGNORECASE)

        # Pattern 3: Remove trailing numbers
        name = re.sub(r'\s*\d+$', '', name)

        return name.strip() or "Unknown"

    def _extract_batch_group(self, batch_name):
        """Extract batch group name — keeps B-suffix, removes only day suffix.
        e.g. Master_Lead-B1-D3 → Master_Lead-B1
             Pune_Email_ B1-B2-D5 → Pune_Email_ B1-B2
             a-D5 → a
             CSR-B1-D3 → CSR-B1
        """
        if not batch_name:
            return "Unknown"
        name = batch_name.strip()
        # Remove only the day suffix (-D1, -D3, -D5, -D7, -D10)
        name = re.sub(r'[-_]D\d+$', '', name, flags=re.IGNORECASE)
        return name.strip() or "Unknown"

    def _deduplicate_batches_by_day(self, batch_list):
        """Keep only the best batch per day within a group.
        Priority: RUNNING > SCHEDULED > DRAFT > PAUSED > COMPLETED.
        Tie-breaker: highest ID (most recently created).
        Returns dict: {'D1': batch, 'D3': batch, ...}
        """
        day_map = {1: "D1", 3: "D3", 5: "D5", 7: "D7", 10: "D10"}
        status_priority = {"RUNNING": 5, "SCHEDULED": 4, "DRAFT": 3, "PAUSED": 2, "COMPLETED": 1}
        buckets = {}

        for b in batch_list:
            day_offset = b.get("day_offset", 1)
            day_code = day_map.get(day_offset, "D1")
            if day_code not in buckets:
                buckets[day_code] = []
            buckets[day_code].append(b)

        result = {"D1": None, "D3": None, "D5": None, "D7": None, "D10": None}
        for day_code, bs in buckets.items():
            if not bs:
                continue
            def sort_key(b):
                st = str(b.get("status", "")).strip().upper()
                return (status_priority.get(st, 0), b.get("id", 0))
            best = max(bs, key=sort_key)
            result[day_code] = best
        return result

    def _extract_day_from_name(self, batch_name):
        """Extract day code from batch name."""
        if not batch_name:
            return "D1"

        # Look for -D first (explicit day)
        m = re.search(r'[-_]D(\d+)', batch_name, re.IGNORECASE)
        if m:
            dn = m.group(1)
            if dn in ["1", "3", "5", "7", "10"]:
                return f"D{dn}"

        # Look for -B — B1=Day1, B2=Day1 (second batch), B3=Day3, etc.
        m = re.search(r'[-_]B(\d+)', batch_name, re.IGNORECASE)
        if m:
            bn = int(m.group(1))
            day_map = {1: 1, 2: 1, 3: 3, 4: 3, 5: 5, 6: 5, 7: 7, 8: 7, 9: 10, 10: 10}
            day = day_map.get(bn, 1)
            return f"D{day}"

        return "D1"

    def _render_pipeline_card(self, family_name, days):
        """Responsive symmetrical pipeline card. All 5 pills scale with window."""
        scale = self._get_scale()

        card = ctk.CTkFrame(self.batches_frame, fg_color=C_PANEL, corner_radius=self._sf(10),
                            border_width=1, border_color="#1e3a5f")
        card.pack(fill="x", pady=self._sf(6), padx=self._sf(6))

        # Header — same style as Batches tab, no expand button
        header_h = self._sf(36)
        header = ctk.CTkFrame(card, fg_color="transparent", height=header_h)
        header.pack(fill="x", padx=self._sf(14), pady=(self._sf(10), self._sf(4)))
        header.pack_propagate(False)

        seq_id = ""
        family_total = 0
        filled_days = 0
        for day_code in ["D1", "D3", "D5", "D7", "D10"]:
            b = days.get(day_code)
            if b and isinstance(b, dict):
                if not seq_id:
                    seq_id = b.get("sequence_id", "").upper()
                if family_total == 0:
                    try:
                        counts = self.engine.db.batch_count_by_status(b["id"])
                        family_total = sum(counts.values())
                    except:
                        pass
                # Only count as "filled" if all emails sent (COMPLETED)
                try:
                    counts = self.engine.db.batch_count_by_status(b["id"])
                    sent = counts.get("sent", 0)
                    total = sum(counts.values())
                    if sent >= total and total > 0:
                        filled_days += 1
                except:
                    pass

        name_color = C_ACCENT if seq_id == "SCHOOL" else C_WARNING if seq_id in ("CSR", "CSR-WSL-5") else "white"

        left_hdr = ctk.CTkFrame(header, fg_color="transparent")
        left_hdr.pack(side="left", fill="y")

        ctk.CTkLabel(left_hdr, text=family_name, font=self._font(15, bold=True),
                     text_color=name_color).pack(side="left")

        seq_badge_bg = "#0d3a4a" if seq_id == "SCHOOL" else "#4a3a0d" if seq_id in ("CSR", "CSR-WSL-5") else "#2a2a4e"
        ctk.CTkLabel(left_hdr, text=f"  {seq_id}  ", font=self._font(8, bold=True),
                     text_color=name_color, fg_color=seq_badge_bg,
                     corner_radius=self._sf(10)).pack(side="left", padx=(self._sf(8), 0))

        ctk.CTkLabel(left_hdr, text=f"  {filled_days}/5 days  •  {family_total} recipients",
                     font=self._font(10), text_color=C_TEXT_DIM).pack(side="left")

        # Overall progress: truly completed days out of 5
        if filled_days > 0:
            prog_pct = min(100, int(filled_days / 5 * 100))
            prog_frame = ctk.CTkFrame(header, fg_color="#1a1a2e", height=self._sf(6),
                                       corner_radius=self._sf(3), width=self._sf(120))
            prog_frame.pack(side="left", padx=(self._sf(14), 0))
            prog_frame.pack_propagate(False)
            if prog_pct > 0:
                fill_w = int(120 * scale * prog_pct / 100)
                ctk.CTkFrame(prog_frame, fg_color=C_SUCCESS, height=self._sf(6),
                             corner_radius=self._sf(3), width=fill_w).pack(side="left")
            ctk.CTkLabel(header, text=f" {prog_pct}%", font=self._font(9, bold=True),
                         text_color=C_SUCCESS if prog_pct == 100 else C_TEXT_DIM).pack(side="left")

        # Pills row - RESPONSIVE GRID
        pills_row = ctk.CTkFrame(card, fg_color="transparent")
        pills_row.pack(fill="x", padx=self._sf(6), pady=(self._sf(2), self._sf(8)))
        for i in range(5):
            pills_row.grid_columnconfigure(i, weight=1, uniform="pill")

        day_list = [("D1", 1, "D1"), ("D3", 3, "D3"), ("D5", 5, "D5"), ("D7", 7, "D7"), ("D10", 10, "D10")]

        for col, (day_code, day_num, day_label) in enumerate(day_list):
            batch = days.get(day_code)
            if batch and not isinstance(batch, dict):
                batch = None

            status = str(batch.get("status", "")).strip().upper() if batch else "NONE"
            batch_id = batch.get("id") if batch else None
            scheduled = batch.get("scheduled_at", "") if batch and batch.get("scheduled_at") else ""

            sent = 0
            total = family_total
            due = 0
            if batch:
                try:
                    counts = self.engine.db.batch_count_by_status(batch["id"])
                    sent = counts.get("sent", 0)
                    due = total - sent
                except:
                    pass
            else:
                due = total

            # FIX: If COMPLETED but not all sent, treat as DRAFT
            # FIX: If has scheduled_at and not completed/running, treat as SCHEDULED
            actual_status = status
            if status == "COMPLETED" and sent < total and total > 0:
                actual_status = "DRAFT"
            elif scheduled and actual_status not in ["COMPLETED", "RUNNING"]:
                actual_status = "SCHEDULED"

            # Colors — SCHEDULED = yellow, COMPLETED = green, RUNNING/DRAFT = teal
            if actual_status == "COMPLETED":
                bg, border, accent = "#0a3a2a", "#2ecc71", "#2ecc71"
            elif actual_status == "SCHEDULED":
                bg, border, accent = "#3a2a0d", "#febe32", "#febe32"
            elif actual_status in ["RUNNING", "DRAFT"]:
                bg, border, accent = "#0d2b2b", "#0d9b8a", "#0d9b8a"
            elif actual_status == "PAUSED":
                bg, border, accent = "#2a2a1a", "#d29922", "#d29922"
            else:
                bg, border, accent = "#151528", "#2a2a4e", "#555577"

            # RESPONSIVE pill
            pill_h = self._sf(155)
            pill = ctk.CTkFrame(pills_row, fg_color=bg, corner_radius=self._sf(6),
                                border_width=1, border_color=border, height=pill_h)
            pill.grid(row=0, column=col, padx=self._sf(3), pady=self._sf(2), sticky="nsew")
            pill.grid_propagate(False)

            # Day label + date on SAME LINE
            day_frame_h = self._sf(16)
            day_frame = ctk.CTkFrame(pill, fg_color="transparent", height=day_frame_h)
            day_frame.pack(fill="x", padx=self._sf(6), pady=(self._sf(4), 0))
            day_frame.pack_propagate(False)

            ctk.CTkLabel(day_frame, text=day_label, font=self._font(8, bold=True),
                         text_color=accent).pack(side="left")

            # Date beside day label
            date_text = ""
            if scheduled:
                try:
                    # ISO format (handles 2026-06-05T10:00:00)
                    dt = datetime.fromisoformat(scheduled.replace("Z", "+00:00"))
                    date_text = dt.strftime("%d %b")
                except Exception:
                    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S.%f",
                                "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"]:
                        try:
                            dt = datetime.strptime(scheduled, fmt)
                            date_text = dt.strftime("%d %b")
                            break
                        except ValueError:
                            continue
            elif status in ["NONE", "NOT_CREATED"]:
                date_text = "Not scheduled"
            else:
                # Existing batch without scheduled_at — don't project from today
                date_text = ""
            if date_text:
                color = "#484f58" if status == "NOT_CREATED" else "#4a5a6a"
                ctk.CTkLabel(day_frame, text=f" {date_text}", font=self._font(7),
                             text_color=color).pack(side="left")

            ctk.CTkLabel(pill, text=f"{sent}/{total}", font=self._font(13, bold=True),
                         text_color="white").pack(anchor="w", padx=self._sf(6), pady=(0, 0))

            # Status line (due count)
            if actual_status == "COMPLETED":
                st_text, st_color = "All sent", "#0d9b8a"
            elif due > 0 and actual_status not in ["NONE"]:
                st_text, st_color = f"{due} due", "#febe32"
            elif actual_status == "NONE" and family_total > 0:
                st_text, st_color = f"{family_total} to send", "#febe32"
            else:
                st_text, st_color = "", C_TEXT_DIM
            if st_text:
                ctk.CTkLabel(pill, text=st_text, font=self._font(8),
                             text_color=st_color).pack(anchor="w", padx=self._sf(6), pady=(0, 0))

            # State label
            states = {"COMPLETED": "Done", "RUNNING": "Sending", "SCHEDULED": "Scheduled",
                      "DRAFT": "Ready", "PAUSED": "Paused", "NONE": "Queue"}
            state_color = C_SUCCESS if actual_status == "COMPLETED" else "#5a6a7a"
            ctk.CTkLabel(pill, text=states.get(actual_status, ""), font=self._font(7),
                         text_color=state_color).pack(anchor="w", padx=self._sf(6), pady=(0, 0))

            # Buttons - fixed at bottom
            btn_h = self._sf(20)
            btn_frame = ctk.CTkFrame(pill, fg_color="transparent", height=btn_h)
            btn_frame.pack(fill="x", padx=self._sf(3), pady=(self._sf(2), self._sf(4)))
            btn_frame.grid_columnconfigure(0, weight=1)
            btn_frame.grid_columnconfigure(1, weight=1)
            btn_frame.pack_propagate(False)

            # FIX: COMPLETED and NOT_CREATED show no action button
            if actual_status in ["COMPLETED", "NOT_CREATED"]:
                action_text = None
            elif actual_status in ["DRAFT", "SCHEDULED", "PAUSED"]:
                action_text, action_color = "▶", "#0d9b8a"
            elif actual_status == "RUNNING":
                action_text, action_color = "⏸", "#d29922"
            else:
                action_text, action_color = "▶", "#3a3a5e"

            if action_text:
                ctk.CTkButton(btn_frame, text=action_text, font=self._font(8, bold=True),
                              fg_color=action_color, hover_color=action_color,
                              text_color="white", corner_radius=self._sf(3), height=btn_h,
                              command=lambda b=batch_id, s=actual_status, d=day_num, f=family_name, sq=seq_id: self._on_pill_click(b, s, d, f, sq)
                              ).grid(row=0, column=0, padx=(0, 1), sticky="nsew")
            else:
                ctk.CTkFrame(btn_frame, fg_color="transparent", height=btn_h).grid(row=0, column=0, padx=(0, 1), sticky="nsew")

            ctk.CTkButton(btn_frame, text="📊", font=self._font(7),
                          fg_color="#1a1a3e", hover_color="#2a2a5e",
                          text_color="white", corner_radius=self._sf(3), height=btn_h,
                          command=lambda b=batch_id, f=family_name, d=day_num: self._show_pill_report(b, f, d)
                          ).grid(row=0, column=1, padx=(1, 0), sticky="nsew")

            if batch_id:
                pill.bind("<Button-1>", lambda e, b=batch_id: self._show_batch_details(b))

    def _on_pill_click(self, batch_id, status, day_num, family_name, seq_id):
        """Handle click on active pill button — start batch or create if missing."""
        if batch_id:
            if status in ["DRAFT", "SCHEDULED", "PAUSED"]:
                # Check if batch is unassigned
                try:
                    batch = self.engine.db.batch_get(batch_id)
                    if batch and batch.get("sequence_id") == "unassigned":
                        self._show_sequence_picker(batch_id, family_name)
                        return
                except:
                    pass
                self._start_batch(batch_id)
            elif status == "RUNNING":
                self._pause_batch(batch_id)
            else:
                self._show_batch_details(batch_id)
        else:
            self._create_day_batch(family_name, day_num, seq_id)

    def _show_sequence_picker(self, batch_id, batch_name):
        """Show dialog to pick sequence for unassigned batch."""
        popup = ctk.CTkToplevel(self)
        popup.title(f"Assign Sequence — {batch_name}")
        popup.geometry("400x250")
        popup.configure(fg_color=C_BG)
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(popup, text="🎯 Select Sequence", font=("Segoe UI", 18, "bold"),
                     text_color=C_ACCENT).pack(pady=(20, 5))
        ctk.CTkLabel(popup, text=f"Batch: {batch_name}", font=("Segoe UI", 12),
                     text_color=C_TEXT_DIM).pack()
        ctk.CTkLabel(popup, text="Choose which email sequence to use for this batch:",
                     font=("Segoe UI", 11), text_color=C_TEXT).pack(pady=(10, 15))

        seq_var = ctk.StringVar(value="csr-wsl-5")
        ctk.CTkOptionMenu(popup, values=["school", "csr", "csr-wsl-5"],
                          variable=seq_var, font=("Segoe UI", 12),
                          width=200).pack(pady=10)

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text="🚀 Launch", font=("Segoe UI", 12, "bold"),
                      fg_color=C_SUCCESS, hover_color="#2a8a4a",
                      command=lambda: [self._start_batch(batch_id, seq_var.get()), popup.destroy()]).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", font=("Segoe UI", 12, "bold"),
                      fg_color=C_PANEL, hover_color="#3a3a5e",
                      command=popup.destroy).pack(side="left", padx=5)

    def _show_pill_report(self, batch_id, family_name, day_num):
        """Show report popup for any pill."""
        popup = ctk.CTkToplevel(self)
        popup.title(f"Report: {family_name} - Day {day_num}")
        popup.geometry("500x400")
        popup.configure(fg_color=C_BG)
        ctk.CTkLabel(popup, text=f"📊 {family_name}", font=("Segoe UI", 18, "bold"), text_color=C_ACCENT).pack(pady=(20, 5))
        ctk.CTkLabel(popup, text=f"Day {day_num} Report", font=("Segoe UI", 14), text_color=C_TEXT_DIM).pack()
        if batch_id:
            try:
                batch = self.engine.db.get_batch(batch_id)
                counts = self.engine.db.batch_count_by_status(batch_id)
                stats_frame = ctk.CTkFrame(popup, fg_color=C_PANEL, corner_radius=12)
                stats_frame.pack(fill="x", padx=20, pady=15)
                for label, value in [("Total", sum(counts.values())), ("Sent", counts.get("sent", 0)),
                                      ("Pending", counts.get("pending", 0)), ("Bounced", counts.get("bounced", 0)),
                                      ("Replied", counts.get("replied", 0))]:
                    row = ctk.CTkFrame(stats_frame, fg_color="transparent")
                    row.pack(fill="x", padx=15, pady=4)
                    ctk.CTkLabel(row, text=label, font=("Segoe UI", 12), text_color=C_TEXT).pack(side="left")
                    ctk.CTkLabel(row, text=str(value), font=("Segoe UI", 12, "bold"), text_color="white").pack(side="right")
                status = batch.get("status", "Unknown") if batch else "Not created"
                ctk.CTkLabel(popup, text=f"Status: {status}", font=("Segoe UI", 12), text_color=C_ACCENT).pack(pady=10)
                scheduled = batch.get("scheduled_at", "") if batch else ""
                if scheduled:
                    ctk.CTkLabel(popup, text=f"Scheduled: {scheduled}", font=("Segoe UI", 11), text_color=C_TEXT_DIM).pack()
            except Exception as e:
                ctk.CTkLabel(popup, text=f"Error: {e}", text_color=C_DANGER).pack(pady=20)
        else:
            ctk.CTkLabel(popup, text="No batch created for this day yet.", font=("Segoe UI", 12), text_color=C_TEXT_DIM).pack(pady=30)
        ctk.CTkButton(popup, text="Close", font=("Segoe UI", 12, "bold"), fg_color=C_ACCENT,
                      hover_color="#0a8a7a", corner_radius=8, command=popup.destroy).pack(pady=20)

    def _create_day_batch(self, family_name, day_num, seq_id):
        """Create a new batch for a specific day in the family."""
        try:
            scheduled = (datetime.now() + timedelta(days=2)).replace(hour=10, minute=0, second=0)
            scheduled_str = scheduled.strftime("%Y-%m-%d %H:%M:%S")

            batch_name = f"{family_name}-D{day_num}"
            day1_batch = None
            batches = self.engine.db.batch_get_all()
            for b in batches:
                bn = b.get("name", "")
                # New naming: Family-D1 (e.g. Master_Lead-B2-D1)
                if bn.startswith(family_name) and "-D1" in bn:
                    day1_batch = b
                    break
                # Old naming: Family is Day 1 itself (e.g. Master_Lead-B2)
                if bn == family_name:
                    day1_batch = b
                    break

            if day1_batch:
                new_batch_id = self.engine.db.batch_create(
                    name=batch_name,
                    sequence_id=seq_id.lower(),
                    scheduled_at=scheduled_str
                )
                recipients = self.engine.db.batch_get_recipients(day1_batch["id"])
                for r in recipients:
                    self.engine.db.batch_add_recipient(new_batch_id, r["id"])

                self._log_activity(f"Created {batch_name} from {day1_batch['name']}")
                # Full rebuild only on batches tab when explicitly needed
                self._refresh_all_batches()
                self._refresh_dashboard()
            else:
                self._log_activity(f"Cannot create {batch_name}: No Day 1 batch found")
        except Exception as e:
            self._log_activity(f"Error creating day batch: {e}")

    def _start_batch(self, batch_id, sequence_id=None):
        """Start a batch. If sequence_id provided, assign it first."""
        try:
            if sequence_id:
                assign = self.engine.assign_sequence_to_batch(batch_id, sequence_id)
                if not assign.get("success"):
                    self._log_activity(f"Failed to assign sequence: {assign.get('error')}")
                    return
            self.engine.db.batch_update_status(batch_id, "running")
            self._log_activity(f"Started batch {batch_id}")
            self._refresh_batch_list()
        except Exception as e:
            self._log_activity(f"Error starting batch: {e}")

    def _pause_batch(self, batch_id):
        """Pause a batch."""
        try:
            self.engine.db.batch_update_status(batch_id, "paused")
            self._log_activity(f"Paused batch {batch_id}")
            # Only refresh dashboard; batches tab updates on next tab switch
            self._refresh_batch_list()
        except Exception as e:
            self._log_activity(f"Error pausing batch: {e}")

    def _show_batch_details(self, batch_id):
        """Show batch details popup."""
        popup = ctk.CTkToplevel(self)
        popup.title(f"Batch Details: {batch_id}")
        popup.geometry("600x500")
        popup.configure(fg_color=C_BG)

        try:
            batch = self.engine.db.batch_get(batch_id)
            if not batch:
                ctk.CTkLabel(popup, text="Batch not found", text_color=C_DANGER).pack(pady=20)
                return

            ctk.CTkLabel(popup, text=f"📦 {batch.get('name', 'Unknown')}",
                         font=("Segoe UI", 18, "bold"), text_color=C_ACCENT).pack(pady=(20, 5))
            ctk.CTkLabel(popup, text=f"Status: {batch.get('status', 'Unknown')}",
                         font=("Segoe UI", 12), text_color=C_TEXT_DIM).pack()

            counts = self.engine.db.batch_count_by_status(batch_id)
            stats_frame = ctk.CTkFrame(popup, fg_color=C_PANEL, corner_radius=12)
            stats_frame.pack(fill="x", padx=20, pady=15)

            for label, value in [("Total", sum(counts.values())), ("Sent", counts.get("sent", 0)),
                                  ("Pending", counts.get("pending", 0)), ("Skipped", counts.get("skipped", 0)),
                                  ("Bounced", counts.get("bounced", 0)), ("Replied", counts.get("replied", 0))]:
                row = ctk.CTkFrame(stats_frame, fg_color="transparent")
                row.pack(fill="x", padx=15, pady=4)
                ctk.CTkLabel(row, text=label, font=("Segoe UI", 12), text_color=C_TEXT).pack(side="left")
                ctk.CTkLabel(row, text=str(value), font=("Segoe UI", 12, "bold"), text_color="white").pack(side="right")

            # Recipient list with status colors
            ctk.CTkLabel(popup, text="Recipients", font=("Segoe UI", 14, "bold"), text_color="white").pack(pady=(10, 5))
            rec_frame = ctk.CTkScrollableFrame(popup, fg_color="transparent", height=200)
            rec_frame.pack(fill="both", expand=True, padx=20, pady=5)

            recipients = self.engine.db.batch_get_recipients(batch_id)
            for r in recipients:
                status = r.get("batch_status", "pending")
                color = C_SUCCESS if status == "sent" else C_DANGER if status == "bounced" else C_WARNING if status == "skipped" else C_TEXT_DIM
                row = ctk.CTkFrame(rec_frame, fg_color="transparent")
                row.pack(fill="x", pady=1)
                ctk.CTkLabel(row, text=f"● {r.get('name', 'Unknown')} ({r.get('email', 'N/A')})",
                             font=("Segoe UI", 10), text_color=color).pack(side="left")
                ctk.CTkLabel(row, text=status.upper(), font=("Segoe UI", 9), text_color=color).pack(side="right")

        except Exception as e:
            ctk.CTkLabel(popup, text=f"Error: {e}", text_color=C_DANGER).pack(pady=20)

        ctk.CTkButton(popup, text="Close", font=("Segoe UI", 12, "bold"), fg_color=C_ACCENT,
                      hover_color="#0a8a7a", corner_radius=8, command=popup.destroy).pack(pady=15)

    # ═══════════════════════════════════════════════════════════
    # THREAD-SAFE REFRESH LOOP (FIXED v4.2.1)
    # ═══════════════════════════════════════════════════════════
    def _start_refresh_loop(self):
        """Start background refresh loop — safety net only (5 min).
        Primary refresh is on user actions (tab switch, button clicks)."""
        self._refresh_lock = threading.Lock()

        def loop():
            while True:
                time.sleep(300)  # 5 minutes — safety net only
                try:
                    if not hasattr(self, 'views'):
                        continue
                    if self._refresh_lock.locked():
                        continue
                    view = getattr(self, '_current_view', 'dashboard')
                    if view == "dashboard" and "dashboard" in self.views:
                        self._safe_after(0, self._refresh_dashboard)
                    elif view == "batches" and "batches" in self.views:
                        self._safe_after(0, self._refresh_all_batches)
                except Exception:
                    pass

        t = threading.Thread(target=loop, daemon=True)
        t.start()

    # ═══════════════════════════════════════════════════════════
    # ANALYTICS VIEW
    # ═══════════════════════════════════════════════════════════
    def _build_analytics_view(self):
        view = ctk.CTkFrame(self.content, fg_color="transparent")
        self.views["analytics"] = view
        self.analytics_view = AnalyticsView(view, self.engine.db, self.engine)

    def _refresh_analytics(self):
        if hasattr(self, 'analytics_view'):
            self.analytics_view._refresh()

    # ═══════════════════════════════════════════════════════════
    # CHAT VIEW
    # ═══════════════════════════════════════════════════════════
    def _build_chat_view(self):
        view = ctk.CTkFrame(self.content, fg_color="transparent")
        self.views["chat"] = view

        ctk.CTkLabel(view, text="💬 Chat with Raj", font=("Segoe UI", 24, "bold"),
                     text_color="white").pack(anchor="w", pady=(0, 15))

        self.chat_output = ctk.CTkTextbox(view, fg_color=C_PANEL, text_color=C_TEXT,
                                          font=("Segoe UI", 12), wrap="word", height=350)
        self.chat_output.pack(fill="both", expand=True, pady=(0, 10))
        self.chat_output.configure(state="disabled")

        input_frame = ctk.CTkFrame(view, fg_color="transparent")
        input_frame.pack(fill="x", pady=(0, 10))
        input_frame.grid_columnconfigure(0, weight=1)

        self.chat_input = ctk.CTkEntry(input_frame, fg_color=C_PANEL, text_color=C_TEXT,
                                       font=("Segoe UI", 12), placeholder_text="Type a command...")
        self.chat_input.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkButton(input_frame, text="Send", font=("Segoe UI", 12, "bold"),
                      fg_color=C_ACCENT, hover_color="#0a8a7a", width=80,
                      command=self._send_chat).grid(row=0, column=1)

        self.chat_input.bind("<Return>", lambda e: self._send_chat())

    def _send_chat(self):
        text = self.chat_input.get().strip()
        if not text: return
        self.chat_input.delete(0, "end")
        self._append_chat(f"You: {text}")

        try:
            result = self.brain.process(text)
            self._append_chat(f"Raj: {result}")
        except Exception as e:
            self._append_chat(f"Raj: Error — {e}")

    def _append_chat(self, text):
        self.chat_output.configure(state="normal")
        self.chat_output.insert("end", f"{text}\n\n")
        self.chat_output.configure(state="disabled")
        self.chat_output.see("end")

    # ═══════════════════════════════════════════════════════════
    # IMPORT VIEW
    # ═══════════════════════════════════════════════════════════
    def _build_import_view(self):
        view = ctk.CTkFrame(self.content, fg_color="transparent")
        self.views["import"] = view

        ctk.CTkLabel(view, text="📥 Import Leads", font=("Segoe UI", 24, "bold"),
                     text_color="white").pack(anchor="w", pady=(0, 15))

        # --- Import Section ---
        import_card = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=10)
        import_card.pack(fill="x", pady=(0, 15))
        import_inner = ctk.CTkFrame(import_card, fg_color="transparent")
        import_inner.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(import_inner, text="📁 Import Leads", font=("Segoe UI", 16, "bold"),
                     text_color=C_ACCENT).pack(anchor="w", pady=(0, 10))

        # Sequence selector
        seq_frame = ctk.CTkFrame(import_inner, fg_color="transparent")
        seq_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(seq_frame, text="Import as:", font=("Segoe UI", 12), text_color=C_TEXT).pack(side="left")
        self.import_seq_var = ctk.StringVar(value="leads")
        ctk.CTkOptionMenu(seq_frame, values=["leads (generic pool)", "school", "csr", "csr-wsl-5"], variable=self.import_seq_var,
                          font=("Segoe UI", 12)).pack(side="left", padx=(10, 0))
        ctk.CTkLabel(seq_frame, text="→ Leads are generic, assign sequence at launch", font=("Segoe UI", 10), text_color=C_TEXT_DIM).pack(side="left", padx=(15, 0))

        # Sub-Pool selector
        subpool_frame = ctk.CTkFrame(import_inner, fg_color="transparent")
        subpool_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(subpool_frame, text="Sub-Pool Name:", font=("Segoe UI", 12), text_color=C_TEXT).pack(side="left")
        self.import_subpool_entry = ctk.CTkEntry(subpool_frame, font=("Segoe UI", 12), width=250, placeholder_text="e.g. Mumbai-Schools, Tier1-CSR (optional)")
        self.import_subpool_entry.pack(side="left", padx=(10, 0))

        # File selector
        file_frame = ctk.CTkFrame(import_inner, fg_color="transparent")
        file_frame.pack(fill="x", pady=(0, 10))
        self.import_file_label = ctk.CTkLabel(file_frame, text="No file selected",
                                               font=("Segoe UI", 11), text_color=C_TEXT_DIM)
        self.import_file_label.pack(side="left")
        ctk.CTkButton(file_frame, text="Browse", font=("Segoe UI", 11),
                      fg_color=C_ACCENT, command=self._browse_import_file).pack(side="left", padx=(10, 0))

        # Import button
        ctk.CTkButton(import_inner, text="Import to Pool", font=("Segoe UI", 14, "bold"),
                      fg_color=C_SUCCESS, hover_color="#2a8a4a", height=40,
                      command=self._do_import).pack(fill="x", pady=(10, 0))

        # --- Trial Send Section ---
        trial_card = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=10)
        trial_card.pack(fill="x", pady=(0, 15))
        trial_inner = ctk.CTkFrame(trial_card, fg_color="transparent")
        trial_inner.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(trial_inner, text="🧪 Trial Send", font=("Segoe UI", 16, "bold"),
                     text_color=C_WARNING).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(trial_inner, text="Send all 5 emails to a test address with 2-minute gaps",
                     font=("Segoe UI", 11), text_color=C_TEXT_DIM).pack(anchor="w", pady=(0, 10))

        # Trial sequence selector
        trial_seq_frame = ctk.CTkFrame(trial_inner, fg_color="transparent")
        trial_seq_frame.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(trial_seq_frame, text="Sequence:", font=("Segoe UI", 12), text_color=C_TEXT).pack(side="left")
        self.trial_seq_var = ctk.StringVar(value="csr-wsl-5")
        ctk.CTkOptionMenu(trial_seq_frame, values=["school", "csr", "csr-wsl-5"], variable=self.trial_seq_var,
                          font=("Segoe UI", 12)).pack(side="left", padx=(10, 0))

        # Email input
        email_frame = ctk.CTkFrame(trial_inner, fg_color="transparent")
        email_frame.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(email_frame, text="Email:", font=("Segoe UI", 12), text_color=C_TEXT).pack(side="left")
        self.trial_email_entry = ctk.CTkEntry(email_frame, font=("Segoe UI", 12), width=280,
                                               placeholder_text="test@example.com")
        self.trial_email_entry.pack(side="left", padx=(10, 0))

        # Name + Org (optional)
        name_frame = ctk.CTkFrame(trial_inner, fg_color="transparent")
        name_frame.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(name_frame, text="Name (opt):", font=("Segoe UI", 12), text_color=C_TEXT).pack(side="left")
        self.trial_name_entry = ctk.CTkEntry(name_frame, font=("Segoe UI", 12), width=150,
                                              placeholder_text="CSR Head")
        self.trial_name_entry.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(name_frame, text="Org (opt):", font=("Segoe UI", 12), text_color=C_TEXT).pack(side="left", padx=(15, 0))
        self.trial_org_entry = ctk.CTkEntry(name_frame, font=("Segoe UI", 12), width=150,
                                             placeholder_text="Company")
        self.trial_org_entry.pack(side="left", padx=(10, 0))

        # Send trial button
        ctk.CTkButton(trial_inner, text="🚀 Send Trial Sequence", font=("Segoe UI", 14, "bold"),
                      fg_color=C_WARNING, hover_color="#c46a00", height=40,
                      command=self._do_trial_send).pack(fill="x", pady=(10, 0))

        # --- Preview ---
        self.import_preview = ctk.CTkTextbox(view, fg_color=C_PANEL, text_color=C_TEXT,
                                             font=("Segoe UI", 11), wrap="word", height=200)
        self.import_preview.pack(fill="both", expand=True, pady=(10, 0))
        self.import_preview.configure(state="disabled")

        self.import_filepath = None

    def _do_trial_send(self):
        email = self.trial_email_entry.get().strip()
        if not email or "@" not in email:
            messagebox.showwarning("Invalid Email", "Please enter a valid email address")
            return
        seq_id = self.trial_seq_var.get()
        name = self.trial_name_entry.get().strip()
        org = self.trial_org_entry.get().strip()
        
        self._append_import_preview(f"🧪 Starting trial send: {seq_id.upper()} to {email}")
        self._append_import_preview("This will take ~10 minutes (5 emails × 2 min gaps)...")
        
        # Run in background thread so UI doesn't freeze
        def run_trial():
            try:
                result = self.engine.trial_send(email, seq_id, name, org)
                if result.get("success"):
                    sent = result.get("sent", 0)
                    total = result.get("total", 0)
                    self._safe_after(0, lambda: self._append_import_preview(f"✅ Trial complete: {sent}/{total} emails sent"))
                    for r in result.get("results", []):
                        status = "✅" if r["status"] == "sent" else "❌"
                        self._safe_after(0, lambda r=r, status=status: self._append_import_preview(f"  {status} Day {r['day']}: {r['status']}"))
                else:
                    self._safe_after(0, lambda: self._append_import_preview(f"❌ Trial failed: {result.get('error')}"))
            except Exception as e:
                self._safe_after(0, lambda: self._append_import_preview(f"❌ Trial error: {e}"))
        
        threading.Thread(target=run_trial, daemon=True).start()

    def _browse_import_file(self):
        path = filedialog.askopenfilename(filetypes=[("Excel/CSV", "*.xlsx *.csv *.xls")])
        if path:
            self.import_filepath = path
            self.import_file_label.configure(text=os.path.basename(path))

    def _do_import(self):
        if not self.import_filepath:
            messagebox.showwarning("No File", "Please select a file first")
            return
        seq_id = self.import_seq_var.get()
        # Map display text to actual sequence_id
        if seq_id == "leads (generic pool)":
            seq_id = "leads"
        sub_pool = self.import_subpool_entry.get().strip() or None
        try:
            result = self.engine.smart_import(self.import_filepath, seq_id, sub_pool=sub_pool)
            if result.get("success"):
                msg = f"Imported {result.get('imported', 0)} leads to {seq_id.upper()} pool"
                if result.get('sub_pool'):
                    msg += f" (sub-pool: {result['sub_pool']})"
                msg += f"\nSkipped: {result.get('skipped', 0)}"
                self._append_import_preview(msg)
                self._refresh_dashboard()
                if hasattr(self, '_refresh_pool_count'):
                    self._refresh_pool_count()
            else:
                self._append_import_preview(f"Error: {result.get('error', 'Unknown')}")
        except Exception as e:
            self._append_import_preview(f"Error: {e}")

    def _append_import_preview(self, text):
        self.import_preview.configure(state="normal")
        self.import_preview.insert("end", f"{text}\n\n")
        self.import_preview.configure(state="disabled")
        self.import_preview.see("end")

    # ═══════════════════════════════════════════════════════════
    # TEMPLATES VIEW
    # ═══════════════════════════════════════════════════════════
    def _build_templates_view(self):
        view = ctk.CTkFrame(self.content, fg_color="transparent")
        self.views["templates"] = view

        # Title
        ctk.CTkLabel(view, text="📝 Templates", font=self._font(24, bold=True),
                     text_color="white").pack(anchor="w", pady=(0, 15))

        # Bulk action buttons
        btn_frame = ctk.CTkFrame(view, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(btn_frame, text="🔄 Sync from Gmail", font=self._font(12),
                      fg_color=C_ACCENT, command=self._sync_templates).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_frame, text="🔒 Lock All", font=self._font(12),
                      fg_color=C_WARNING, command=self._lock_templates).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_frame, text="⚡ Generate Missing", font=self._font(12),
                      fg_color=C_SUCCESS, command=self._generate_missing).pack(side="left")

        # Full-width scrollable card grid (no preview panel)
        scroll = ctk.CTkScrollableFrame(view, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        self.template_grid = ctk.CTkFrame(scroll, fg_color="transparent")
        self.template_grid.pack(fill="both", expand=True)

        self._template_card_refs = {}  # (seq_id, day) -> widget dict
        self._template_full_data = {}  # (seq_id, day) -> full template dict

        self._refresh_templates()

    def _refresh_templates(self):
        self._template_card_refs.clear()
        self._template_full_data.clear()

        for widget in self.template_grid.winfo_children():
            widget.destroy()

        status = self.engine.get_template_status()
        all_templates = self.engine.get_templates()

        for seq_id, days in status.items():
            seq_color = C_ACCENT if seq_id == "school" else C_WARNING
            border_color = seq_color

            seq_frame = ctk.CTkFrame(self.template_grid, fg_color=C_PANEL, corner_radius=10,
                                     border_width=1, border_color="#2a2a4e")
            seq_frame.pack(fill="x", pady=self._sf(8), padx=self._sf(4))

            ctk.CTkLabel(seq_frame, text=seq_id.upper(), font=self._font(16, bold=True),
                         text_color=seq_color).pack(anchor="w", padx=self._sf(15),
                                                     pady=(self._sf(10), self._sf(5)))

            # Grid container: 5 equal columns for the 5 days
            cards_grid = ctk.CTkFrame(seq_frame, fg_color="transparent")
            cards_grid.pack(fill="x", padx=self._sf(10), pady=(0, self._sf(10)))
            for c in range(5):
                cards_grid.grid_columnconfigure(c, weight=1)

            col = 0
            for day, info in days.items():
                self._build_template_day_card(cards_grid, seq_id, day, info,
                                              all_templates.get(seq_id, {}).get(day),
                                              seq_color, border_color, col)
                col += 1

    def _build_template_day_card(self, parent, seq_id, day, info, full_tmpl,
                                 seq_color, border_color, col):
        exists = info["exists"]
        locked = info["locked"]
        subject = info.get("subject") or "No subject"
        source = info.get("source") or ""

        key = (seq_id, day)

        # Card frame — grid cell, no fixed width so it fills the column
        card = ctk.CTkFrame(parent, fg_color=C_BG, corner_radius=10,
                            border_width=1,
                            border_color=seq_color if exists else C_DANGER)
        card.grid(row=0, column=col, sticky="nsew", padx=self._sf(4), pady=self._sf(4))

        # Top: Day badge + lock icon
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=self._sf(8), pady=(self._sf(6), 0))

        badge_bg = seq_color if exists else C_DANGER
        badge = ctk.CTkLabel(top, text=f"Day {day}", font=self._font(10, bold=True),
                             text_color=C_BG if exists else "white",
                             fg_color=badge_bg, corner_radius=999)
        badge.pack(side="left")

        if locked:
            ctk.CTkLabel(top, text="🔒", font=self._font(11)).pack(side="right")

        # Subject preview
        display_subj = subject[:22] + "…" if len(subject) > 24 else subject
        subj_color = C_TEXT if exists else C_TEXT_DIM
        subj_lbl = ctk.CTkLabel(card, text=display_subj, font=self._font(9),
                                text_color=subj_color)
        subj_lbl.pack(anchor="w", padx=self._sf(8), pady=(self._sf(4), self._sf(2)))

        # Source hint
        if source and source != "unknown":
            src_lbl = ctk.CTkLabel(card, text=f"src: {source}", font=self._font(8),
                                   text_color=C_TEXT_DIM)
            src_lbl.pack(anchor="w", padx=self._sf(8))

        # Action buttons
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=self._sf(6), pady=(self._sf(4), self._sf(6)), side="bottom")

        # Preview button — opens directly in browser
        prev_btn = ctk.CTkButton(btn_row, text="👁", font=self._font(10),
                                 fg_color=C_PANEL, width=self._sf(30), height=self._sf(24),
                                 command=lambda s=seq_id, d=day: self._preview_template_in_browser(s, d))
        prev_btn.pack(side="left", padx=(0, self._sf(3)))

        # Lock / Unlock toggle
        if locked:
            lock_btn = ctk.CTkButton(btn_row, text="🔓", font=self._font(10),
                                     fg_color=C_WARNING, width=self._sf(30), height=self._sf(24),
                                     command=lambda s=seq_id, d=day: self._lock_single_template(s, d))
        else:
            lock_btn = ctk.CTkButton(btn_row, text="🔒", font=self._font(10),
                                     fg_color=C_SUCCESS, width=self._sf(30), height=self._sf(24),
                                     command=lambda s=seq_id, d=day: self._lock_single_template(s, d))
        lock_btn.pack(side="left", padx=(0, self._sf(3)))

        # Generate button (only if missing)
        gen_btn = None
        if not exists:
            gen_btn = ctk.CTkButton(btn_row, text="⚡", font=self._font(10),
                                    fg_color=C_ACCENT, width=self._sf(30), height=self._sf(24),
                                    command=lambda s=seq_id, d=day: self._generate_single_template(s, d))
            gen_btn.pack(side="left")

        # Store refs for in-place updates
        self._template_card_refs[key] = {
            "card": card,
            "badge": badge,
            "subject": subj_lbl,
            "lock_btn": lock_btn,
            "gen_btn": gen_btn,
            "exists": exists,
            "locked": locked,
        }
        if full_tmpl:
            self._template_full_data[key] = full_tmpl
        else:
            self._template_full_data[key] = None

    def _preview_template_in_browser(self, seq_id, day):
        """Open template HTML directly in default browser."""
        key = (seq_id, day)
        tmpl = self._template_full_data.get(key)
        if not tmpl:
            tmpl = self.engine.db.template_get(seq_id, day)
            if tmpl:
                self._template_full_data[key] = tmpl
        if not tmpl:
            self._log_activity(f"No template to preview for {seq_id.upper()} Day {day}")
            return
        html = tmpl.get("html_body", "")
        self._preview_html(html, title=f"{seq_id.upper()} Day {day}")

    def _lock_single_template(self, seq_id, day):
        key = (seq_id, day)
        refs = self._template_card_refs.get(key)
        if not refs:
            return

        currently_locked = refs["locked"]
        try:
            if currently_locked:
                self.engine.unlock_template(seq_id, day)
                self._log_activity(f"Unlocked {seq_id.upper()} Day {day}")
            else:
                self.engine.lock_template(seq_id, day)
                self._log_activity(f"Locked {seq_id.upper()} Day {day}")
        except Exception as e:
            self._log_activity(f"Lock error: {e}")
            return

        # In-place update: fetch fresh status
        tmpl = self.engine.db.template_get(seq_id, day)
        if tmpl:
            self._template_full_data[key] = tmpl

        # Refresh just this card
        self._refresh_single_template_card(seq_id, day)

    def _generate_single_template(self, seq_id, day):
        key = (seq_id, day)
        try:
            result = self.engine.generate_template(seq_id, day)
            if "error" in result:
                self._log_activity(f"Generate error: {result['error']}")
                return
            self.engine.db.template_put(seq_id, day, result["subject"], result["html_body"], source="generated")
            self._log_activity(f"Generated {seq_id.upper()} Day {day}")

            # Store full data
            self._template_full_data[key] = result
        except Exception as e:
            self._log_activity(f"Generate error: {e}")
            return

        # In-place update
        self._refresh_single_template_card(seq_id, day)

        # Auto-preview
        self._on_template_click(seq_id, day)

    def _refresh_single_template_card(self, seq_id, day):
        key = (seq_id, day)
        refs = self._template_card_refs.get(key)
        if not refs:
            return

        info = self.engine.get_template_status().get(seq_id, {}).get(day, {})
        exists = info.get("exists", False)
        locked = info.get("locked", False)
        subject = info.get("subject") or "No subject"
        source = info.get("source") or ""

        seq_color = C_ACCENT if seq_id == "school" else C_WARNING
        badge_bg = seq_color if exists else C_DANGER

        # Update badge
        refs["badge"].configure(text=f"Day {day}", fg_color=badge_bg,
                                text_color=C_BG if exists else "white")

        # Update border
        refs["card"].configure(border_color=seq_color if exists else C_DANGER)

        # Update subject
        display_subj = subject[:32] + "…" if len(subject) > 34 else subject
        subj_color = C_TEXT if exists else C_TEXT_DIM
        refs["subject"].configure(text=display_subj, text_color=subj_color)

        # Update lock button
        btn_parent = refs["lock_btn"].master
        refs["lock_btn"].destroy()
        if locked:
            new_lock = ctk.CTkButton(btn_parent, text="🔓", font=self._font(10),
                                     fg_color=C_WARNING, width=self._sf(36), height=self._sf(26),
                                     command=lambda s=seq_id, d=day: self._lock_single_template(s, d))
        else:
            new_lock = ctk.CTkButton(btn_parent, text="🔒", font=self._font(10),
                                     fg_color=C_SUCCESS, width=self._sf(36), height=self._sf(26),
                                     command=lambda s=seq_id, d=day: self._lock_single_template(s, d))
        new_lock.pack(side="left", padx=(0, self._sf(4)))
        refs["lock_btn"] = new_lock

        # Update generate button
        if not exists and refs.get("gen_btn") is None:
            gen_btn = ctk.CTkButton(btn_parent, text="⚡", font=self._font(10),
                                    fg_color=C_ACCENT, width=self._sf(36), height=self._sf(26),
                                    command=lambda s=seq_id, d=day: self._generate_single_template(s, d))
            gen_btn.pack(side="left")
            refs["gen_btn"] = gen_btn
        elif exists and refs.get("gen_btn"):
            refs["gen_btn"].destroy()
            refs["gen_btn"] = None

        refs["exists"] = exists
        refs["locked"] = locked

    def _sync_templates(self):
        result = self.engine.sync_templates()
        self._log_activity(f"Synced: {result['loaded']} loaded, {len(result['missing'])} missing")
        self._refresh_templates()

    def _lock_templates(self):
        result = self.engine.lock_templates()
        self._log_activity(f"Locked {result['locked']} templates")
        self._refresh_templates()

    def _generate_missing(self):
        result = self.engine.create_missing_drafts()
        self._log_activity(f"Generated {result['count']} missing templates")
        self._refresh_templates()

    # ═══════════════════════════════════════════════════════════
    # BATCHES VIEW
    # ═══════════════════════════════════════════════════════════
    def _refresh_source_pools(self):
        """Refresh the Pull From dropdown with available pools and their counts."""
        try:
            pools = []
            for seq_id in ["leads", "school", "csr", "csr-wsl-5"]:
                count = self.engine.get_pool_count(seq_id)
                if count > 0:
                    label = "Generic" if seq_id == "leads" else seq_id.upper()
                    pools.append(f"{label} ({count})")
            
            if not pools:
                pools = ["No pools available (0)"]
            
            self.batch_source_menu.configure(values=pools)
            # Extract the sequence_id from the first option
            if pools[0] != "No pools available (0)":
                self.batch_source.set(pools[0])
            self._refresh_sub_pools()
        except Exception as e:
            self.batch_source_menu.configure(values=[f"Error: {e}"])

    def _refresh_sub_pools(self):
        """Refresh the Sub-Pool dropdown based on selected source sequence."""
        try:
            seq_id = self._get_batch_source_seq()
            rows = self.engine.db.execute(
                "SELECT DISTINCT sub_pool FROM recipients WHERE sequence_id=? AND sub_pool != '' AND batched=0 ORDER BY sub_pool",
                (seq_id,)
            ).fetchall()
            options = ["(All)"] + [r[0] for r in rows]
            self.batch_sub_pool_menu.configure(values=options)
            self.batch_sub_pool.set("(All)")
        except Exception as e:
            self.batch_sub_pool_menu.configure(values=[f"Error: {e}"])

    def _get_batch_source_seq(self):
        """Extract sequence_id from the selected dropdown option."""
        selected = self.batch_source.get()
        if "Generic" in selected:
            return "leads"
        elif "SCHOOL" in selected or "school" in selected:
            return "school"
        elif "CSR-WSL-5" in selected or "csr-wsl-5" in selected:
            return "csr-wsl-5"
        elif "CSR" in selected:
            return "csr"
        return "leads"

    def _build_batches_view(self):
        view = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        self.views["batches"] = view

        ctk.CTkLabel(view, text="🚀 Batches", font=("Segoe UI", 24, "bold"),
                     text_color="white").pack(anchor="w", pady=(0, 15))

        # Create batch form
        form = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=10)
        form.pack(fill="x", pady=(0, 15))

        # Name
        name_row = ctk.CTkFrame(form, fg_color="transparent")
        name_row.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(name_row, text="Name:", font=("Segoe UI", 12), text_color=C_TEXT).pack(side="left")
        self.batch_name = ctk.CTkEntry(name_row, fg_color=C_BG, text_color=C_TEXT, font=("Segoe UI", 12))
        self.batch_name.pack(side="left", fill="x", expand=True, padx=(10, 0))

        # Pull From (pool source)
        source_row = ctk.CTkFrame(form, fg_color="transparent")
        source_row.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(source_row, text="Pull From:", font=("Segoe UI", 12), text_color=C_TEXT).pack(side="left")
        self.batch_source = ctk.StringVar(value="leads")
        self.batch_source_menu = ctk.CTkOptionMenu(source_row, values=["Loading..."], variable=self.batch_source,
                                                    font=("Segoe UI", 12), width=200,
                                                    command=lambda _: self._refresh_sub_pools())
        self.batch_source_menu.pack(side="left", padx=(10, 0))
        ctk.CTkButton(source_row, text="🔄 Refresh", font=("Segoe UI", 10), fg_color=C_PANEL, width=60, height=24,
                      command=lambda: self._refresh_source_pools()).pack(side="left", padx=(10, 0))

        # Sub-Pool
        subpool_row = ctk.CTkFrame(form, fg_color="transparent")
        subpool_row.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(subpool_row, text="Sub-Pool:", font=("Segoe UI", 12), text_color=C_TEXT).pack(side="left")
        self.batch_sub_pool = ctk.StringVar(value="(All)")
        self.batch_sub_pool_menu = ctk.CTkOptionMenu(subpool_row, values=["(All)"], variable=self.batch_sub_pool,
                                                      font=("Segoe UI", 12), width=200)
        self.batch_sub_pool_menu.pack(side="left", padx=(10, 0))

        # Size
        size_row = ctk.CTkFrame(form, fg_color="transparent")
        size_row.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(size_row, text="Size:", font=("Segoe UI", 12), text_color=C_TEXT).pack(side="left")
        self.batch_size = ctk.CTkEntry(size_row, fg_color=C_BG, text_color=C_TEXT, font=("Segoe UI", 12), width=80)
        self.batch_size.insert(0, "50")
        self.batch_size.pack(side="left", padx=(10, 0))

        # Day offset
        day_row = ctk.CTkFrame(form, fg_color="transparent")
        day_row.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(day_row, text="Day:", font=("Segoe UI", 12), text_color=C_TEXT).pack(side="left")
        self.batch_day = ctk.StringVar(value="1")
        ctk.CTkOptionMenu(day_row, values=["1", "3", "5", "7", "10"], variable=self.batch_day,
                          font=("Segoe UI", 12)).pack(side="left", padx=(10, 0))
        ctk.CTkLabel(day_row, text="→ Sequence is assigned at launch", font=("Segoe UI", 10), text_color=C_TEXT_DIM).pack(side="left", padx=(10, 0))

        # Schedule
        sched_row = ctk.CTkFrame(form, fg_color="transparent")
        sched_row.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(sched_row, text="Schedule:", font=("Segoe UI", 12), text_color=C_TEXT).pack(side="left")
        self.batch_sched = ctk.CTkEntry(sched_row, fg_color=C_BG, text_color=C_TEXT, font=("Segoe UI", 12))
        self.batch_sched.insert(0, "2026-06-05 10:00:00")
        self.batch_sched.pack(side="left", fill="x", expand=True, padx=(10, 0))

        ctk.CTkButton(form, text="Create Batch from Pool", font=("Segoe UI", 14, "bold"),
                      fg_color=C_SUCCESS, hover_color="#2a8a4a", height=40,
                      command=self._create_batch).pack(fill="x", padx=15, pady=(5, 15))

        # Batch list
        self.all_batches_frame = ctk.CTkFrame(view, fg_color="transparent")
        self.all_batches_frame.pack(fill="both", expand=True)

        # ── Deleted Batches History ──
        self.history_frame = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=10)
        self.history_frame.pack(fill="x", pady=(15, 5), padx=self._sf(6))
        self.history_frame.pack_propagate(False)
        self.history_frame.configure(height=self._sf(42))

        self.history_header = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        self.history_header.pack(fill="x", padx=15, pady=8)
        self.history_header.bind("<Button-1>", lambda e: self._toggle_history())

        self.history_title = ctk.CTkLabel(self.history_header, text="📜 History (0)", font=("Segoe UI", 12, "bold"),
                                          text_color=C_TEXT_DIM)
        self.history_title.pack(side="left")
        self.history_toggle = ctk.CTkLabel(self.history_header, text="▼", font=("Segoe UI", 12, "bold"),
                                           text_color=C_TEXT_DIM)
        self.history_toggle.pack(side="right")

        self.history_content = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        self.history_expanded = False

        self._refresh_source_pools()
        self._refresh_all_batches()
        self._refresh_history()

    def _create_batch(self):
        try:
            name = self.batch_name.get().strip()
            size = int(self.batch_size.get())
            day = int(self.batch_day.get())
            sched = self.batch_sched.get().strip()
            source_seq = self._get_batch_source_seq()
            sub_pool = self.batch_sub_pool.get()
            if sub_pool == "(All)":
                sub_pool = None

            if not name:
                messagebox.showwarning("Missing Name", "Please enter a batch name")
                return

            result = self.engine.create_batch_from_pool(
                name=name, sequence_id=source_seq, batch_size=size,
                sub_pool=sub_pool, day_offset=day, scheduled_at=sched
            )

            if result.get("success"):
                pool_name = "Generic" if source_seq == "leads" else source_seq.upper()
                if sub_pool:
                    pool_name += f" [{sub_pool}]"
                self._log_activity(f"Created batch '{name}' with {result['size']} leads from {pool_name}")
                self._refresh_all_batches()
                self._refresh_dashboard()
                self._refresh_source_pools()
            else:
                messagebox.showwarning("Error", result.get("error", "Unknown error"))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _confirm_delete_batch(self, batch_id, batch_name):
        """Show confirmation popup before soft-deleting a batch."""
        try:
            count = self.engine.db.batch_count_recipients(batch_id)
        except:
            count = 0

        popup = ctk.CTkToplevel(self)
        popup.title("Delete Batch")
        popup.geometry("420x200")
        popup.configure(fg_color=C_BG)
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(popup, text="🗑️ Delete Batch?", font=("Segoe UI", 18, "bold"),
                     text_color=C_DANGER).pack(pady=(20, 5))
        ctk.CTkLabel(popup, text=f"{batch_name}", font=("Segoe UI", 12, "bold"),
                     text_color=C_TEXT).pack()
        ctk.CTkLabel(popup, text=f"{count} leads will return to the pool.", font=("Segoe UI", 11),
                     text_color=C_TEXT_DIM).pack(pady=(5, 20))

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Cancel", font=("Segoe UI", 12, "bold"),
                      fg_color=C_PANEL, hover_color="#3a3a5e",
                      command=popup.destroy).pack(side="left", padx=5)

        def do_delete():
            popup.destroy()
            self._delete_batch(batch_id)

        ctk.CTkButton(btn_frame, text="Yes, Delete", font=("Segoe UI", 12, "bold"),
                      fg_color=C_DANGER, hover_color="#8a1c1c",
                      command=do_delete).pack(side="left", padx=5)

    def _delete_batch(self, batch_id):
        """Soft-delete a batch and refresh the view."""
        try:
            result = self.engine.delete_batch(batch_id)
            if result.get("success"):
                returned = result.get("returned", 0)
                self._log_activity(f"Batch deleted — {returned} leads returned to pool")
                self._refresh_all_batches()
                self._refresh_dashboard()
                self._refresh_source_pools()
                self._refresh_history()
            else:
                messagebox.showwarning("Cannot Delete", result.get("error", "Unknown error"))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _toggle_history(self):
        """Expand/collapse the deleted batches history section."""
        self.history_expanded = not self.history_expanded
        if self.history_expanded:
            self.history_frame.configure(height=0)
            self.history_toggle.configure(text="▲")
            self.history_content.pack(fill="x", padx=15, pady=(0, 15), expand=True)
            self._refresh_history()
        else:
            self.history_content.pack_forget()
            self.history_frame.configure(height=self._sf(42))
            self.history_toggle.configure(text="▼")

    def _refresh_history(self):
        """Refresh the deleted batches history list."""
        for widget in self.history_content.winfo_children():
            widget.destroy()

        try:
            deleted = self.engine.db.batch_get_deleted()
            self.history_title.configure(text=f"📜 History ({len(deleted)})")

            if not deleted:
                ctk.CTkLabel(self.history_content, text="No deleted batches",
                             font=("Segoe UI", 11), text_color=C_TEXT_DIM).pack(anchor="w", pady=(5, 0))
                return

            for batch in deleted[:20]:  # Show last 20
                row = ctk.CTkFrame(self.history_content, fg_color="transparent")
                row.pack(fill="x", pady=2)

                name = batch.get("name", "Unknown")
                seq = batch.get("sequence_id", "").upper()
                deleted_at = batch.get("deleted_at", "") or "Unknown"
                try:
                    dt = datetime.fromisoformat(deleted_at.replace("Z", "+00:00"))
                    deleted_at = dt.strftime("%d %b %Y")
                except:
                    pass

                try:
                    count = self.engine.db.batch_count_recipients(batch["id"])
                except:
                    count = 0

                ctk.CTkLabel(row, text=f"• {name}", font=("Segoe UI", 11, "bold"),
                             text_color=C_TEXT).pack(side="left")
                ctk.CTkLabel(row, text=f"  {seq}  •  {count} leads  •  deleted {deleted_at}",
                             font=("Segoe UI", 10), text_color=C_TEXT_DIM).pack(side="left", padx=(8, 0))
        except Exception as e:
            ctk.CTkLabel(self.history_content, text=f"Error loading history: {e}",
                         font=("Segoe UI", 10), text_color=C_DANGER).pack(anchor="w", pady=(5, 0))

    def _refresh_all_batches(self):
        for widget in self.all_batches_frame.winfo_children():
            widget.destroy()
        self._family_card_widgets.clear()
        self._family_days_cache.clear()
        self._family_expanded_frames.clear()
        self._family_toggle_buttons.clear()

        # Show loading indicator so UI doesn't look frozen
        loading = ctk.CTkLabel(self.all_batches_frame, text="Loading batches...",
                               font=self._font(12), text_color=C_TEXT_DIM)
        loading.pack(pady=self._sf(30))

        def _fetch():
            batches = self.engine.db.batch_get_all()
            if not batches:
                return []

            from collections import defaultdict
            groups = defaultdict(list)
            for b in batches:
                gn = self._extract_batch_group(b.get("name", str(b["id"])))
                groups[gn].append(b)

            families = {}
            for gn, batch_list in groups.items():
                families[gn] = self._deduplicate_batches_by_day(batch_list)

            def _sort_key(item):
                name, days = item
                dates = []
                for d in ["D1", "D3", "D5", "D7", "D10"]:
                    b = days.get(d)
                    if b and isinstance(b, dict) and b.get("scheduled_at"):
                        try:
                            dt = datetime.fromisoformat(b["scheduled_at"].replace("Z", "+00:00"))
                            dates.append(dt)
                        except:
                            pass
                due_key = min(dates) if dates else datetime.max
                priority = 0
                for d in ["D1", "D3", "D5", "D7", "D10"]:
                    b = days.get(d)
                    if b and isinstance(b, dict):
                        st = str(b.get("status", "")).lower()
                        if st == "running":
                            priority = max(priority, 5)
                        elif st == "scheduled":
                            priority = max(priority, 4)
                        elif st == "draft":
                            priority = max(priority, 3)
                        elif st == "paused":
                            priority = max(priority, 2)
                        elif st == "completed":
                            priority = max(priority, 1)
                return (due_key, -priority)

            return sorted(families.items(), key=_sort_key)

        self._run_bg(_fetch, self._build_all_batches_ui, self._show_batches_error)

    def _build_all_batches_ui(self, sorted_families):
        for widget in self.all_batches_frame.winfo_children():
            widget.destroy()
        if not sorted_families:
            ctk.CTkLabel(self.all_batches_frame, text="No batches yet. Create one above.",
                         font=self._font(12), text_color=C_TEXT_DIM).pack(pady=self._sf(30))
            return
        for family_name, days in sorted_families:
            self._family_days_cache[family_name] = days
            self._render_batch_family_card(family_name, days)

    def _show_batches_error(self, msg):
        for widget in self.all_batches_frame.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self.all_batches_frame, text=f"Error: {msg}", text_color=C_DANGER).pack(pady=20)

    def _render_batch_family_card(self, family_name, days):
        """5-day pipeline card for Batches tab. Exactly 5 day pills per group."""
        scale = self._get_scale()
        is_expanded = self._expanded_families.get(family_name, False)

        card = ctk.CTkFrame(self.all_batches_frame, fg_color=C_PANEL, corner_radius=self._sf(12),
                            border_width=1, border_color="#1e3a5f")
        card.pack(fill="x", pady=self._sf(8), padx=self._sf(6))
        self._family_card_widgets[family_name] = card

        # ── Header ──
        header = ctk.CTkFrame(card, fg_color="transparent", height=self._sf(36))
        header.pack(fill="x", padx=self._sf(14), pady=(self._sf(10), self._sf(4)))
        header.pack_propagate(False)

        seq_id = ""
        family_total = 0
        filled_days = 0
        for day_code in ["D1", "D3", "D5", "D7", "D10"]:
            b = days.get(day_code)
            if b and isinstance(b, dict):
                if not seq_id:
                    seq_id = b.get("sequence_id", "").upper()
                if family_total == 0:
                    try:
                        counts = self.engine.db.batch_count_by_status(b["id"])
                        family_total = sum(counts.values())
                    except:
                        pass
                # Only count as "filled" if all emails sent (COMPLETED)
                try:
                    counts = self.engine.db.batch_count_by_status(b["id"])
                    sent = counts.get("sent", 0)
                    total = sum(counts.values())
                    if sent >= total and total > 0:
                        filled_days += 1
                except:
                    pass

        name_color = C_ACCENT if seq_id == "SCHOOL" else C_WARNING if seq_id in ("CSR", "CSR-WSL-5") else "white"

        left_hdr = ctk.CTkFrame(header, fg_color="transparent")
        left_hdr.pack(side="left", fill="y")

        ctk.CTkLabel(left_hdr, text=family_name, font=self._font(15, bold=True),
                     text_color=name_color).pack(side="left")

        seq_badge_bg = "#0d3a4a" if seq_id == "SCHOOL" else "#4a3a0d" if seq_id in ("CSR", "CSR-WSL-5") else "#2a2a4e"
        ctk.CTkLabel(left_hdr, text=f"  {seq_id}  ", font=self._font(8, bold=True),
                     text_color=name_color, fg_color=seq_badge_bg,
                     corner_radius=self._sf(10)).pack(side="left", padx=(self._sf(8), 0))

        ctk.CTkLabel(left_hdr, text=f"  {filled_days}/5 days  •  {family_total} recipients",
                     font=self._font(10), text_color=C_TEXT_DIM).pack(side="left")

        # Overall progress: truly completed days out of 5
        if filled_days > 0:
            prog_pct = min(100, int(filled_days / 5 * 100))
            prog_frame = ctk.CTkFrame(header, fg_color="#1a1a2e", height=self._sf(6),
                                       corner_radius=self._sf(3), width=self._sf(120))
            prog_frame.pack(side="left", padx=(self._sf(14), 0))
            prog_frame.pack_propagate(False)
            if prog_pct > 0:
                fill_w = int(120 * scale * prog_pct / 100)
                ctk.CTkFrame(prog_frame, fg_color=C_SUCCESS, height=self._sf(6),
                             corner_radius=self._sf(3), width=fill_w).pack(side="left")
            ctk.CTkLabel(header, text=f" {prog_pct}%", font=self._font(9, bold=True),
                         text_color=C_SUCCESS if prog_pct == 100 else C_TEXT_DIM).pack(side="left")

        # Expand / collapse toggle
        toggle_text = "▲ Collapse" if is_expanded else "▼ Expand"
        toggle_btn = ctk.CTkButton(header, text=toggle_text, font=self._font(9),
                                   fg_color="transparent", hover_color="#1e3a5f",
                                   text_color=C_ACCENT, width=self._sf(80), height=self._sf(24),
                                   command=lambda fn=family_name: self._toggle_family_expand(fn))
        toggle_btn.pack(side="right")
        self._family_toggle_buttons[family_name] = toggle_btn

        # ── 5 Day Pills Row ──
        pills_row = ctk.CTkFrame(card, fg_color="transparent")
        pills_row.pack(fill="x", padx=self._sf(8), pady=(self._sf(4), self._sf(8)))
        for i in range(5):
            pills_row.grid_columnconfigure(i, weight=1, uniform="pill")

        day_list = [("D1", 1, "D1"), ("D3", 3, "D3"), ("D5", 5, "D5"), ("D7", 7, "D7"), ("D10", 10, "D10")]

        for col, (day_code, day_num, day_label) in enumerate(day_list):
            batch = days.get(day_code)
            if batch and not isinstance(batch, dict):
                batch = None

            status = str(batch.get("status", "")).strip().upper() if batch else "NONE"
            batch_id = batch.get("id") if batch else None
            scheduled = batch.get("scheduled_at", "") if batch and batch.get("scheduled_at") else ""

            sent = 0
            total = family_total
            due = 0
            if batch:
                try:
                    counts = self.engine.db.batch_count_by_status(batch["id"])
                    sent = counts.get("sent", 0)
                    due = total - sent
                except:
                    pass
            else:
                due = total

            actual_status = status
            if status == "COMPLETED" and sent < total and total > 0:
                actual_status = "DRAFT"
            elif scheduled and actual_status not in ["COMPLETED", "RUNNING"]:
                actual_status = "SCHEDULED"

            # Colors — SCHEDULED = yellow, COMPLETED = green, RUNNING/DRAFT = teal
            if actual_status == "COMPLETED":
                bg, border, accent = "#0a3a2a", "#2ecc71", "#2ecc71"
            elif actual_status == "SCHEDULED":
                bg, border, accent = "#3a2a0d", "#febe32", "#febe32"
            elif actual_status in ["RUNNING", "DRAFT"]:
                bg, border, accent = "#0d2b2b", "#0d9b8a", "#0d9b8a"
            elif actual_status == "PAUSED":
                bg, border, accent = "#2a2a1a", "#d29922", "#d29922"
            else:
                bg, border, accent = "#151528", "#2a2a4e", "#555577"

            # Elongated pill
            pill_h = self._sf(200)
            pill = ctk.CTkFrame(pills_row, fg_color=bg, corner_radius=self._sf(8),
                                border_width=1, border_color=border, height=pill_h)
            pill.grid(row=0, column=col, padx=self._sf(4), pady=self._sf(3), sticky="nsew")
            pill.grid_propagate(False)

            # Day label + date
            day_frame = ctk.CTkFrame(pill, fg_color="transparent", height=self._sf(20))
            day_frame.pack(fill="x", padx=self._sf(8), pady=(self._sf(6), 0))
            day_frame.pack_propagate(False)

            ctk.CTkLabel(day_frame, text=day_label, font=self._font(10, bold=True),
                         text_color=accent).pack(side="left")

            date_text = ""
            if scheduled:
                try:
                    dt = datetime.fromisoformat(scheduled.replace("Z", "+00:00"))
                    date_text = dt.strftime("%d %b")
                except Exception:
                    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S.%f",
                                "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"]:
                        try:
                            dt = datetime.strptime(scheduled, fmt)
                            date_text = dt.strftime("%d %b")
                            break
                        except ValueError:
                            continue
            elif status in ["NONE", "NOT_CREATED"]:
                date_text = "Not scheduled"
            else:
                date_text = ""
            if date_text:
                color = "#484f58" if status == "NOT_CREATED" else "#4a5a6a"
                ctk.CTkLabel(day_frame, text=f"  {date_text}", font=self._font(8),
                             text_color=color).pack(side="left")

            # Sent / Total big
            ctk.CTkLabel(pill, text=f"{sent}/{total}", font=self._font(18, bold=True),
                         text_color="white").pack(anchor="w", padx=self._sf(8), pady=(self._sf(2), 0))

            # Mini progress bar inside pill
            if total > 0:
                prog_pct = int(sent / total * 100)
                bar_w = self._sf(100)
                bar_bg = ctk.CTkFrame(pill, fg_color="#1a1a2e", height=self._sf(4),
                                       corner_radius=self._sf(2), width=bar_w)
                bar_bg.pack(anchor="w", padx=self._sf(8), pady=(self._sf(4), self._sf(4)))
                bar_bg.pack_propagate(False)
                if prog_pct > 0:
                    fill_w = max(2, int(bar_w * prog_pct / 100))
                    ctk.CTkFrame(bar_bg, fg_color=C_SUCCESS if prog_pct == 100 else C_ACCENT,
                                 height=self._sf(4), corner_radius=self._sf(2), width=fill_w
                                 ).pack(side="left")

            # Status badge
            states = {"COMPLETED": "Done", "RUNNING": "Sending", "SCHEDULED": "Scheduled",
                      "DRAFT": "Ready", "PAUSED": "Paused", "NONE": "Queue"}
            badge_text = states.get(actual_status, "")
            badge_color = C_SUCCESS if actual_status == "COMPLETED" else "#febe32" if actual_status == "SCHEDULED" else "#0d9b8a" if actual_status == "RUNNING" else "#d29922" if actual_status == "PAUSED" else "#5a6a7a"
            badge_bg = "#0d3a2a" if actual_status == "COMPLETED" else "#3a2a0d" if actual_status == "SCHEDULED" else "#0d2b2b" if actual_status == "RUNNING" else "#2a2a1a" if actual_status == "PAUSED" else "#1a1a2e"
            if badge_text:
                badge = ctk.CTkLabel(pill, text=f"  {badge_text}  ", font=self._font(8, bold=True),
                                     text_color=badge_color, fg_color=badge_bg,
                                     corner_radius=self._sf(10))
                badge.pack(anchor="w", padx=self._sf(8), pady=(self._sf(2), 0))

            # Due / to-send line
            if actual_status == "COMPLETED":
                st_text, st_color = "All sent", "#0d9b8a"
            elif due > 0 and actual_status not in ["NONE"]:
                st_text, st_color = f"{due} due", "#febe32"
            elif actual_status == "NONE" and family_total > 0:
                st_text, st_color = f"{family_total} to send", "#febe32"
            else:
                st_text, st_color = "", C_TEXT_DIM
            if st_text:
                ctk.CTkLabel(pill, text=st_text, font=self._font(9),
                             text_color=st_color).pack(anchor="w", padx=self._sf(8), pady=(self._sf(2), 0))

            # Buttons row
            btn_h = self._sf(26)
            btn_frame = ctk.CTkFrame(pill, fg_color="transparent", height=btn_h)
            btn_frame.pack(fill="x", padx=self._sf(4), pady=(self._sf(4), self._sf(6)))
            btn_frame.grid_columnconfigure(0, weight=1)
            btn_frame.grid_columnconfigure(1, weight=1)
            btn_frame.grid_columnconfigure(2, weight=1)
            btn_frame.pack_propagate(False)

            if actual_status in ["COMPLETED", "NOT_CREATED"]:
                action_text = None
            elif actual_status in ["DRAFT", "SCHEDULED", "PAUSED"]:
                action_text, action_color = "▶ Start", "#0d9b8a"
            elif actual_status == "RUNNING":
                action_text, action_color = "⏸ Pause", "#d29922"
            else:
                action_text, action_color = "+ Create", "#3a3a5e"

            # Deletable only for completed or draft batches
            can_delete = batch_id and status in ("COMPLETED", "DRAFT")

            if action_text:
                ctk.CTkButton(btn_frame, text=action_text, font=self._font(9, bold=True),
                              fg_color=action_color, hover_color=action_color,
                              text_color="white", corner_radius=self._sf(4), height=btn_h,
                              command=lambda b=batch_id, s=actual_status, d=day_num, f=family_name, sq=seq_id: self._on_pill_click(b, s, d, f, sq)
                              ).grid(row=0, column=0, padx=(0, 1), sticky="nsew")
            else:
                ctk.CTkFrame(btn_frame, fg_color="transparent", height=btn_h).grid(row=0, column=0, padx=(0, 1), sticky="nsew")

            if can_delete:
                ctk.CTkButton(btn_frame, text="🗑️", font=self._font(9),
                              fg_color=C_DANGER, hover_color="#8a1c1c",
                              text_color="white", corner_radius=self._sf(4), height=btn_h,
                              command=lambda b=batch_id, n=batch.get("name", ""): self._confirm_delete_batch(b, n)
                              ).grid(row=0, column=1, padx=(1, 1), sticky="nsew")
            else:
                ctk.CTkFrame(btn_frame, fg_color="transparent", height=btn_h).grid(row=0, column=1, padx=(1, 1), sticky="nsew")

            ctk.CTkButton(btn_frame, text="📊", font=self._font(9),
                          fg_color="#1a1a3e", hover_color="#2a2a5e",
                          text_color="white", corner_radius=self._sf(4), height=btn_h,
                          command=lambda b=batch_id, f=family_name, d=day_num: self._show_pill_report(b, f, d)
                          ).grid(row=0, column=2, padx=(1, 0), sticky="nsew")

            if batch_id:
                pill.bind("<Button-1>", lambda e, b=batch_id, fn=family_name, dc=day_code: self._on_pill_select(b, fn, dc))

        # ── Expanded section ──
        if is_expanded:
            self._render_family_expanded_section(card, family_name, days)

    def _on_pill_select(self, batch_id, family_name, day_code):
        """Select a day pill to focus the expanded view on — in-place update."""
        self._expanded_family_day[family_name] = day_code
        if self._expanded_families.get(family_name, False):
            card = self._family_card_widgets.get(family_name)
            days = self._family_days_cache.get(family_name)
            if card and days:
                old_frame = self._family_expanded_frames.pop(family_name, None)
                if old_frame:
                    old_frame.destroy()
                self._render_family_expanded_section(card, family_name, days)
        else:
            self._toggle_family_expand(family_name)

    def _toggle_family_expand(self, family_name):
        """Toggle expand/collapse for a family card — in-place, no full re-render."""
        currently_expanded = self._expanded_families.get(family_name, False)
        self._expanded_families[family_name] = not currently_expanded

        card = self._family_card_widgets.get(family_name)
        days = self._family_days_cache.get(family_name)
        if not card or not days:
            self._refresh_all_batches()
            return

        if currently_expanded:
            old_frame = self._family_expanded_frames.pop(family_name, None)
            if old_frame:
                old_frame.destroy()
        else:
            if family_name not in self._expanded_family_day:
                for dc in ["D1", "D3", "D5", "D7", "D10"]:
                    if days.get(dc):
                        self._expanded_family_day[family_name] = dc
                        break
            self._render_family_expanded_section(card, family_name, days)

        btn = self._family_toggle_buttons.get(family_name)
        if btn:
            btn.configure(text="▲ Collapse" if not currently_expanded else "▼ Expand")

    def _update_expand_button_text(self, card, family_name, is_expanded):
        """Helper to update toggle button text (fallback)."""
        btn = self._family_toggle_buttons.get(family_name)
        if btn:
            btn.configure(text="▲ Collapse" if is_expanded else "▼ Expand")

    def _render_family_expanded_section(self, parent_card, family_name, days):
        """Render the expanded recipient list + stats below the day pills."""
        scale = self._get_scale()

        exp_frame = ctk.CTkFrame(parent_card, fg_color="#0f0f1a", corner_radius=self._sf(8))
        exp_frame.pack(fill="x", padx=self._sf(10), pady=(0, self._sf(10)))
        self._family_expanded_frames[family_name] = exp_frame

        # Find the day to show — prefer selected, fallback to first existing
        day_code = self._expanded_family_day.get(family_name, "D1")
        batch = days.get(day_code)
        if not batch:
            for dc in ["D1", "D3", "D5", "D7", "D10"]:
                if days.get(dc):
                    day_code = dc
                    batch = days[dc]
                    break

        if not batch:
            ctk.CTkLabel(exp_frame, text="No batch data available",
                         font=self._font(11), text_color=C_TEXT_DIM).pack(pady=self._sf(20))
            return

        batch_id = batch.get("id")

        # Mini stats bar
        try:
            counts = self.engine.db.batch_count_by_status(batch_id)
        except:
            counts = {}
        total = sum(counts.values())
        sent = counts.get("sent", 0)
        pending = counts.get("pending", 0)
        bounced = counts.get("bounced", 0)
        replied = counts.get("replied", 0)

        stats_bar = ctk.CTkFrame(exp_frame, fg_color="transparent", height=self._sf(28))
        stats_bar.pack(fill="x", padx=self._sf(12), pady=(self._sf(8), self._sf(6)))
        stats_bar.pack_propagate(False)

        ctk.CTkLabel(stats_bar, text=f"📅 Day {day_code.replace('D', '')}  •  ",
                     font=self._font(11, bold=True), text_color=C_ACCENT).pack(side="left")

        stat_items = [
            ("Total", total, "white"), ("Sent", sent, C_SUCCESS),
            ("Pending", pending, C_WARNING), ("Bounced", bounced, C_DANGER),
            ("Replied", replied, C_ACCENT)
        ]
        for label, val, color in stat_items:
            ctk.CTkLabel(stats_bar, text=f"{label}: ", font=self._font(10), text_color=C_TEXT_DIM).pack(side="left")
            ctk.CTkLabel(stats_bar, text=str(val), font=self._font(10, bold=True), text_color=color).pack(side="left")
            ctk.CTkLabel(stats_bar, text="  ", font=self._font(10)).pack(side="left")

        # Scrollable recipient list
        rec_frame = ctk.CTkScrollableFrame(exp_frame, fg_color="transparent", height=self._sf(180))
        rec_frame.pack(fill="x", padx=self._sf(12), pady=(0, self._sf(10)))

        try:
            recipients = self.engine.db.batch_get_recipients(batch_id)
            if not recipients:
                ctk.CTkLabel(rec_frame, text="No recipients in this batch",
                             font=self._font(10), text_color=C_TEXT_DIM).pack(pady=self._sf(10))
            else:
                for r in recipients:
                    status = r.get("batch_status", "pending")
                    color = C_SUCCESS if status == "sent" else C_DANGER if status == "bounced" else C_WARNING if status == "skipped" else C_TEXT_DIM
                    row = ctk.CTkFrame(rec_frame, fg_color="transparent")
                    row.pack(fill="x", pady=self._sf(2))
                    ctk.CTkLabel(row, text="●", font=self._font(8), text_color=color).pack(side="left")
                    ctk.CTkLabel(row, text=f" {r.get('name', 'Unknown')}  ({r.get('email', 'N/A')})",
                                 font=self._font(10), text_color=C_TEXT).pack(side="left")
                    ctk.CTkLabel(row, text=status.upper(), font=self._font(9), text_color=color).pack(side="right")
        except Exception as e:
            ctk.CTkLabel(rec_frame, text=f"Error loading recipients: {e}",
                         font=self._font(10), text_color=C_DANGER).pack(pady=self._sf(10))

    # ═══════════════════════════════════════════════════════════
    # REPLIES VIEW
    # ═══════════════════════════════════════════════════════════
    def _build_replies_view(self):
        view = ctk.CTkFrame(self.content, fg_color="transparent")
        self.views["replies"] = view

        ctk.CTkLabel(view, text="💬 Replies", font=("Segoe UI", 24, "bold"),
                     text_color="white").pack(anchor="w", pady=(0, 15))

        self.replies_frame = ctk.CTkFrame(view, fg_color="transparent")
        self.replies_frame.pack(fill="both", expand=True)

        self._refresh_replies()

    def _refresh_replies(self):
        for widget in self.replies_frame.winfo_children():
            widget.destroy()

        try:
            replies = self.engine.db.execute("""
                SELECT r.id, r.from_addr, r.subject, r.body, r.sentiment, r.status, r.received_at,
                       s.recipient_id, rec.name, rec.org
                FROM replies r
                LEFT JOIN sends s ON r.send_id = s.id
                LEFT JOIN recipients rec ON s.recipient_id = rec.id
                ORDER BY r.received_at DESC
            """).fetchall()

            if not replies:
                ctk.CTkLabel(self.replies_frame, text="No replies yet",
                             font=("Segoe UI", 12), text_color=C_TEXT_DIM).pack(pady=30)
                return

            for reply in replies:
                row = ctk.CTkFrame(self.replies_frame, fg_color=C_PANEL, corner_radius=8)
                row.pack(fill="x", pady=4, padx=4)

                from_addr = reply[1] or "Unknown"
                subject = reply[2] or "No subject"
                sentiment = reply[4] or "neutral"
                status = reply[5] or "pending"
                name = reply[8] or "Unknown"
                org = reply[9] or ""

                color = C_SUCCESS if sentiment == "positive" else C_DANGER if sentiment in ["hostile", "unsubscribe"] else C_WARNING
                ctk.CTkLabel(row, text=f"● {name} ({from_addr})", font=("Segoe UI", 12, "bold"),
                             text_color=color).pack(anchor="w", padx=10, pady=(8, 2))
                ctk.CTkLabel(row, text=f"Subject: {subject}", font=("Segoe UI", 10),
                             text_color=C_TEXT_DIM).pack(anchor="w", padx=10)
                ctk.CTkLabel(row, text=f"Sentiment: {sentiment} | Status: {status}", font=("Segoe UI", 10),
                             text_color=C_TEXT_DIM).pack(anchor="w", padx=10, pady=(0, 8))

        except Exception as e:
            ctk.CTkLabel(self.replies_frame, text=f"Error: {e}", text_color=C_DANGER).pack(pady=20)

    # ═══════════════════════════════════════════════════════════
    # BLACKLIST VIEW
    # ═══════════════════════════════════════════════════════════
    def _build_blacklist_view(self):
        view = ctk.CTkFrame(self.content, fg_color="transparent")
        self.views["blacklist"] = view

        ctk.CTkLabel(view, text="🚫 Blacklist", font=("Segoe UI", 24, "bold"),
                     text_color="white").pack(anchor="w", pady=(0, 15))

        # Add email
        add_frame = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=10)
        add_frame.pack(fill="x", pady=(0, 10))

        self.blacklist_entry = ctk.CTkEntry(add_frame, fg_color=C_BG, text_color=C_TEXT, font=("Segoe UI", 12))
        self.blacklist_entry.pack(side="left", fill="x", expand=True, padx=15, pady=10)
        ctk.CTkButton(add_frame, text="Add", font=("Segoe UI", 12), width=80,
                      fg_color=C_DANGER, command=self._add_to_blacklist).pack(side="right", padx=15, pady=10)

        # Bounce Scanner
        scan_frame = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=10)
        scan_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(scan_frame, text="📨 Bounce Scan", font=("Segoe UI", 12, "bold"),
                     text_color=C_ACCENT).pack(side="left", padx=15, pady=10)

        self.bounce_range = ctk.CTkOptionMenu(scan_frame,
            values=["Last 3 days", "Last 7 days", "Last 15 days", "Last 30 days"],
            font=("Segoe UI", 11), width=140, fg_color=C_BG)
        self.bounce_range.pack(side="left", padx=(0, 10), pady=10)
        self.bounce_range.set("Last 15 days")

        ctk.CTkButton(scan_frame, text="▶ Scan", font=("Segoe UI", 11), width=80,
                      fg_color=C_SUCCESS, hover_color="#0d7a6a",
                      command=self._run_bounce_scan).pack(side="left", padx=(0, 10), pady=10)

        self.bounce_status = ctk.CTkLabel(scan_frame, text="", font=("Segoe UI", 10),
                                          text_color=C_TEXT_DIM)
        self.bounce_status.pack(side="left", padx=10, pady=10)

        # List
        self.blacklist_frame = ctk.CTkFrame(view, fg_color="transparent")
        self.blacklist_frame.pack(fill="both", expand=True)

        self._refresh_blacklist()

    def _refresh_blacklist(self):
        for widget in self.blacklist_frame.winfo_children():
            widget.destroy()

        try:
            emails = self.engine.db.execute("SELECT email, reason, added_at FROM blacklist ORDER BY added_at DESC").fetchall()

            if not emails:
                ctk.CTkLabel(self.blacklist_frame, text="No blacklisted emails",
                             font=("Segoe UI", 12), text_color=C_TEXT_DIM).pack(pady=30)
                return

            for email, reason, added_at in emails:
                row = ctk.CTkFrame(self.blacklist_frame, fg_color=C_PANEL, corner_radius=6)
                row.pack(fill="x", pady=2, padx=4)

                ctk.CTkLabel(row, text=f"● {email}", font=("Segoe UI", 11),
                             text_color=C_DANGER).pack(side="left", padx=10, pady=6)
                ctk.CTkLabel(row, text=f"({reason})", font=("Segoe UI", 9),
                             text_color=C_TEXT_DIM).pack(side="left")
                ctk.CTkButton(row, text="✕", font=("Segoe UI", 10), width=30,
                              fg_color="transparent", text_color=C_DANGER,
                              command=lambda e=email: self._remove_from_blacklist(e)).pack(side="right", padx=5)

        except Exception as e:
            ctk.CTkLabel(self.blacklist_frame, text=f"Error: {e}", text_color=C_DANGER).pack(pady=20)

    def _add_to_blacklist(self):
        email = self.blacklist_entry.get().strip().lower()
        if email and "@" in email:
            self.engine.blacklist_add(email, "manual")
            self.blacklist_entry.delete(0, "end")
            self._refresh_blacklist()
            self._refresh_dashboard()

    def _remove_from_blacklist(self, email):
        self.engine.blacklist_remove(email)
        self._refresh_blacklist()
        self._refresh_dashboard()

    def _run_bounce_scan(self):
        """Run deep bounce scan from the Blacklist tab UI."""
        import threading
        range_map = {
            "Last 3 days": 3,
            "Last 7 days": 7,
            "Last 15 days": 15,
            "Last 30 days": 30,
        }
        days = range_map.get(self.bounce_range.get(), 15)
        self.bounce_status.configure(text="Scanning...", text_color=C_WARNING)

        def do_scan():
            try:
                result = self.engine.deep_bounce_scan(days=days)
                self._safe_after(0, lambda: self._on_bounce_scan_done(result))
            except Exception as e:
                self._safe_after(0, lambda: self.bounce_status.configure(
                    text=f"Error: {str(e)[:50]}", text_color=C_DANGER))

        threading.Thread(target=do_scan, daemon=True).start()

    def _on_bounce_scan_done(self, result):
        found = result.get('found', 0)
        blacklisted = result.get('blacklisted', 0)
        protected = result.get('protected', 0)
        self.bounce_status.configure(
            text=f"Done — {found} found, {blacklisted} blacklisted, {protected} protected",
            text_color=C_SUCCESS)
        self._refresh_blacklist()
        self._refresh_dashboard()

    # ═══════════════════════════════════════════════════════════
    # SETTINGS VIEW
    # ═══════════════════════════════════════════════════════════
    def _build_settings_view(self):
        view = ctk.CTkFrame(self.content, fg_color="transparent")
        self.views["settings"] = view

        ctk.CTkLabel(view, text="⚙️ Settings", font=("Segoe UI", 24, "bold"),
                     text_color="white").pack(anchor="w", pady=(0, 15))

        # Brief email
        brief_frame = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=10)
        brief_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(brief_frame, text="Morning Brief Email:", font=("Segoe UI", 12),
                     text_color=C_TEXT).pack(anchor="w", padx=15, pady=(10, 5))
        self.brief_email_entry = ctk.CTkEntry(brief_frame, fg_color=C_BG, text_color=C_TEXT, font=("Segoe UI", 12))
        self.brief_email_entry.pack(fill="x", padx=15, pady=(0, 10))
        self.brief_email_entry.insert(0, self.engine.brief_email or "")
        ctk.CTkButton(brief_frame, text="Save", font=("Segoe UI", 12),
                      fg_color=C_ACCENT, command=self._save_brief_email).pack(anchor="e", padx=15, pady=(0, 10))

        # Pause sequences
        pause_frame = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=10)
        pause_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(pause_frame, text="Pause Sequences:", font=("Segoe UI", 12),
                     text_color=C_TEXT).pack(anchor="w", padx=15, pady=(10, 5))

        self.pause_school = ctk.CTkCheckBox(pause_frame, text="Pause SCHOOL",
                                              font=("Segoe UI", 11), text_color=C_TEXT)
        self.pause_school.pack(anchor="w", padx=15, pady=5)

        self.pause_csr = ctk.CTkCheckBox(pause_frame, text="Pause CSR",
                                         font=("Segoe UI", 11), text_color=C_TEXT)
        self.pause_csr.pack(anchor="w", padx=15, pady=5)

        self.pause_csr_wsl_5 = ctk.CTkCheckBox(pause_frame, text="Pause CSR-WSL-5",
                                                font=("Segoe UI", 11), text_color=C_TEXT)
        self.pause_csr_wsl_5.pack(anchor="w", padx=15, pady=5)

        ctk.CTkButton(pause_frame, text="Apply", font=("Segoe UI", 12),
                      fg_color=C_ACCENT, command=self._apply_pauses).pack(anchor="e", padx=15, pady=(5, 10))

        # Export
        export_frame = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=10)
        export_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(export_frame, text="Export:", font=("Segoe UI", 12),
                     text_color=C_TEXT).pack(anchor="w", padx=15, pady=(10, 5))
        ctk.CTkButton(export_frame, text="Export Campaign State", font=("Segoe UI", 12),
                      fg_color=C_SUCCESS, command=self._export_state).pack(anchor="w", padx=15, pady=(0, 10))

    def _save_brief_email(self):
        email = self.brief_email_entry.get().strip()
        self.engine.brief_email = email
        self.engine.db.set_meta("brief_email", email)
        self._log_activity(f"Brief email set to: {email}")

    def _apply_pauses(self):
        if self.pause_school.get():
            self.engine.db.set_meta("pause_school", "true")
        else:
            self.engine.db.set_meta("pause_school", "false")
        if self.pause_csr.get():
            self.engine.db.set_meta("pause_csr", "true")
        else:
            self.engine.db.set_meta("pause_csr", "false")
        if self.pause_csr_wsl_5.get():
            self.engine.db.set_meta("pause_csr_wsl_5", "true")
        else:
            self.engine.db.set_meta("pause_csr_wsl_5", "false")
        self._log_activity("Pause settings updated")

    def _export_state(self):
        try:
            md = self.engine.export_campaign_state()
            path = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown", "*.md")])
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(md)
                self._log_activity(f"State exported to {path}")
        except Exception as e:
            self._log_activity(f"Export error: {e}")

    # ═══════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ═══════════════════════════════════════════════════════════
    def _show_view(self, key):
        self._current_view = key
        for k, v in self.views.items():
            v.pack_forget()
        self.views[key].pack(fill="both", expand=True)

        # Update nav button colors
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color="#1a1a3e", text_color=C_ACCENT)
            else:
                btn.configure(fg_color="transparent", text_color=C_TEXT)

        # Debounce refreshes — don't hammer the UI on rapid tab switches
        now = time.time()
        last_refresh = getattr(self, '_last_refresh_time', {}).get(key, 0)
        if now - last_refresh < 2.0:
            return
        if not hasattr(self, '_last_refresh_time'):
            self._last_refresh_time = {}
        self._last_refresh_time[key] = now

        # Refresh specific views (lightweight — heavy DB work runs in threads)
        if key == "dashboard":
            self._refresh_dashboard()
        elif key == "analytics":
            self._refresh_analytics()
        elif key == "templates":
            self._refresh_templates()
        elif key == "batches":
            self._refresh_all_batches()
        elif key == "replies":
            self._refresh_replies()
        elif key == "blacklist":
            self._refresh_blacklist()

    def _scan_bounces_now(self):
        self._log_activity("Scanning bounces...")
        threading.Thread(target=self._do_bounce_scan, daemon=True).start()

    def _do_bounce_scan(self):
        try:
            result = self.engine.scan_bounces(days_back=15)
            self._safe_after(0, lambda: self._log_activity(
                f"Bounce scan: {result['new_blacklisted']} new, {result['auto_replies']} auto-replies, {result['protected']} protected"
            ))
            self._safe_after(0, self._refresh_dashboard)
        except Exception as e:
            self._safe_after(0, lambda: self._log_activity(f"Bounce scan error: {e}"))

    def _pause_engine(self):
        if self.engine.is_paused():
            self.engine.resume()
            self.btn_pause.configure(text="⏸", fg_color=C_WARNING)
            self.status_text.configure(text="Running", text_color=C_SUCCESS)
            self.status_dot.configure(text_color=C_SUCCESS)
            self._log_activity("Engine resumed")
        else:
            self.engine.pause()
            self.btn_pause.configure(text="▶", fg_color=C_SUCCESS)
            self.status_text.configure(text="Paused", text_color=C_WARNING)
            self.status_dot.configure(text_color=C_WARNING)
            self._log_activity("Engine paused")

    def _log_activity(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] {msg}")

    def _on_window_resize(self, event):
        """Handle window resize — debounced font update only."""
        if event.widget != self:
            return
        new_w = self.winfo_width()
        # Only act on meaningful width changes (>100px diff)
        if abs(new_w - getattr(self, '_last_win_width', new_w)) < 100:
            return
        self._last_win_width = new_w
        if getattr(self, '_resize_debounce', None):
            self.after_cancel(self._resize_debounce)
        self._resize_debounce = self.after(800, self._do_responsive_refresh)

    def _do_responsive_refresh(self):
        """Update fonts only — NEVER destroy/recreate widgets on resize."""
        try:
            self._refresh_dashboard_fonts()
        except Exception:
            pass

    # ═══════════════════════════════════════════════════════════
    # TRAY ICON INTEGRATION
    # ═══════════════════════════════════════════════════════════
    def setup_tray_icon(self, icon_path=None):
        """Setup system tray icon for quick access."""
        try:
            from tray_icon import TrayIcon
            self.tray = TrayIcon(self, icon_path)
            self.tray.run()
            self._log_activity("System tray icon active")
        except ImportError:
            self._log_activity("Tray icon not available (tray_icon.py missing)")
        except Exception as e:
            self._log_activity(f"Tray icon error: {e}")

    def show_window(self):
        """Show/hide window from tray."""
        if self.winfo_viewable():
            self.withdraw()
        else:
            self.deiconify()
            self.lift()
            self.focus_force()

    def on_closing(self):
        """Handle window close — minimize to tray instead of quitting."""
        if hasattr(self, 'tray') and self.tray:
            self.withdraw()
        else:
            self.destroy()

    def _graceful_exit(self):
        """Ctrl+Space or explicit close — stop engine and quit."""
        try:
            self._log_activity("Shutting down Raj...")
            if hasattr(self, 'engine'):
                self.engine.stop()
        except:
            pass
        self.destroy()
        import sys
        sys.exit(0)

    # ═══════════════════════════════════════════════════════════
    # BATCH RECIPIENT IMPORT (for individual batch)
    # ═══════════════════════════════════════════════════════════
    def _import_batch_recipients(self, batch_id, filepath):
        """Import recipients into a specific batch from Excel/CSV."""
        if not PANDAS_AVAILABLE:
            messagebox.showwarning("Missing Package", "pandas not installed. Run: pip install pandas openpyxl")
            return 0, 0

        try:
            df = pd.read_excel(filepath) if filepath.endswith('.xlsx') else pd.read_csv(filepath)
            headers = [str(h).strip().lower() for h in df.columns.tolist()]

            # Auto-detect columns
            email_col = None
            name_col = None
            org_col = None
            for i, h in enumerate(headers):
                if 'email' in h or 'e-mail' in h or 'mail' in h:
                    email_col = i
                elif 'name' in h or 'principal' in h or 'contact' in h or 'person' in h:
                    name_col = i
                elif 'org' in h or 'school' in h or 'company' in h or 'institution' in h or 'college' in h:
                    org_col = i

            if email_col is None:
                messagebox.showwarning("Column Error", "Could not find email column. Headers: " + ", ".join(headers))
                return 0, 0

            imported = 0
            skipped = 0
            for _, row in df.iterrows():
                email = str(row.iloc[email_col]).strip().lower() if email_col is not None else ""
                name = str(row.iloc[name_col]).strip() if name_col is not None else ""
                org = str(row.iloc[org_col]).strip() if org_col is not None else ""

                if not email or "@" not in email:
                    skipped += 1
                    continue
                if self.engine.db.blacklist_has(email):
                    skipped += 1
                    continue

                # Get sequence_id from the batch
                seq_id = self.engine.db.execute(
                    "SELECT sequence_id FROM batches WHERE id=?", (batch_id,)
                ).fetchone()[0]
                
                try:
                    self.engine.db.execute(
                        "INSERT INTO recipients (sequence_id, email, name, org, extra_json) VALUES (?, ?, ?, ?, ?)",
                        (seq_id, email, name, org, "{}")
                    )
                    rec_id = self.engine.db.execute("SELECT last_insert_rowid()").fetchone()[0]
                    self.engine.db.batch_add_recipient(batch_id, rec_id)
                    imported += 1
                except Exception as e:
                    skipped += 1

            self.engine.db.commit()
            self._log_activity(f"Batch import: {imported} imported, {skipped} skipped")
            return imported, skipped

        except Exception as e:
            messagebox.showerror("Import Error", str(e))
            return 0, 0

    # ═══════════════════════════════════════════════════════════
    # HTML PREVIEW
    # ═══════════════════════════════════════════════════════════
    def _preview_html(self, html_content, title="Preview"):
        """Open HTML preview in browser."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                path = f.name
            webbrowser.open(f'file://{path}')
            self._log_activity(f"Preview opened: {title}")
        except Exception as e:
            self._log_activity(f"Preview error: {e}")

    # ═══════════════════════════════════════════════════════════
    # BATCH IMPORT FROM FILE (standalone)
    # ═══════════════════════════════════════════════════════════
    def _import_batch_from_file(self):
        """Import recipients from file into current batch."""
        filepath = filedialog.askopenfilename(
            filetypes=[("Excel/CSV", "*.xlsx *.csv *.xls *.txt")]
        )
        if not filepath:
            return

        # Ask which batch
        batches = self.engine.db.batch_get_all()
        if not batches:
            messagebox.showwarning("No Batches", "Create a batch first")
            return

        batch_names = [f"{b['name']} (ID: {b['id']})" for b in batches]
        # Simple selection — just use first batch for now
        batch_id = batches[0]["id"]

        self._import_batch_recipients(batch_id, filepath)
        self._refresh_all_batches()
        self._refresh_dashboard()
