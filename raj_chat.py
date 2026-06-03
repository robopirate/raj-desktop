"""
raj_chat.py — Raj Command Center GUI v4.1
Dashboard, Batch Manager, Pipeline View, Individual Blacklist Removal
RESPONSIVE: Auto-adjusts to screen size, DPI aware, resize-friendly.
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

# === CHARTS TAB ===
try:
    from raj_charts import ChartsTab
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False

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

        self.template_cards = {}
        self.nav_buttons = {}
        self.views = {}
        self.batch_frames = {}

        self._build_ui()
        self._start_refresh_loop()
        self._log_activity("Raj v4.2 RoboPirate Brand Theme initialized")

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
            ("📧 Chat", "chat"),
            ("📥 Import", "import"),
            ("📝 Templates", "templates"),
            ("🚀 Batches", "batches"),
            ("💬 Replies", "replies"),
            ("🚫 Blacklist", "blacklist"),
            ("📊 Charts", "charts"),
            ("⚙️ Settings", "settings"),
        ]
        for text, key in nav_items:
            btn = ctk.CTkButton(self.sidebar, text=text, font=("Segoe UI", 12),
                               fg_color="transparent", anchor="w",
                               command=lambda k=key: self._show_view(k))
            btn.pack(fill="x", padx=10, pady=3)
            self.nav_buttons[key] = btn

        # Status bar
        self.status_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.status_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        self.status_dot = ctk.CTkLabel(self.status_frame, text="●", font=("Segoe UI", 14),
                                      text_color=C_SUCCESS)
        self.status_dot.pack(side="left")
        self.status_text = ctk.CTkLabel(self.status_frame, text="Running",
                                       font=("Segoe UI", 10), text_color=C_SUCCESS)
        self.status_text.pack(side="left", padx=(5, 0))

        self.btn_scan = ctk.CTkButton(self.status_frame, text="🔍 Scan",
                                      font=("Segoe UI", 9), width=60, height=25,
                                      fg_color=C_ACCENT,
                                      command=self._scan_bounces_now)
        self.btn_scan.pack(side="right", padx=(0, 5))

        self.btn_pause = ctk.CTkButton(self.status_frame, text="⏸ Pause",
                                      font=("Segoe UI", 9), width=80, height=25,
                                      fg_color=C_WARNING,
                                      command=self._pause_engine)
        self.btn_pause.pack(side="right")

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
        self._build_chat_view()
        self._build_import_view()
        self._build_templates_view()
        self._build_batches_view()
        self._build_replies_view()
        self._build_blacklist_view()
        self._build_charts_view()
        self._build_settings_view()

        self._show_view("dashboard")

    # ═══════════════════════════════════════════════════════════
    #  DASHBOARD VIEW
    # ═══════════════════════════════════════════════════════════
    def _build_dashboard_view(self):
        view = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        self.views["dashboard"] = view

        # Header
        ctk.CTkLabel(view, text="📊 Dashboard", font=("Segoe UI", 28, "bold"),
                    text_color="white").pack(anchor="w", pady=(0, 20))

        # Pipeline Overview Cards
        cards_frame = ctk.CTkFrame(view, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, 20))
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.dashboard_cards = {}
        sequences = [("school", "SCHOOL", C_ACCENT), ("csr", "CSR", C_WARNING), 
                     ("total", "TOTAL", C_SUCCESS), ("blacklist", "BLACKLIST", C_DANGER)]

        for col, (seq_id, label, color) in enumerate(sequences):
            card = ctk.CTkFrame(cards_frame, fg_color=C_PANEL, corner_radius=12)
            card.grid(row=0, column=col, padx=8, pady=5, sticky="nsew")

            ctk.CTkLabel(card, text=label, font=("Segoe UI", 14, "bold"),
                        text_color=color).pack(pady=(15, 5))

            stats = ctk.CTkFrame(card, fg_color="transparent")
            stats.pack(pady=(0, 15))

            self.dashboard_cards[seq_id] = {}
            for metric in ["leads", "sent", "replied", "bounced", "pool"]:
                lbl = ctk.CTkLabel(stats, text=f"{metric.capitalize()}: 0",
                                    font=("Segoe UI", 11), text_color=C_TEXT)
                lbl.pack(anchor="w", padx=15)
                self.dashboard_cards[seq_id][metric] = lbl

        # Day-wise Pipeline
        ctk.CTkLabel(view, text="📅 Day-wise Pipeline", font=("Segoe UI", 20, "bold"),
                    text_color="white").pack(anchor="w", pady=(20, 10))

        self.pipeline_table = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=8)
        self.pipeline_table.pack(fill="x", pady=(0, 20))

        # Headers
        headers = ["Day", "Total", "Sent", "Bounced", "Replied", "Status"]
        for col, h in enumerate(headers):
            ctk.CTkLabel(self.pipeline_table, text=h, font=("Segoe UI", 11, "bold"),
                        text_color=C_ACCENT).grid(row=0, column=col, padx=15, pady=8)

        self.pipeline_rows = {}
        for row, day in enumerate([1, 3, 5, 7, 10], start=1):
            self.pipeline_rows[day] = {}
            for col, h in enumerate(headers):
                lbl = ctk.CTkLabel(self.pipeline_table, text="-" if col > 0 else f"Day {day}",
                                   font=("Segoe UI", 10), text_color=C_TEXT)
                lbl.grid(row=row, column=col, padx=15, pady=5)
                self.pipeline_rows[day][h.lower()] = lbl

        # Active Batches
        ctk.CTkLabel(view, text="🚀 Active Batches", font=("Segoe UI", 20, "bold"),
                    text_color="white").pack(anchor="w", pady=(20, 10))

        self.batches_frame = ctk.CTkFrame(view, fg_color="transparent")
        self.batches_frame.pack(fill="x", pady=(0, 20))

    def _refresh_dashboard(self):
        """Refresh all dashboard data — cards, day table, active batches."""
        try:
            summary = self.engine.get_summary()

            # ─── Overview Cards ───
            totals = {"leads": 0, "sent": 0, "replied": 0, "bounced": 0, "pool": 0}

            for seq_id in ["school", "csr"]:
                seq_data = summary.get("sequences", {}).get(seq_id, {})
                pipeline = seq_data.get("pipeline", {})
                pool_count = seq_data.get("pool_count", 0)

                totals["leads"] += pipeline.get("total", 0)
                totals["sent"] += pipeline.get("sent", 0)
                totals["replied"] += pipeline.get("replied", 0)
                totals["bounced"] += pipeline.get("bounced", 0)
                totals["pool"] += pool_count

                # Update individual card with bright white text
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
            self.dashboard_cards["total"]["leads"].configure(text=f"Leads: {totals['leads']}", text_color="white")
            self.dashboard_cards["total"]["sent"].configure(text=f"Sent: {totals['sent']}", text_color="white")
            self.dashboard_cards["total"]["replied"].configure(text=f"Replied: {totals['replied']}", text_color="white")
            self.dashboard_cards["total"]["bounced"].configure(text=f"Bounced: {totals['bounced']}", text_color="white")
            if "pool" in self.dashboard_cards["total"]:
                self.dashboard_cards["total"]["pool"].configure(text=f"Pool: {totals['pool']}", text_color="white")

            # BLACKLIST card
            total_blacklist = summary.get("global", {}).get("blacklist_count", 0)
            self.dashboard_cards["blacklist"]["leads"].configure(text=f"Blocked: {total_blacklist}", text_color="white")

            # ─── Day-wise Pipeline Table (COMBINED SCHOOL + CSR) ───
            combined_day_wise = {}
            for seq_id in ["school", "csr"]:
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
                        status_text = f"ⳁ {metrics['sent']}/{metrics['total']}"
                        status_color = C_WARNING
                    else:
                        status_text = "⏳ Pending"
                        status_color = C_TEXT_DIM

                    self.pipeline_rows[day]["status"].configure(text=status_text, text_color=status_color)

            # ─── Active Batches (pipeline view) ───
            self._refresh_batch_list()

        except Exception as e:
            print(f"Dashboard refresh error: {e}")
            import traceback
            print(traceback.format_exc())

    def _refresh_batch_list(self):
        """Refresh active batches — show pipeline rows for all batches."""
        for widget in self.batches_frame.winfo_children():
            widget.destroy()

        try:
            batches = self.engine.db.batch_get_all()

            if not batches:
                ctk.CTkLabel(self.batches_frame, text="No batches yet. Create one in Batches tab.",
                            font=("Segoe UI", 12), text_color=C_TEXT_DIM).pack(pady=30)
                return

            # Group into families
            families = self._group_batches_into_families(batches)

            for family_name, days in sorted(families.items()):
                self._render_pipeline_card(family_name, days)

        except Exception as e:
            print(f"Batch list error: {e}")
            import traceback
            print(traceback.format_exc())
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
                if day in family_dict:
                    family_dict[day] = batch
                else:
                    family_dict["D1"] = batch
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
            if families[family_name].get(day) is None:
                families[family_name][day] = b
            else:
                for d in ["D1", "D3", "D5", "D7", "D10"]:
                    if families[family_name][d] is None:
                        families[family_name][d] = b
                        break
            assigned.add(b["id"])

        return families
    def _extract_family_name(self, batch_name):
        """Extract family name from batch name. Handles all patterns:
        - 'MUMBAI SCHOOL-B1' -> 'MUMBAI SCHOOL'
        - 'Pune_Email_B1-B1-D5' -> 'Pune_Email_B1'
        - 'Master_Lead-B2' -> 'Master_Lead'
        - 'CSR-Tata-D1' -> 'CSR-Tata'
        - 'a' -> 'a'
        - 'a-D3' -> 'a'
        """
        if not batch_name:
            return "Unknown"

        name = batch_name.strip()

        # Pattern 1: Remove -D<number> suffix (Day suffix like -D3, -D5)
        name = re.sub(r'[-_]D\d+$', '', name, flags=re.IGNORECASE)

        # Pattern 2: Remove -B<number> suffix (Batch suffix like -B1, -B2)
        # But be careful: "Pune_Email_B1-B1" should become "Pune_Email_B1"
        # "MUMBAI SCHOOL-B1" should become "MUMBAI SCHOOL"
        # Try: remove trailing -B<digit> or _B<digit> only if preceded by non-B
        name = re.sub(r'(?<![Bb])[-_]B\d+$', '', name, flags=re.IGNORECASE)

        # Pattern 3: If still has pattern like "B1-B1" at end, keep first part
        name = re.sub(r'[-_][Bb]\d+[-_][Bb]\d+$', '', name)

        # Pattern 4: Clean up trailing separators
        name = re.sub(r'[-_]+$', '', name)

        return name.strip() or batch_name
    def _extract_day_from_name(self, batch_name):
        """Extract day from batch name. Handles:
        - 'MUMBAI SCHOOL-B1' -> D1 (B1 means Day 1)
        - 'Pune_Email_B1-B1-D5' -> D5
        - 'a-D3' -> D3
        - 'Master_Lead-B2' -> D1 (B2 = Day 1, second batch)
        """
        if not batch_name:
            return "D1"

        # Look for -D<number> first (explicit day)
        m = re.search(r'[-_]D(\d+)', batch_name, re.IGNORECASE)
        if m:
            dn = m.group(1)
            if dn in ["1", "3", "5", "7", "10"]:
                return f"D{dn}"

        # Look for -B<number> — B1=Day1, B2=Day1 (second batch), B3=Day3, etc.
        m = re.search(r'[-_]B(\d+)', batch_name, re.IGNORECASE)
        if m:
            bn = int(m.group(1))
            # Map batch number to day: B1/B2=Day1, B3=Day3, B5=Day5, etc.
            day_map = {1: 1, 2: 1, 3: 3, 4: 3, 5: 5, 6: 5, 7: 7, 8: 7, 9: 10, 10: 10}
            day = day_map.get(bn, 1)
            return f"D{day}"

        return "D1"
    def _render_pipeline_card(self, family_name, days):
        """Compact symmetrical pipeline card. All 5 pills fit in one row."""
        card = ctk.CTkFrame(self.batches_frame, fg_color=C_PANEL, corner_radius=10,
                           border_width=1, border_color="#1e3a5f")
        card.pack(fill="x", pady=6, padx=6)

        # Header
        header = ctk.CTkFrame(card, fg_color="transparent", height=24)
        header.pack(fill="x", padx=10, pady=(8, 2))
        header.pack_propagate(False)

        seq_id = ""
        family_total = 0
        # Calculate family total from ALL batches in family
        for day_code in ["D1", "D3", "D5", "D7", "D10"]:
            b = days.get(day_code)
            if b and isinstance(b, dict):
                if not seq_id:
                    seq_id = b.get("sequence_id", "").upper()
                try:
                    counts = self.engine.db.batch_count_by_status(b["id"])
                    family_total = max(family_total, sum(counts.values()))
                except:
                    pass
        total_leads = family_total

        name_color = C_ACCENT if seq_id == "SCHOOL" else C_WARNING if seq_id == "CSR" else "white"
        ctk.CTkLabel(header, text=family_name, font=("Segoe UI", 13, "bold"),
                    text_color=name_color).pack(side="left")
        if total_leads > 0:
            ctk.CTkLabel(header, text=f"  •  {total_leads} recipients", font=("Segoe UI", 9),
                        text_color=C_TEXT_DIM).pack(side="left")

        # Pills row - RESPONSIVE GRID (auto-fits any screen width)
        pills_row = ctk.CTkFrame(card, fg_color="transparent")
        pills_row.pack(fill="x", padx=6, pady=(2, 8))
        # 5 equal columns that stretch to fill available width
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
            total = family_total  # Use family total for consistency
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
            actual_status = status
            if status == "COMPLETED" and sent < total and total > 0:
                actual_status = "DRAFT"
            # FIX: If RUNNING but 0 sent, show as Ready (not started yet)
            if actual_status == "RUNNING" and sent == 0:
                actual_status = "DRAFT"

            # Colors
            if actual_status == "COMPLETED":
                bg, border, accent = "#0d2b2b", "#0d9b8a", "#0d9b8a"
            elif actual_status in ["RUNNING", "SCHEDULED", "DRAFT"]:
                bg, border, accent = "#0d2b2b", "#0d9b8a", "#0d9b8a"
            elif actual_status == "PAUSED":
                bg, border, accent = "#2a2a1a", "#d29922", "#d29922"
            else:
                bg, border, accent = "#151528", "#2a2a4e", "#555577"

            # RESPONSIVE pill - uses grid, fills column, min height 155px
            pill = ctk.CTkFrame(pills_row, fg_color=bg, corner_radius=6,
                               border_width=1, border_color=border, height=155)
            pill.grid(row=0, column=col, padx=3, pady=2, sticky="nsew")
            pill.grid_propagate(False)

            # Day label + date on SAME LINE
            day_frame = ctk.CTkFrame(pill, fg_color="transparent", height=16)
            day_frame.pack(fill="x", padx=6, pady=(4, 0))
            day_frame.pack_propagate(False)

            ctk.CTkLabel(day_frame, text=day_label, font=("Segoe UI", 8, "bold"),
                        text_color=accent).pack(side="left")

            # Date beside day label
            from datetime import datetime, timedelta
            date_text = ""
            if scheduled:
                try:
                    dt = None
                    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S.%f"]:
                        try:
                            dt = datetime.strptime(scheduled, fmt)
                            break
                        except ValueError:
                            continue
                    if dt:
                        date_text = dt.strftime("%d %b")
                except:
                    pass
            else:
                base_date = datetime.now()
                projected = base_date + timedelta(days=day_num)
                date_text = projected.strftime("%d %b")
            if date_text:
                ctk.CTkLabel(day_frame, text=f"  {date_text}", font=("Segoe UI", 7),
                            text_color="#4a5a6a").pack(side="left")

            ctk.CTkLabel(pill, text=f"{sent}/{total}", font=("Segoe UI", 13, "bold"),
                        text_color="white").pack(anchor="w", padx=6, pady=(0, 0))

            # Status line (due count)
            if actual_status == "COMPLETED":
                st_text, st_color = "All sent", "#0d9b8a"
            elif due > 0 and actual_status not in ["NONE"]:
                st_text, st_color = f"{due} due", "#febe32"
            elif actual_status == "NONE" and total_leads > 0:
                st_text, st_color = f"{total_leads} to send", "#febe32"
            else:
                st_text, st_color = "", C_TEXT_DIM
            if st_text:
                ctk.CTkLabel(pill, text=st_text, font=("Segoe UI", 8),
                            text_color=st_color).pack(anchor="w", padx=6, pady=(0, 0))

            # State label
            states = {"COMPLETED": "Done", "RUNNING": "Sending", "SCHEDULED": "Scheduled",
                     "DRAFT": "Ready", "PAUSED": "Paused", "NONE": "Queue"}
            ctk.CTkLabel(pill, text=states.get(actual_status, ""), font=("Segoe UI", 7),
                        text_color="#5a6a7a").pack(anchor="w", padx=6, pady=(0, 0))



            # Buttons - fixed at bottom
            btn_frame = ctk.CTkFrame(pill, fg_color="transparent", height=20)
            btn_frame.pack(fill="x", padx=3, pady=(2, 4))
            btn_frame.grid_columnconfigure(0, weight=1)
            btn_frame.grid_columnconfigure(1, weight=1)
            btn_frame.pack_propagate(False)

            # FIX: COMPLETED shows no action button
            if actual_status == "COMPLETED":
                action_text = None
            elif actual_status in ["DRAFT", "SCHEDULED", "PAUSED"]:
                action_text, action_color = "▶", "#0d9b8a"
            elif actual_status == "RUNNING":
                action_text, action_color = "⏸", "#d29922"
            else:
                action_text, action_color = "▶", "#3a3a5e"

            if action_text:
                ctk.CTkButton(btn_frame, text=action_text, font=("Segoe UI", 8, "bold"),
                             fg_color=action_color, hover_color=action_color,
                             text_color="white", corner_radius=3, height=20,
                             command=lambda b=batch_id, s=actual_status, d=day_num, f=family_name, sq=seq_id: self._on_pill_click(b, s, d, f, sq)
                             ).grid(row=0, column=0, padx=(0, 1), sticky="nsew")
            else:
                ctk.CTkFrame(btn_frame, fg_color="transparent", height=20).grid(row=0, column=0, padx=(0, 1), sticky="nsew")

            ctk.CTkButton(btn_frame, text="📊", font=("Segoe UI", 7),
                         fg_color="#1a1a3e", hover_color="#2a2a5e",
                         text_color="white", corner_radius=3, height=20,
                         command=lambda b=batch_id, f=family_name, d=day_num: self._show_pill_report(b, f, d)
                         ).grid(row=0, column=1, padx=(1, 0), sticky="nsew")

            if batch_id:
                pill.bind("<Button-1>", lambda e, b=batch_id: self._show_batch_details(b))

    def _on_pill_click(self, batch_id, status, day_num, family_name, seq_id):
        """Handle click on active pill button — start batch or create if missing."""
        if batch_id:
            if status in ["DRAFT", "SCHEDULED", "PAUSED"]:
                self._start_batch(batch_id)
            elif status == "RUNNING":
                self._pause_batch(batch_id)
            else:
                self._show_batch_details(batch_id)
        else:
            # No batch exists — create one for this day
            self._create_day_batch(family_name, day_num, seq_id)


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
            from datetime import datetime, timedelta
            # Schedule for +2 days at 10 AM
            scheduled = (datetime.now() + timedelta(days=2)).replace(hour=10, minute=0, second=0)
            scheduled_str = scheduled.strftime("%Y-%m-%d %H:%M:%S")

            batch_name = f"{family_name}-D{day_num}"
            # Copy recipients from Day 1 batch if exists
            day1_batch = None
            batches = self.engine.db.batch_get_all()
            for b in batches:
                if b.get("name", "").startswith(family_name) and "-D1" in b.get("name", ""):
                    day1_batch = b
                    break

            if day1_batch:
                # Create batch with same recipients
                new_batch_id = self.engine.db.batch_create(
                    name=batch_name,
                    sequence_id=seq_id.lower(),
                    scheduled_at=scheduled_str
                )
                # Copy recipients from Day 1
                recipients = self.engine.db.batch_get_recipients(day1_batch["id"])
                for r in recipients:
                    self.engine.db.batch_add_recipient(new_batch_id, r["id"])

                self._log_activity(f"Created {batch_name} from {day1_batch['name']}")
                self._refresh_batch_list()
                self._refresh_dashboard()
            else:
                self._log_activity(f"Cannot create {batch_name}: No Day 1 batch found")
        except Exception as e:
            self._log_activity(f"Error creating day batch: {e}")

    def _create_batch_card(self, batch):
        """Create a batch summary card."""
        card = ctk.CTkFrame(self.batches_frame, fg_color=C_PANEL, corner_radius=8)
        card.pack(fill="x", pady=5)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkLabel(top, text=batch["name"], font=("Segoe UI", 14, "bold"),
                    text_color=C_ACCENT).pack(side="left")

        status_color = C_SUCCESS if batch["status"] == "running" else C_WARNING if batch["status"] == "scheduled" else C_TEXT_DIM
        ctk.CTkLabel(top, text=batch["status"].upper(), font=("Segoe UI", 10),
                    text_color=status_color).pack(side="right")

        # Progress
        try:
            counts = self.engine.db.batch_count_by_status(batch["id"])
            total = sum(counts.values())
            sent = counts.get("sent", 0)
            progress = f"{sent}/{total} sent"
        except:
            progress = "Loading..."

        ctk.CTkLabel(card, text=f"{batch['sequence_id'].upper()} | {progress}",
                    font=("Segoe UI", 10), text_color=C_TEXT_DIM).pack(anchor="w", padx=15, pady=(0, 10))

    # ═══════════════════════════════════════════════════════════
    #  CHAT VIEW (Existing, slightly enhanced)
    # ═══════════════════════════════════════════════════════════
    def _build_chat_view(self):
        view = ctk.CTkFrame(self.content, fg_color="transparent")
        self.views["chat"] = view
        view.grid_columnconfigure(0, weight=1)
        view.grid_rowconfigure(0, weight=1)
        view.grid_rowconfigure(1, weight=0)

        # Messages area
        self.messages_container = ctk.CTkScrollableFrame(view, fg_color=C_PANEL)
        self.messages_container.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        # Input area
        input_frame = ctk.CTkFrame(view, fg_color="transparent")
        input_frame.grid(row=1, column=0, sticky="ew")

        self.chat_input = ctk.CTkEntry(input_frame, placeholder_text="Command Raj...",
                                       font=("Segoe UI", 12))
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.chat_input.bind("<Return>", lambda e: self._send_chat())

        ctk.CTkButton(input_frame, text="Send", width=80,
                     command=self._send_chat).pack(side="right")

        # Welcome message
        self._add_message("raj", "🤖 Raj v4.2 online — RoboPirate Command Center. Dashboard shows live pipeline. Say 'help' for commands.")

    def _send_chat(self):
        text = self.chat_input.get().strip()
        if not text:
            return
        self.chat_input.delete(0, "end")
        self._add_message("user", text)

        # Process command - brain returns dict, extract response text
        try:
            reply = self.brain.process(text)
            # Handle both old string returns and new dict returns
            if isinstance(reply, dict):
                response_text = reply.get("response", str(reply))
            else:
                response_text = str(reply)
            self._add_message("raj", response_text)
        except Exception as e:
            self._add_message("raj", f"I encountered an error processing that, sir. ({str(e)[:100]})")
            import traceback
            print(f"Brain error: {traceback.format_exc()}")

        self._log_activity(f"Chat: {text[:50]}")

    def _add_message(self, sender, text):
        is_raj = sender == "raj"
        bubble = ctk.CTkFrame(self.messages_container,
                             fg_color=C_PANEL if is_raj else "#2a2a4a",
                             corner_radius=12)
        bubble.pack(fill="x", pady=5, padx=10, anchor="w" if is_raj else "e")

        ctk.CTkLabel(bubble, text=text, font=("Segoe UI", 11),
                    text_color=C_TEXT, wraplength=600, justify="left").pack(padx=12, pady=8)


    # ═══════════════════════════════════════════════════════════
    #  IMPORT VIEW (Smart Import & Auto-Batch)
    # ═══════════════════════════════════════════════════════════
    def _build_import_view(self):
        view = ctk.CTkFrame(self.content, fg_color="transparent")
        self.views["import"] = view
        view.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(view, text="📥 Smart Import", font=("Segoe UI", 28, "bold"),
                    text_color="white").grid(row=0, column=0, sticky="w", pady=(0, 10))

        ctk.CTkLabel(view, text="Upload any file — Excel, CSV, or TXT. I'll auto-detect columns and create batches.",
                    font=("Segoe UI", 12), text_color=C_TEXT_DIM).grid(row=1, column=0, sticky="w", pady=(0, 20))

        # === STEP 1: SELECT FILE ===
        step1 = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=12)
        step1.grid(row=2, column=0, sticky="ew", pady=(0, 15))

        ctk.CTkLabel(step1, text="Step 1: Select File", font=("Segoe UI", 16, "bold"),
                    text_color=C_ACCENT).pack(anchor="w", padx=15, pady=(15, 10))

        file_frame = ctk.CTkFrame(step1, fg_color="transparent")
        file_frame.pack(fill="x", padx=15, pady=5)

        self.import_file_path = ctk.CTkEntry(file_frame, placeholder_text="No file selected...", state="readonly")
        self.import_file_path.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(file_frame, text="📁 Browse", command=self._browse_import_file,
                     fg_color=C_ACCENT, width=100).pack(side="left")

        # === STEP 2: CONFIGURE ===
        step2 = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=12)
        step2.grid(row=3, column=0, sticky="ew", pady=(0, 15))

        ctk.CTkLabel(step2, text="Step 2: Configure", font=("Segoe UI", 16, "bold"),
                    text_color=C_ACCENT).pack(anchor="w", padx=15, pady=(15, 10))

        cfg_frame = ctk.CTkFrame(step2, fg_color="transparent")
        cfg_frame.pack(fill="x", padx=15, pady=5)

        # Sequence
        ctk.CTkLabel(cfg_frame, text="Sequence:", font=("Segoe UI", 11), text_color=C_TEXT).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.import_seq_var = ctk.StringVar(value="school")
        ctk.CTkOptionMenu(cfg_frame, values=["school", "csr"], variable=self.import_seq_var, width=150).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Batch size
        ctk.CTkLabel(cfg_frame, text="Batch Size:", font=("Segoe UI", 11), text_color=C_TEXT).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.import_batch_size = ctk.CTkOptionMenu(cfg_frame, values=["50", "100", "150", "200"], width=100)
        self.import_batch_size.set("50")
        self.import_batch_size.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Batch name prefix
        ctk.CTkLabel(cfg_frame, text="Batch Prefix:", font=("Segoe UI", 11), text_color=C_TEXT).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.import_prefix = ctk.CTkEntry(cfg_frame, placeholder_text="e.g., Pune-Schools")
        self.import_prefix.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        # Start day
        ctk.CTkLabel(cfg_frame, text="Start Day:", font=("Segoe UI", 11), text_color=C_TEXT).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.import_start_day = ctk.CTkOptionMenu(cfg_frame, values=["1", "3", "5", "7", "10"], width=100)
        self.import_start_day.set("1")
        self.import_start_day.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # === STEP 3: ANALYZE & PREVIEW ===
        step3 = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=12)
        step3.grid(row=4, column=0, sticky="ew", pady=(0, 15))

        ctk.CTkLabel(step3, text="Step 3: Analyze & Preview", font=("Segoe UI", 16, "bold"),
                    text_color=C_ACCENT).pack(anchor="w", padx=15, pady=(15, 10))

        preview_btn_frame = ctk.CTkFrame(step3, fg_color="transparent")
        preview_btn_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(preview_btn_frame, text="🔍 Analyze File", command=self._analyze_import_file,
                     fg_color=C_WARNING, width=140).pack(side="left", padx=5)
        ctk.CTkButton(preview_btn_frame, text="👁 Preview Rows", command=self._preview_import_rows,
                     fg_color=C_PANEL, width=140).pack(side="left", padx=5)

        # Analysis results display
        self.import_analysis_frame = ctk.CTkFrame(step3, fg_color="transparent")
        self.import_analysis_frame.pack(fill="x", padx=15, pady=(5, 15))

        self.import_analysis_text = ctk.CTkLabel(self.import_analysis_frame, text="Click Analyze to see detected columns...",
                                                  font=("Segoe UI", 11), text_color=C_TEXT_DIM, wraplength=800, justify="left")
        self.import_analysis_text.pack(anchor="w")

        # === STEP 4: IMPORT ===
        step4 = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=12)
        step4.grid(row=5, column=0, sticky="ew", pady=(0, 15))

        ctk.CTkLabel(step4, text="Step 4: Import & Create Batches", font=("Segoe UI", 16, "bold"),
                    text_color=C_ACCENT).pack(anchor="w", padx=15, pady=(15, 10))

        btn_frame = ctk.CTkFrame(step4, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(5, 5))

        ctk.CTkButton(btn_frame, text="📥 Import to Pool Only", command=self._run_pool_import,
                     fg_color=C_ACCENT, height=35, font=("Segoe UI", 12, "bold"),
                     hover_color="#00a8cc").pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text="🚀 Legacy: Import + Auto-Batch", command=self._run_smart_import,
                     fg_color=C_SUCCESS, height=35, font=("Segoe UI", 11),
                     hover_color="#2ecc71").pack(side="left", padx=5)

        # Pool status display
        self.pool_status_frame = ctk.CTkFrame(step4, fg_color="transparent")
        self.pool_status_frame.pack(fill="x", padx=15, pady=(5, 15))

        self.pool_status_text = ctk.CTkLabel(self.pool_status_frame, text="",
                                              font=("Segoe UI", 11), text_color=C_TEXT_DIM, wraplength=800, justify="left")
        self.pool_status_text.pack(anchor="w")

        # Results
        self.import_result_frame = ctk.CTkFrame(step4, fg_color="transparent")
        self.import_result_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.import_result_text = ctk.CTkLabel(self.import_result_frame, text="",
                                                font=("Segoe UI", 12), text_color=C_TEXT, wraplength=800, justify="left")
        self.import_result_text.pack(anchor="w")

    def _browse_import_file(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("Text files", "*.txt *.tsv"),
                ("All files", "*.*")
            ]
        )
        if path:
            self.import_file_path.configure(state="normal")
            self.import_file_path.delete(0, "end")
            self.import_file_path.insert(0, path)
            self.import_file_path.configure(state="readonly")
            # Auto-set prefix from filename
            from pathlib import Path
            prefix = Path(path).stem[:20]
            self.import_prefix.delete(0, "end")
            self.import_prefix.insert(0, prefix)

    def _analyze_import_file(self):
        path = self.import_file_path.get()
        if not path or path == "No file selected...":
            self.import_analysis_text.configure(text="❌ Please select a file first.", text_color=C_DANGER)
            return

        if not SMART_IMPORT_AVAILABLE:
            self.import_analysis_text.configure(text="❌ smart_importer.py not found. Please ensure it's in the same folder.", text_color=C_DANGER)
            return

        try:
            importer = SmartImporter(self.engine.db, self.engine)
            result = importer.analyze_file(path)

            lines = [f"📁 {result.get('filename', '')} — {result.get('total_rows', 0)} rows", ""]
            lines.append("🔍 Detected columns:")

            mapping = result.get("mapping", {})
            confidence = result.get("confidence", {})
            for key, val in mapping.items():
                if val:
                    conf = confidence.get(key, (val, "medium"))
                    conf_str = conf[1] if isinstance(conf, tuple) else "medium"
                    color_emoji = "🟢" if "high" in conf_str else "🟡" if "medium" in conf_str else "🔴"
                    lines.append(f"  {color_emoji} {key.capitalize()}: '{val}' ({conf_str})")

            lines.append("")
            lines.append(f"✅ Valid emails: {result.get('valid_emails', 0)}")
            lines.append(f"❌ Invalid emails: {result.get('invalid_emails', 0)}")

            if result.get("ready_to_import"):
                lines.append("\n✅ Ready to import!")
                self.import_analysis_text.configure(text="\n".join(lines), text_color=C_SUCCESS)
            else:
                lines.append("\n⚠️ Email column not confidently detected. Check your file headers.")
                self.import_analysis_text.configure(text="\n".join(lines), text_color=C_WARNING)

        except Exception as e:
            self.import_analysis_text.configure(text=f"❌ Analysis error: {str(e)[:200]}", text_color=C_DANGER)

    def _preview_import_rows(self):
        path = self.import_file_path.get()
        if not path or path == "No file selected...":
            self.import_analysis_text.configure(text="❌ Please select a file first.", text_color=C_DANGER)
            return

        try:
            importer = SmartImporter(self.engine.db, self.engine)
            result = importer.get_import_preview(path, max_rows=5)

            lines = ["📋 Preview (first 5 rows):", ""]
            for i, row in enumerate(result.get("preview", []), 1):
                lines.append(f"Row {i}: {row.get('name', '')} <{row.get('email', '')}> @ {row.get('org', '')}")
                if row.get("extra_fields"):
                    extras = ", ".join([f"{k}={v}" for k, v in list(row["extra_fields"].items())[:3]])
                    lines.append(f"    Extras: {extras}")

            unmapped = result.get("unmapped_columns", [])
            if unmapped:
                lines.append(f"\n📎 Extra columns (will be stored): {', '.join(unmapped[:5])}")

            self.import_analysis_text.configure(text="\n".join(lines), text_color=C_TEXT)

        except Exception as e:
            self.import_analysis_text.configure(text=f"❌ Preview error: {str(e)[:200]}", text_color=C_DANGER)

    def _run_smart_import(self):
        path = self.import_file_path.get()
        if not path or path == "No file selected...":
            self.import_result_text.configure(text="❌ Please select a file first.", text_color=C_DANGER)
            return

        seq = self.import_seq_var.get()
        batch_size = int(self.import_batch_size.get())
        prefix = self.import_prefix.get().strip() or "Import"
        start_day = int(self.import_start_day.get())

        self.import_result_text.configure(text="⏳ Importing... please wait.", text_color=C_ACCENT)
        self.update_idletasks()

        try:
            importer = SmartImporter(self.engine.db, self.engine)
            result = importer.import_leads(
                path, seq,
                batch_size=batch_size,
                auto_create_batches=True,
                batch_name_prefix=prefix,
                start_day=start_day
            )

            if result.get("success"):
                lines = [f"✅ Import complete!", ""]
                lines.append(f"📊 Imported: {result.get('imported', 0)} leads")
                lines.append(f"⏭️ Skipped: {result.get('skipped', 0)} (blacklisted: {result.get('blacklisted', 0)})")

                batches = result.get("batches", [])
                if batches:
                    lines.append("")
                    lines.append(f"🚀 Created {len(batches)} batches:")
                    for b in batches:
                        lines.append(f"  • {b['name']}: {b['recipients']} recipients — {b['status'].upper()}")
                    lines.append("")
                    lines.append("👉 Go to Batches tab to start sending!")

                self.import_result_text.configure(text="\n".join(lines), text_color=C_SUCCESS)
                self._refresh_batches_list()
                self._refresh_dashboard()
                self._add_message("raj", f"Smart import done! {result.get('imported', 0)} leads imported into {len(batches)} batches.")
            else:
                self.import_result_text.configure(text=f"❌ Import failed: {result.get('error', 'Unknown error')}", text_color=C_DANGER)

        except Exception as e:
            import traceback
            self.import_result_text.configure(text=f"❌ Error: {str(e)[:200]}\n\n{traceback.format_exc()[:300]}", text_color=C_DANGER)

    def _run_pool_import(self):
        """Import leads to pool only (no batch creation)."""
        path = self.import_file_path.get()
        if not path or path == "No file selected...":
            self.import_result_text.configure(text="❌ Please select a file first.", text_color=C_DANGER)
            return

        seq = self.import_seq_var.get()
        self.import_result_text.configure(text="⏳ Importing to pool... please wait.", text_color=C_ACCENT)
        self.update_idletasks()

        try:
            result = self.engine.smart_import(path, seq)

            if result.get("success"):
                lines = [f"✅ Pool import complete!", ""]
                lines.append(f"📊 Imported: {result.get('imported', 0)} leads")
                lines.append(f"⏭️ Skipped: {result.get('skipped', 0)} (blacklisted: {result.get('blacklisted', 0)}, duplicates: {result.get('duplicates', 0)})")
                lines.append(f"📦 Pool: {result.get('pool_count', 0)} unbatched / {result.get('total_in_sequence', 0)} total in {seq.upper()}")
                lines.append("")
                lines.append("👉 Go to Batches tab → 'Create from Pool' to make batches")

                self.import_result_text.configure(text="\n".join(lines), text_color=C_SUCCESS)
                self._update_pool_status_display()
                self._refresh_dashboard()
                self._add_message("raj", f"Pool import done! {result.get('imported', 0)} leads in {seq.upper()} pool.")
            else:
                self.import_result_text.configure(text=f"❌ Pool import failed: {result.get('error', 'Unknown error')}", text_color=C_DANGER)

        except Exception as e:
            import traceback
            self.import_result_text.configure(text=f"❌ Error: {str(e)[:200]}\n\n{traceback.format_exc()[:300]}", text_color=C_DANGER)

    def _update_pool_status_display(self):
        """Update pool status text in import tab."""
        try:
            school_pool = self.engine.get_pool_count("school")
            csr_pool = self.engine.get_pool_count("csr")
            lines = ["📦 Current Pool Status:", ""]
            lines.append(f"  📚 SCHOOL: {school_pool} unbatched leads available")
            lines.append(f"  🏢 CSR:    {csr_pool} unbatched leads available")
            lines.append("")
            if school_pool > 0 or csr_pool > 0:
                lines.append("Go to Batches tab and use 'Create from Pool' to batch them.")
            else:
                lines.append("Pools are empty. Import more leads above.")
            self.pool_status_text.configure(text="\n".join(lines), text_color=C_TEXT)
        except:
            pass

    # ═══════════════════════════════════════════════════════════
    #  TEMPLATES VIEW (Enhanced with source tracking)
    # ═══════════════════════════════════════════════════════════
    def _build_templates_view(self):
        view = ctk.CTkFrame(self.content, fg_color="transparent")
        self.views["templates"] = view
        view.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(view, text="📝 Templates", font=("Segoe UI", 24, "bold"),
                    text_color="white").grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Controls
        ctrl = ctk.CTkFrame(view, fg_color="transparent")
        ctrl.grid(row=1, column=0, sticky="ew", pady=(0, 15))

        ctk.CTkButton(ctrl, text="🔄 Sync from Gmail", command=self._sync_templates,
                     fg_color=C_ACCENT).pack(side="left", padx=5)
        ctk.CTkButton(ctrl, text="✨ Auto-Generate Missing", command=self._auto_generate_missing,
                     fg_color=C_WARNING).pack(side="left", padx=5)
        ctk.CTkButton(ctrl, text="🔒 Lock All", command=self._lock_all_templates,
                     fg_color=C_SUCCESS).pack(side="left", padx=5)

        # Template grid
        self.template_grid = ctk.CTkFrame(view, fg_color="transparent")
        self.template_grid.grid(row=2, column=0, sticky="nsew")

        # SCHOOL row
        ctk.CTkLabel(self.template_grid, text="SCHOOL", font=("Segoe UI", 16, "bold"),
                    text_color=C_ACCENT).grid(row=0, column=0, columnspan=5, sticky="w", pady=(20, 5))

        for col, day in enumerate([1, 3, 5, 7, 10]):
            card = ctk.CTkFrame(self.template_grid, fg_color=C_PANEL, corner_radius=8, height=120)
            card.grid(row=1, column=col, padx=8, pady=8, sticky="ew")
            card.grid_propagate(False)

            ctk.CTkLabel(card, text=f"Day {day}", font=("Segoe UI", 12, "bold"),
                        text_color=C_ACCENT).pack(pady=(10, 2))

            status_lbl = ctk.CTkLabel(card, text="Not synced", font=("Segoe UI", 10),
                                     text_color=C_DANGER)
            status_lbl.pack()

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(pady=(5, 0))

            preview_btn = ctk.CTkButton(btn_frame, text="👁", width=30, height=22,
                                       fg_color=C_PANEL, hover_color=C_ACCENT,
                                       command=lambda s="school", d=day: self._preview_template(s, d))
            preview_btn.pack(side="left", padx=2)

            gen_btn = ctk.CTkButton(btn_frame, text="✨", width=30, height=22,
                                   fg_color=C_PANEL, hover_color=C_ACCENT,
                                   command=lambda s="school", d=day: self._generate_template(s, d))
            gen_btn.pack(side="left", padx=2)

            lock_btn = ctk.CTkButton(btn_frame, text="🔒", width=30, height=22,
                                    fg_color=C_PANEL, hover_color=C_WARNING,
                                    command=lambda s="school", d=day: self._lock_template(s, d))
            lock_btn.pack(side="left", padx=2)

            self.template_cards[f"school_{day}"] = (status_lbl, preview_btn, gen_btn, lock_btn)

        # CSR row
        ctk.CTkLabel(self.template_grid, text="CSR", font=("Segoe UI", 16, "bold"),
                    text_color=C_WARNING).grid(row=2, column=0, columnspan=5, sticky="w", pady=(20, 5))

        for col, day in enumerate([1, 3, 5, 7, 10]):
            card = ctk.CTkFrame(self.template_grid, fg_color=C_PANEL, corner_radius=8, height=120)
            card.grid(row=3, column=col, padx=8, pady=8, sticky="ew")
            card.grid_propagate(False)

            ctk.CTkLabel(card, text=f"Day {day}", font=("Segoe UI", 12, "bold"),
                        text_color=C_WARNING).pack(pady=(10, 2))

            status_lbl = ctk.CTkLabel(card, text="Not synced", font=("Segoe UI", 10),
                                     text_color=C_DANGER)
            status_lbl.pack()

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(pady=(5, 0))

            preview_btn = ctk.CTkButton(btn_frame, text="👁", width=30, height=22,
                                       fg_color=C_PANEL, hover_color=C_WARNING,
                                       command=lambda s="csr", d=day: self._preview_template(s, d))
            preview_btn.pack(side="left", padx=2)

            gen_btn = ctk.CTkButton(btn_frame, text="✨", width=30, height=22,
                                   fg_color=C_PANEL, hover_color=C_WARNING,
                                   command=lambda s="csr", d=day: self._generate_template(s, d))
            gen_btn.pack(side="left", padx=2)

            lock_btn = ctk.CTkButton(btn_frame, text="🔒", width=30, height=22,
                                    fg_color=C_PANEL, hover_color=C_WARNING,
                                    command=lambda s="csr", d=day: self._lock_template(s, d))
            lock_btn.pack(side="left", padx=2)

            self.template_cards[f"csr_{day}"] = (status_lbl, preview_btn, gen_btn, lock_btn)

    # ═══════════════════════════════════════════════════════════
    #  BATCHES VIEW (NEW)
    # ═══════════════════════════════════════════════════════════
    def _build_batches_view(self):
        view = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        self.views["batches"] = view
        view.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(view, text="🚀 Batch Manager", font=("Segoe UI", 24, "bold"),
                    text_color="white").grid(row=0, column=0, sticky="w", pady=(0, 20))

        # === CREATE FROM POOL SECTION ===
        pool_frame = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=12)
        pool_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))

        ctk.CTkLabel(pool_frame, text="🎯 Create Batch from Pool", font=("Segoe UI", 16, "bold"),
                    text_color=C_SUCCESS).pack(anchor="w", padx=15, pady=(15, 10))

        pool_cfg = ctk.CTkFrame(pool_frame, fg_color="transparent")
        pool_cfg.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(pool_cfg, text="Sequence:", font=("Segoe UI", 11), text_color=C_TEXT).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.pool_seq_var = ctk.StringVar(value="school")
        self.pool_seq_dropdown = ctk.CTkOptionMenu(pool_cfg, values=["school", "csr"], 
                                                    variable=self.pool_seq_var, width=150,
                                                    command=self._on_pool_seq_change)
        self.pool_seq_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(pool_cfg, text="Available:", font=("Segoe UI", 11), text_color=C_TEXT).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.pool_count_label = ctk.CTkLabel(pool_cfg, text="Loading...", font=("Segoe UI", 11, "bold"),
                                            text_color=C_ACCENT)
        self.pool_count_label.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(pool_cfg, text="Batch Size:", font=("Segoe UI", 11), text_color=C_TEXT).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.pool_batch_size = ctk.CTkOptionMenu(pool_cfg, values=["10", "25", "50", "100"], width=100)
        self.pool_batch_size.set("50")
        self.pool_batch_size.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(pool_cfg, text="Day Offset:", font=("Segoe UI", 11), text_color=C_TEXT).grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.pool_day_offset = ctk.CTkOptionMenu(pool_cfg, values=["1", "3", "5", "7", "10"], width=100)
        self.pool_day_offset.set("1")
        self.pool_day_offset.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(pool_cfg, text="Name:", font=("Segoe UI", 11), text_color=C_TEXT).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.pool_batch_name = ctk.CTkEntry(pool_cfg, placeholder_text="Auto-generated")
        self.pool_batch_name.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        ctk.CTkButton(pool_frame, text="🚀 Create from Pool", command=self._create_batch_from_pool,
                     fg_color=C_SUCCESS, height=35, font=("Segoe UI", 12, "bold")).pack(pady=(10, 15))

        # === LEGACY MANUAL BATCH CREATION ===
        create_frame = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=12)
        create_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(create_frame, text="✋ Manual Batch Creation", font=("Segoe UI", 16, "bold"),
                    text_color=C_ACCENT).pack(anchor="w", padx=15, pady=(15, 10))

        # Batch name
        name_frame = ctk.CTkFrame(create_frame, fg_color="transparent")
        name_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(name_frame, text="Name:", font=("Segoe UI", 11), text_color=C_TEXT).pack(side="left")
        self.batch_name_entry = ctk.CTkEntry(name_frame, placeholder_text="e.g., Pune Schools Batch 1")
        self.batch_name_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))

        # Sequence
        seq_frame = ctk.CTkFrame(create_frame, fg_color="transparent")
        seq_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(seq_frame, text="Sequence:", font=("Segoe UI", 11), text_color=C_TEXT).pack(side="left")
        self.batch_seq_var = ctk.StringVar(value="school")
        ctk.CTkOptionMenu(seq_frame, values=["school", "csr"], variable=self.batch_seq_var,
                         width=150).pack(side="left", padx=(10, 0))

        # Schedule
        sched_frame = ctk.CTkFrame(create_frame, fg_color="transparent")
        sched_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(sched_frame, text="Schedule:", font=("Segoe UI", 11), text_color=C_TEXT).pack(side="left")
        self.batch_sched_var = ctk.StringVar(value="immediate")
        ctk.CTkOptionMenu(sched_frame, values=["immediate", "tomorrow_10am", "custom"],
                         variable=self.batch_sched_var, width=150).pack(side="left", padx=(10, 0))

        # Send rate
        rate_frame = ctk.CTkFrame(create_frame, fg_color="transparent")
        rate_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(rate_frame, text="Send Rate:", font=("Segoe UI", 11), text_color=C_TEXT).pack(side="left")
        self.batch_rate_var = ctk.StringVar(value="all")
        ctk.CTkOptionMenu(rate_frame, values=["all_at_once", "1_per_minute", "1_per_2min", "1_per_5min"],
                         variable=self.batch_rate_var, width=150).pack(side="left", padx=(10, 0))

        # Recipients selection
        recip_frame = ctk.CTkFrame(create_frame, fg_color="transparent")
        recip_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(recip_frame, text="Recipients:", font=("Segoe UI", 11), text_color=C_TEXT).pack(side="left")
        ctk.CTkButton(recip_frame, text="📁 Import XLSX", command=self._import_batch_recipients,
                     fg_color=C_ACCENT, width=120).pack(side="left", padx=(10, 5))
        ctk.CTkButton(recip_frame, text="📋 Select from DB", command=self._select_db_recipients,
                     fg_color=C_PANEL, width=120).pack(side="left", padx=5)

        self.batch_recipients_label = ctk.CTkLabel(create_frame, text="0 recipients selected",
                                                  font=("Segoe UI", 10), text_color=C_TEXT_DIM)
        self.batch_recipients_label.pack(anchor="w", padx=15, pady=5)

        # Create button
        ctk.CTkButton(create_frame, text="🚀 Create Batch", command=self._create_batch,
                     fg_color=C_SUCCESS, height=35, font=("Segoe UI", 12, "bold")).pack(pady=(10, 15))

        # Existing batches list
        ctk.CTkLabel(view, text="Existing Batches", font=("Segoe UI", 18, "bold"),
                    text_color="white").grid(row=3, column=0, sticky="w", pady=(20, 10))

        self.batches_list_frame = ctk.CTkFrame(view, fg_color="transparent")
        self.batches_list_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 20))

        self._refresh_batches_list()


    def _build_replies_view(self):
        """Replies tab — split pane: left list, right detail."""
        view = ctk.CTkFrame(self.content, fg_color="transparent")
        self.views["replies"] = view
        view.grid_columnconfigure(0, weight=1)
        view.grid_columnconfigure(1, weight=2)
        view.grid_rowconfigure(0, weight=1)

        # LEFT: Reply list
        left = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(1, weight=1)

        # Filter tabs
        filter_frame = ctk.CTkFrame(left, fg_color="transparent")
        filter_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.reply_filter = ctk.StringVar(value="all")
        filters = [("all", "All"), ("positive", "🟢"), ("neutral", "🔵"), 
                   ("hostile", "🔴"), ("drafted", "✍️"), ("handled", "✅")]
        for val, text in filters:
            ctk.CTkRadioButton(filter_frame, text=text, variable=self.reply_filter,
                              value=val, command=self._refresh_replies,
                              font=("Segoe UI", 11)).pack(side="left", padx=5)

        # Scrollable list
        self.replies_list = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.replies_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # RIGHT: Detail view
        right = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(3, weight=1)

        # Detail header
        self.reply_detail_header = ctk.CTkLabel(right, text="Select a reply →",
                                                font=("Segoe UI", 18, "bold"), text_color="white")
        self.reply_detail_header.grid(row=0, column=0, sticky="w", padx=15, pady=15)

        # Sentiment badge
        self.reply_sentiment = ctk.CTkLabel(right, text="", font=("Segoe UI", 12, "bold"))
        self.reply_sentiment.grid(row=1, column=0, sticky="w", padx=15)

        # Summary box
        self.reply_summary = ctk.CTkTextbox(right, height=80, wrap="word",
                                           font=("Segoe UI", 12), fg_color=C_BG)
        self.reply_summary.grid(row=2, column=0, sticky="ew", padx=15, pady=10)
        self.reply_summary.insert("0.0", "AI summary will appear here...")
        self.reply_summary.configure(state="disabled")

        # Original reply body
        self.reply_body = ctk.CTkTextbox(right, wrap="word",
                                         font=("Segoe UI", 12), fg_color=C_BG)
        self.reply_body.grid(row=3, column=0, sticky="nsew", padx=15, pady=10)
        self.reply_body.insert("0.0", "Original reply text will appear here...")
        self.reply_body.configure(state="disabled")

        # Draft preview
        draft_label = ctk.CTkLabel(right, text="🤖 AI Draft Reply:",
                                   font=("Segoe UI", 12, "bold"), text_color=C_TEXT_DIM)
        draft_label.grid(row=4, column=0, sticky="w", padx=15, pady=(6, 0))

        self.reply_draft = ctk.CTkTextbox(right, height=120, wrap="word",
                                          font=("Segoe UI", 12), fg_color=C_BG)
        self.reply_draft.grid(row=5, column=0, sticky="ew", padx=15, pady=10)
        self.reply_draft.insert("0.0", "AI draft will appear here...")
        self.reply_draft.configure(state="disabled")

        # Action buttons
        btn_frame = ctk.CTkFrame(right, fg_color="transparent")
        btn_frame.grid(row=6, column=0, sticky="ew", padx=15, pady=(0, 15))

        self.btn_generate_draft = ctk.CTkButton(btn_frame, text="🤖 Generate Draft",
                                                 font=("Segoe UI", 11), width=140,
                                                 fg_color=C_WARNING, state="disabled",
                                                 command=self._generate_draft_now)
        self.btn_generate_draft.pack(side="left", padx=(0, 8))

        self.btn_open_gmail = ctk.CTkButton(btn_frame, text="📧 Open in Gmail",
                                            font=("Segoe UI", 11), width=130,
                                            fg_color=C_ACCENT, state="disabled",
                                            command=self._open_reply_in_gmail)
        self.btn_open_gmail.pack(side="left", padx=(0, 8))

        self.btn_blacklist_reply = ctk.CTkButton(btn_frame, text="🚫 Blacklist",
                                                  font=("Segoe UI", 11), width=100,
                                                  fg_color=C_DANGER, state="disabled",
                                                  command=self._blacklist_from_reply)
        self.btn_blacklist_reply.pack(side="left", padx=(0, 8))

        self.btn_mark_handled = ctk.CTkButton(btn_frame, text="✅ Mark Handled",
                                               font=("Segoe UI", 11), width=120,
                                               fg_color=C_SUCCESS, state="disabled",
                                               command=self._mark_reply_handled)
        self.btn_mark_handled.pack(side="left")

        self.current_reply_id = None
        return view

    def _refresh_replies(self):
        """Load replies from DB and populate the list."""
        for widget in self.replies_list.winfo_children():
            widget.destroy()

        filt = self.reply_filter.get()
        try:
            if filt == "all":
                rows = self.engine.db.execute(
                    "SELECT id, from_addr, subject, body, sentiment, status, received_at, draft_reply_id, summary FROM replies ORDER BY received_at DESC"
                ).fetchall()
            else:
                rows = self.engine.db.execute(
                    "SELECT id, from_addr, subject, body, sentiment, status, received_at, draft_reply_id, summary FROM replies WHERE sentiment=? OR status=? ORDER BY received_at DESC",
                    (filt, filt)
                ).fetchall()
        except Exception as e:
            ctk.CTkLabel(self.replies_list, text=f"Error: {e}",
                        font=("Segoe UI", 12), text_color=C_DANGER).pack(pady=20)
            return

        if not rows:
            ctk.CTkLabel(self.replies_list, text="No replies yet.",
                        font=("Segoe UI", 14), text_color=C_TEXT_DIM).pack(pady=40)
            return

        for row in rows:
            r = dict(row)
            self._make_reply_card(r)

    def _make_reply_card(self, r: dict):
        """Build a single reply card for the list."""
        card = ctk.CTkFrame(self.replies_list, fg_color=C_BG, corner_radius=8,
                           border_width=1, border_color=C_TEXT_DIM)
        card.pack(fill="x", pady=4, padx=2)
        card.bind("<Button-1>", lambda e, rid=r["id"]: self._show_reply_detail(rid))

        # Top row: name + sentiment badge
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(8, 2))

        from_addr = r.get("from_addr", "Unknown")
        name = from_addr.split("@")[0].replace(".", " ").title() if "@" in from_addr else from_addr
        ctk.CTkLabel(top, text=name[:25], font=("Segoe UI", 13, "bold"),
                    text_color="white").pack(side="left")

        sentiment = r.get("sentiment", "neutral")
        # Badge colors: text color + background color (darker version)
        badge_colors = {
            "positive": (C_SUCCESS, "#1a4d2e"),
            "neutral": (C_ACCENT, "#1a3a4d"),
            "hostile": (C_DANGER, "#4d1a1a"),
            "unsubscribe": ("#6B7280", "#2d2d2d")
        }
        text_color, bg_color = badge_colors.get(sentiment, (C_TEXT_DIM, C_BG))
        ctk.CTkLabel(top, text=sentiment.upper(), font=("Segoe UI", 8, "bold"),
                    text_color=text_color, fg_color=bg_color,
                    corner_radius=6, width=60).pack(side="right")

        # Subject preview
        subj = r.get("subject", "No subject")
        ctk.CTkLabel(card, text=subj[:45], font=("Segoe UI", 11),
                    text_color=C_TEXT_DIM).pack(anchor="w", padx=10, pady=(0, 2))

        # Bottom: status + time
        bottom = ctk.CTkFrame(card, fg_color="transparent")
        bottom.pack(fill="x", padx=10, pady=(0, 8))

        status = r.get("status", "pending")
        status_emoji = {"pending": "⏳", "drafted": "✍️", "handled": "✅"}.get(status, "⏳")
        ctk.CTkLabel(bottom, text=f"{status_emoji} {status.upper()}",
                    font=("Segoe UI", 9), text_color=C_TEXT_DIM).pack(side="left")

        received = r.get("received_at", "")
        if received:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(received)
                time_str = dt.strftime("%d %b %H:%M")
            except:
                time_str = received[:16]
            ctk.CTkLabel(bottom, text=time_str, font=("Segoe UI", 9),
                        text_color=C_TEXT_DIM).pack(side="right")

    def _show_reply_detail(self, reply_id: int):
        """Show reply details in right pane."""
        self.current_reply_id = reply_id
        row = self.engine.db.execute(
            "SELECT * FROM replies WHERE id=?", (reply_id,)
        ).fetchone()
        if not row:
            return

        r = dict(row)

        # Header
        from_addr = r.get("from_addr", "Unknown")
        self.reply_detail_header.configure(text=f"📧 {from_addr}")

        # Sentiment badge
        sentiment = r.get("sentiment", "neutral")
        colors = {"positive": (C_SUCCESS, "#1a4d2e"), "neutral": (C_ACCENT, "#1a3a4d"), "hostile": (C_DANGER, "#4d1a1a")}
        text_color, bg_color = colors.get(sentiment, (C_TEXT_DIM, C_BG))
        self.reply_sentiment.configure(text=f"  {sentiment.upper()}  ",
                                       text_color=text_color,
                                       fg_color=bg_color,
                                       corner_radius=8)

        # Summary
        self.reply_summary.configure(state="normal")
        self.reply_summary.delete("0.0", "end")
        self.reply_summary.insert("0.0", r.get("summary", "No AI summary available."))
        self.reply_summary.configure(state="disabled")

        # Body
        self.reply_body.configure(state="normal")
        self.reply_body.delete("0.0", "end")
        body = r.get("body", "No body available.")
        self.reply_body.insert("0.0", body[:2000] if body else "No body available.")
        self.reply_body.configure(state="disabled")

        # Draft
        self.reply_draft.configure(state="normal")
        self.reply_draft.delete("0.0", "end")
        draft_id = r.get("draft_reply_id")
        if draft_id:
            self.reply_draft.insert("0.0", f"Draft created in Gmail (ID: {draft_id[:20]}...).\n\nOpen Gmail to review and send.")
        else:
            self.reply_draft.insert("0.0", "No draft yet. EOD run will generate one.")
        self.reply_draft.configure(state="disabled")

        # Enable buttons
        self.btn_generate_draft.configure(state="normal")
        self.btn_open_gmail.configure(state="normal")
        self.btn_blacklist_reply.configure(state="normal")
        self.btn_mark_handled.configure(state="normal")

    def _open_reply_in_gmail(self):
        """Open Gmail in browser to the reply thread."""
        if not self.current_reply_id:
            return
        row = self.engine.db.execute("SELECT thread_id FROM replies WHERE id=?",
                                      (self.current_reply_id,)).fetchone()
        if row:
            import webbrowser
            thread_id = row[0]
            webbrowser.open(f"https://mail.google.com/mail/u/0/#all/{thread_id}")
            self._log_activity(f"Opened Gmail thread {thread_id[:20]}...")

    def _blacklist_from_reply(self):
        """Blacklist the sender of current reply."""
        if not self.current_reply_id:
            return
        row = self.engine.db.execute("SELECT from_addr FROM replies WHERE id=?",
                                      (self.current_reply_id,)).fetchone()
        if row:
            email = row[0]
            self.engine.db.blacklist_add(email, "manual-from-replies")
            self.engine.db.execute("UPDATE replies SET status='handled' WHERE id=?",
                                  (self.current_reply_id,))
            self.engine.db.commit()
            self._log_activity(f"Blacklisted {email} from Replies tab")
            self._refresh_replies()
            self._refresh_dashboard()
            self._add_message("raj", f"🚫 Blacklisted {email}")

    def _mark_reply_handled(self):
        """Mark current reply as handled."""
        if not self.current_reply_id:
            return
        self.engine.db.execute("UPDATE replies SET status='handled' WHERE id=?",
                              (self.current_reply_id,))
        self.engine.db.commit()
        self._log_activity(f"Marked reply {self.current_reply_id} as handled")
        self._refresh_replies()


    def _generate_draft_now(self):
        """Manually trigger AI draft generation for current reply."""
        if not self.current_reply_id:
            return

        self._add_message("raj", "🤖 Generating draft... checking Ollama...")

        def do_generate():
            try:
                # Check if Ollama is running
                import requests
                r = requests.get("http://localhost:11434", timeout=5)
                if r.status_code != 200:
                    self.after(0, lambda: self._add_message("raj", "❌ Ollama is not running. Start it first: ollama serve"))
                    return

                # Get reply data
                row = self.engine.db.execute(
                    "SELECT * FROM replies WHERE id=?", (self.current_reply_id,)
                ).fetchone()
                if not row:
                    return

                reply = dict(row)
                from_addr = reply.get("from_addr", "")
                subject = reply.get("subject", "")
                body = reply.get("body", "")
                thread_id = reply.get("thread_id", "")
                send_id = reply.get("send_id")

                # Get recipient info
                rec = self.engine.db.execute("""
                    SELECT r.*, s.day, s.subject as orig_subject
                    FROM recipients r JOIN sends s ON s.recipient_id=r.id WHERE s.id=?
                """, (send_id,)).fetchone()

                if not rec:
                    self.after(0, lambda: self._add_message("raj", "❌ Could not find recipient info"))
                    return

                seq_id = rec[1]
                persona = self.engine.SEQUENCES.get(seq_id, {}).get("persona", "school")
                name, org = rec[3], rec[4]

                system = self.engine._persona_prompt(persona)
                user = f"Recipient: {name} from {org}. Original: {rec[10]}. Reply: --- {body} --- Return JSON: {{sentiment, summary, draft_html}}"

                # Call Ollama
                r = requests.post("http://localhost:11434/api/chat", json={
                    "model": "gpt-oss:20b-cloud",
                    "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                    "stream": False
                }, timeout=120)

                content = r.json()["message"]["content"]
                import re, json
                m = re.search(r"\{.*\}", content, re.DOTALL)
                if not m:
                    self.after(0, lambda: self._add_message("raj", "❌ AI returned invalid format"))
                    return

                result = json.loads(m.group())
                sentiment = result.get("sentiment", "neutral")

                if sentiment in ("hostile", "unsubscribe"):
                    self.engine.db.blacklist_add(from_addr, f"sentiment:{sentiment}")
                    self.engine.db.execute("UPDATE replies SET status='handled', sentiment=? WHERE id=?",
                                          (sentiment, self.current_reply_id))
                    self.engine.db.commit()
                    self.after(0, lambda: self._add_message("raj", f"🚫 Auto-blacklisted {from_addr} ({sentiment})"))
                    self.after(0, self._refresh_replies)
                    return

                # Create Gmail draft
                draft = self.engine.gmail.draft_reply(thread_id, result.get("draft_html", ""),
                                                       f"Re: {subject}" if not subject.startswith("Re:") else subject)
                draft_id = draft.get("id") if draft else None

                self.engine.db.execute(
                    "UPDATE replies SET status='drafted', sentiment=?, summary=?, draft_reply_id=? WHERE id=?",
                    (sentiment, result.get("summary", ""), draft_id, self.current_reply_id)
                )
                self.engine.db.commit()

                self.after(0, lambda: self._add_message("raj", f"✅ Draft generated! Sentiment: {sentiment}. Open Gmail to review."))
                self.after(0, lambda: self._show_reply_detail(self.current_reply_id))
                self.after(0, self._refresh_replies)

            except requests.exceptions.ConnectionError:
                self.after(0, lambda: self._add_message("raj", "❌ Ollama not running. Install & start: https://ollama.com"))
            except Exception as e:
                self.after(0, lambda: self._add_message("raj", f"❌ Draft generation failed: {str(e)[:100]}"))

        threading.Thread(target=do_generate, daemon=True).start()

    def _create_batch(self):
        """Create a new batch from UI inputs."""
        name = self.batch_name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Batch name required")
            return
        
        seq = self.batch_seq_var.get()
        sched = self.batch_sched_var.get()
        rate_str = self.batch_rate_var.get()
        
        # Parse schedule
        if sched == "immediate":
            scheduled_at = datetime.now().isoformat()
        elif sched == "tomorrow_10am":
            scheduled_at = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0).isoformat()
        else:
            scheduled_at = None
        
        # Parse rate to stagger_minutes
        rate_map = {"all_at_once": 0, "1_per_minute": 1, "1_per_2min": 2, "1_per_5min": 5}
        stagger_minutes = rate_map.get(rate_str, 0)
        send_rate = 1 if stagger_minutes > 0 else 0  # 1 email per interval
        
        # Create batch
        batch_id = self.engine.db.batch_create(name, seq, scheduled_at, 
                                               send_rate=send_rate, stagger_minutes=stagger_minutes)
        
        # Add recipients if loaded
        added = 0
        if hasattr(self, "_batch_temp_recipients") and self._batch_temp_recipients:
            for recip in self._batch_temp_recipients:
                # First add to recipients table if not exists
                ok, _ = self.engine.db.recipient_add(seq, recip["email"], recip["name"], 
                                                     recip["org"], recip.get("extra_json"))
                # Get recipient ID
                row = self.engine.db.execute(
                    "SELECT id FROM recipients WHERE sequence_id=? AND email=?",
                    (seq, recip["email"])).fetchone()
                if row:
                    self.engine.db.batch_add_recipient(batch_id, row[0])
                    added += 1
            self._batch_temp_recipients = []
        
        self.batch_recipients_label.configure(text="0 recipients selected")
        self.batch_name_entry.delete(0, "end")
        
        self._add_message("raj", f"Batch \'{name}\' created (ID: {batch_id}) with {added} recipients.")
        self._refresh_batches_list()
        self._refresh_dashboard()
        self.engine.db.log_action("batch_create", f"{name} ({seq}) - {added} recipients", "user")
    def _refresh_batches_list(self):
        """Refresh the batches list in the Batches view."""
        for widget in self.batches_list_frame.winfo_children():
            widget.destroy()

        try:
            batches = self.engine.db.batch_get_all()
            if not batches:
                ctk.CTkLabel(self.batches_list_frame, text="No batches yet. Create one above.",
                            font=("Segoe UI", 12), text_color=C_TEXT_DIM).pack(pady=20)
                return

            for batch in batches:
                self._create_batch_detail_card(batch)
        except Exception as e:
            print(f"Batches list error: {e}")

    def _create_batch_detail_card(self, batch):
        """Detailed batch card for the batches list."""
        card = ctk.CTkFrame(self.batches_list_frame, fg_color=C_PANEL, corner_radius=8)
        card.pack(fill="x", pady=5)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkLabel(top, text=batch["name"], font=("Segoe UI", 14, "bold"),
                    text_color=C_ACCENT).pack(side="left")

        status_colors = {
            "running": C_SUCCESS,
            "scheduled": C_WARNING,
            "draft": C_TEXT_DIM,
            "paused": C_DANGER,
            "completed": C_SUCCESS
        }
        status_color = status_colors.get(batch["status"], C_TEXT_DIM)
        ctk.CTkLabel(top, text=batch["status"].upper(), font=("Segoe UI", 10),
                    text_color=status_color).pack(side="right")

        # Details
        details = ctk.CTkFrame(card, fg_color="transparent")
        details.pack(fill="x", padx=15, pady=(0, 5))

        seq_text = f"Sequence: {batch['sequence_id'].upper()}"
        sched_text = f"Scheduled: {batch.get('scheduled_at', 'Not set')[:16] if batch.get('scheduled_at') else 'Not set'}"
        # FIX: Show correct rate interval
        stagger = batch.get("stagger_minutes", 0)
        if stagger == 0:
            rate_text = "Rate: All at once"
        elif stagger == 1:
            rate_text = "Rate: 1 per minute"
        elif stagger == 2:
            rate_text = "Rate: 1 per 2 min"
        elif stagger == 5:
            rate_text = "Rate: 1 per 5 min"
        else:
            rate_text = f"Rate: 1 per {stagger} min"

        ctk.CTkLabel(details, text=f"{seq_text} | {sched_text} | {rate_text}",
                    font=("Segoe UI", 10), text_color=C_TEXT_DIM).pack(anchor="w")

        # Progress
        try:
            counts = self.engine.db.batch_count_by_status(batch["id"])
            total = sum(counts.values())
            sent = counts.get("sent", 0)
            progress_text = f"Progress: {sent}/{total} sent"
        except:
            progress_text = "Progress: Loading..."

        ctk.CTkLabel(details, text=progress_text,
                    font=("Segoe UI", 10), text_color=C_TEXT).pack(anchor="w", pady=(5, 0))

        # Actions
        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(fill="x", padx=15, pady=(5, 10))

        if batch["status"] in ["draft", "scheduled", "paused"]:
            ctk.CTkButton(actions, text="▶ Start", width=80, height=25,
                         fg_color=C_SUCCESS, command=lambda b=batch["id"]: self._start_batch(b)).pack(side="left", padx=2)
        elif batch["status"] == "running":
            ctk.CTkButton(actions, text="⏸ Pause", width=80, height=25,
                         fg_color=C_WARNING, command=lambda b=batch["id"]: self._pause_batch(b)).pack(side="left", padx=2)
            ctk.CTkButton(actions, text="⏹ Stop", width=80, height=25,
                         fg_color=C_DANGER, command=lambda b=batch["id"]: self._stop_batch(b)).pack(side="left", padx=2)

        ctk.CTkButton(actions, text="🗑 Delete", width=80, height=25,
                     fg_color=C_DANGER, command=lambda b=batch["id"]: self._delete_batch(b)).pack(side="left", padx=2)
        ctk.CTkButton(actions, text="📊 Details", width=80, height=25,
                     fg_color=C_PANEL, command=lambda b=batch["id"]: self._show_batch_details(b)).pack(side="left", padx=2)

        # Show "Add to Pipeline" button for completed batches
        if batch["status"] == "completed":
            has_pipeline = False
            try:
                pipe_check = self.engine.db.execute(
                    "SELECT COUNT(*) FROM batches WHERE parent_batch_id=? AND id != ?",
                    (batch["id"], batch["id"])
                ).fetchone()
                has_pipeline = pipe_check[0] > 0
            except:
                pass

            if not has_pipeline:
                ctk.CTkButton(actions, text="➕ Add to Pipeline", width=130, height=25,
                             fg_color=C_SUCCESS, hover_color="#2ecc71",
                             command=lambda b=batch: self._add_batch_to_pipeline(b)).pack(side="left", padx=2)

    def _start_batch(self, batch_id):
        self.engine.db.batch_update_status(batch_id, "running")
        self._refresh_batches_list()
        self._refresh_dashboard()
        self._add_message("raj", f"Batch {batch_id} started.")

    def _pause_batch(self, batch_id):
        self.engine.db.batch_update_status(batch_id, "paused")
        self._refresh_batches_list()
        self._add_message("raj", f"Batch {batch_id} paused.")

    def _stop_batch(self, batch_id):
        """Stop a running batch (mark as paused)."""
        self.engine.db.batch_update_status(batch_id, "paused")
        self._refresh_batches_list()
        self._refresh_dashboard()
        self._add_message("raj", f"Batch {batch_id} stopped.")

    def _delete_batch(self, batch_id):
        if messagebox.askyesno("Confirm", "Delete this batch? Recipients stay in database."):
            self.engine.db.batch_delete(batch_id)
            self._refresh_batches_list()
            self._refresh_dashboard()
            self._add_message("raj", f"Batch {batch_id} deleted.")

    def _add_batch_to_pipeline(self, batch):
        """Add a completed batch to the pipeline (create Day 3,5,7,10 follow-ups)."""
        try:
            batch_id = batch["id"]
            seq_id = batch["sequence_id"]
            current_day = batch.get("day_offset", 1)

            # Set as pipeline root
            self.engine.db.execute(
                "UPDATE batches SET parent_batch_id=? WHERE id=?",
                (batch_id, batch_id)
            )
            self.engine.db.commit()

            # Get recipients
            recipients = self.engine.db.batch_get_recipients(batch_id)
            recipient_ids = [r["id"] for r in recipients if r.get("batch_status") == "sent"]
            if not recipient_ids:
                recipient_ids = [r["id"] for r in recipients]

            # Sequence days
            days = [1, 3, 5, 7, 10]
            try:
                current_idx = days.index(current_day)
            except ValueError:
                self._add_message("raj", "Day " + str(current_day) + " not in standard sequence")
                return

            base_name = batch["name"].split("-D")[0] if "-D" in batch["name"] else batch["name"]
            stagger = batch.get("stagger_minutes", 2)
            created = []

            from datetime import datetime, timedelta

            for i in range(current_idx + 1, len(days)):
                next_day = days[i]
                next_name = base_name + "-D" + str(next_day)

                # Schedule 2 days apart
                days_from_now = (i - current_idx) * 2
                scheduled = (datetime.now() + timedelta(days=days_from_now)).replace(
                    hour=10, minute=0, second=0, microsecond=0
                )

                # Check if exists
                existing = self.engine.db.execute(
                    "SELECT id FROM batches WHERE name=?", (next_name,)
                ).fetchone()
                if existing:
                    continue

                # Create batch
                new_id = self.engine.db.batch_create(
                    next_name, seq_id, scheduled.isoformat(),
                    stagger_minutes=stagger, day_offset=next_day
                )

                # Link to parent
                self.engine.db.execute(
                    "UPDATE batches SET parent_batch_id=? WHERE id=?",
                    (batch_id, new_id)
                )

                # Copy recipients
                for rid in recipient_ids:
                    self.engine.db.batch_add_recipient(new_id, rid)

                created.append({"name": next_name, "day": next_day, "scheduled": scheduled.strftime("%d %b %H:%M")})

            self.engine.db.commit()

            if created:
                msg = "Added " + batch["name"] + " to pipeline! Created " + str(len(created)) + " follow-ups:"
                for c in created:
                    msg += "\n   -> " + c["name"] + " (Day " + str(c["day"]) + ") at " + c["scheduled"]
                self._add_message("raj", msg)
            else:
                self._add_message("raj", "Batch " + batch["name"] + " is already in pipeline or all follow-ups exist.")

            self._refresh_batches_list()
            self._refresh_dashboard()

        except Exception as e:
            self._add_message("raj", "Pipeline error: " + str(e)[:100])
            import traceback
            print("Pipeline error: " + traceback.format_exc())

    def _show_batch_details(self, batch_id):
        # Open a detail popup showing all recipients in the batch
        try:
            batch = self.engine.db.batch_get(batch_id)
            if not batch:
                self._add_message("raj", f"Batch {batch_id} not found.")
                return

            recipients = self.engine.db.batch_get_recipients(batch_id)

            # Create popup window
            popup = ctk.CTkToplevel(self)
            popup.title(f"Batch Details: {batch['name']}")
            popup.geometry("800x600")
            popup.configure(fg_color=C_BG)

            # Header
            ctk.CTkLabel(popup, text=f"📊 {batch['name']}", 
                        font=("Segoe UI", 18, "bold"), text_color=C_ACCENT).pack(pady=(15, 5))
            ctk.CTkLabel(popup, text=f"Sequence: {batch['sequence_id'].upper()} | Status: {batch['status'].upper()}",
                        font=("Segoe UI", 12), text_color=C_TEXT_DIM).pack()

            # Stats
            counts = self.engine.db.batch_count_by_status(batch_id)
            total = sum(counts.values())
            sent = counts.get("sent", 0)
            pending = counts.get("pending", 0)
            failed = counts.get("failed", 0)

            stats_frame = ctk.CTkFrame(popup, fg_color=C_PANEL, corner_radius=8)
            stats_frame.pack(fill="x", padx=20, pady=15)

            ctk.CTkLabel(stats_frame, text=f"Total: {total} | Sent: {sent} | Pending: {pending} | Failed: {failed}",
                        font=("Segoe UI", 12), text_color=C_TEXT).pack(pady=10)

            # Recipients list
            scroll = ctk.CTkScrollableFrame(popup, fg_color=C_PANEL)
            scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))

            # Headers
            headers = ["Email", "Name", "Org", "Status"]
            for col, h in enumerate(headers):
                ctk.CTkLabel(scroll, text=h, font=("Segoe UI", 11, "bold"),
                            text_color=C_ACCENT).grid(row=0, column=col, padx=10, pady=5)

            for i, r in enumerate(recipients, start=1):
                status_color = C_SUCCESS if r.get("batch_status") == "sent" else C_WARNING if r.get("batch_status") == "pending" else C_DANGER
                ctk.CTkLabel(scroll, text=r.get("email", ""), font=("Segoe UI", 10),
                            text_color=C_TEXT).grid(row=i, column=0, padx=10, pady=2, sticky="w")
                ctk.CTkLabel(scroll, text=r.get("name", ""), font=("Segoe UI", 10),
                            text_color=C_TEXT).grid(row=i, column=1, padx=10, pady=2, sticky="w")
                ctk.CTkLabel(scroll, text=r.get("org", ""), font=("Segoe UI", 10),
                            text_color=C_TEXT).grid(row=i, column=2, padx=10, pady=2, sticky="w")
                ctk.CTkLabel(scroll, text=r.get("batch_status", "").upper(), font=("Segoe UI", 10),
                            text_color=status_color).grid(row=i, column=3, padx=10, pady=2)

        except Exception as e:
            self._add_message("raj", f"Batch details error: {e}")

    def _import_batch_recipients(self):
        """Import XLSX and store recipients in temporary batch list."""
        if not PANDAS_AVAILABLE:
            messagebox.showerror("Error", "pandas not installed. Run: pip install pandas openpyxl")
            return
        path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx *.xls")])
        if not path:
            return
        
        try:
            df = pd.read_excel(path)
            
            self._batch_temp_recipients = []
            for idx, row in df.iterrows():
                email = str(row.get("email", "")).strip().lower()
                if not email or "@" not in email or "***" in email:
                    continue
                name = str(row.get("name", "Principal")).strip()
                org = str(row.get("org", "")).strip()
                extra = row.get("extra_json", "")
                if pd.isna(extra):
                    extra = None
                self._batch_temp_recipients.append({
                    "email": email, "name": name, "org": org, "extra_json": extra
                })
            
            count = len(self._batch_temp_recipients)
            self.batch_recipients_label.configure(
                text=f"{count} recipients loaded from {os.path.basename(path)}")
            self._add_message("raj", f"Loaded {count} recipients. Click Create Batch to save them.")
            
        except Exception as e:
            messagebox.showerror("Import Error", str(e))
        """Import XLSX and store recipients in temporary batch list."""
        path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx *.xls")])
        if not path:
            return
        
        try:
            import pandas as pd
            df = pd.read_excel(path)
            
            self._batch_temp_recipients = []
            for idx, row in df.iterrows():
                email = str(row.get("email", "")).strip().lower()
                if not email or "@" not in email or "***" in email:
                    continue
                name = str(row.get("name", "Principal")).strip()
                org = str(row.get("org", "")).strip()
                extra = row.get("extra_json", "")
                if pd.isna(extra):
                    extra = None
                self._batch_temp_recipients.append({
                    "email": email, "name": name, "org": org, "extra_json": extra
                })
            
            self.batch_recipients_label.configure(
                text=f"{len(self._batch_temp_recipients)} recipients loaded from {os.path.basename(path)}")
            self._add_message("raj", f"Loaded {len(self._batch_temp_recipients)} recipients from XLSX. Click Create Batch to add them.")
            
        except Exception as e:
            messagebox.showerror("Import Error", str(e))
    def _select_db_recipients(self):
        """Select recipients already in database for this batch."""
        seq = self.batch_seq_var.get()
        recipients = self.engine.db.recipient_get_by_sequence(seq)
        if not recipients:
            messagebox.showinfo("No Recipients", f"No recipients found in {seq.upper()} sequence. Import them first in Settings.")
            return
        
        self._batch_temp_recipients = []
        for r in recipients:
            self._batch_temp_recipients.append({
                "email": r["email"], "name": r.get("name", ""), 
                "org": r.get("org", ""), "extra_json": r.get("extra_json", "")
            })
        
        self.batch_recipients_label.configure(
            text=f"{len(self._batch_temp_recipients)} recipients selected from {seq.upper()} database")
        self._add_message("raj", f"Selected {len(self._batch_temp_recipients)} recipients from {seq.upper()} database.")

    def _on_pool_seq_change(self, seq_id):
        """Update pool count when sequence dropdown changes."""
        try:
            count = self.engine.get_pool_count(seq_id)
            self.pool_count_label.configure(text=f"{count} leads", 
                                            text_color=C_SUCCESS if count > 0 else C_TEXT_DIM)
            # Auto-generate batch name
            from datetime import datetime
            auto_name = f"{seq_id.upper()}-Pool-{datetime.now().strftime('%m%d')}"
            self.pool_batch_name.delete(0, "end")
            self.pool_batch_name.insert(0, auto_name)
        except Exception as e:
            self.pool_count_label.configure(text="Error", text_color=C_DANGER)

    def _create_batch_from_pool(self):
        """Create a batch from unbatched leads in the pool."""
        seq = self.pool_seq_var.get()
        size = int(self.pool_batch_size.get())
        day = int(self.pool_day_offset.get())
        name = self.pool_batch_name.get().strip()

        if not name:
            from datetime import datetime
            name = f"{seq.upper()}-Pool-{datetime.now().strftime('%m%d')}"

        try:
            result = self.engine.create_batch_from_pool(
                name=name,
                sequence_id=seq,
                batch_size=size,
                day_offset=day
            )

            if result.get("success"):
                self._add_message("raj", 
                    f"✅ Created batch '{result.get('name')}' with {result.get('size', 0)} leads. "
                    f"Pool remaining: {result.get('pool_remaining', 0)}. "
                    f"Click Start in Batches list to launch.")
                self._on_pool_seq_change(seq)  # Refresh pool count
                self._refresh_batches_list()
                self._refresh_dashboard()
            else:
                self._add_message("raj", f"❌ Could not create batch: {result.get('error', 'Unknown error')}")

        except Exception as e:
            self._add_message("raj", f"❌ Pool batch error: {str(e)[:100]}")
    # ═══════════════════════════════════════════════════════════
    #  BLACKLIST VIEW (Enhanced — Individual Removal)
    # ═══════════════════════════════════════════════════════════
    def _build_blacklist_view(self):
        view = ctk.CTkFrame(self.content, fg_color="transparent")
        self.views["blacklist"] = view
        view.grid_columnconfigure(0, weight=1)
        view.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(view, text="🚫 Blacklist Management", font=("Segoe UI", 24, "bold"),
                    text_color="white").grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Controls
        ctrl = ctk.CTkFrame(view, fg_color="transparent")
        ctrl.grid(row=1, column=0, sticky="ew", pady=(0, 15))

        self.bl_entry = ctk.CTkEntry(ctrl, placeholder_text="Email to blacklist...", width=250)
        self.bl_entry.pack(side="left", padx=5)

        ctk.CTkButton(ctrl, text="➕ Add", command=self._add_blacklist,
                     fg_color=C_DANGER, width=80).pack(side="left", padx=5)
        ctk.CTkButton(ctrl, text="📁 Import", command=self._import_blacklist,
                     fg_color=C_PANEL, width=80).pack(side="left", padx=5)
        ctk.CTkButton(ctrl, text="🗑 Clear All", command=self._clear_blacklist,
                     fg_color=C_DANGER, width=100).pack(side="left", padx=5)

        # Blacklist table
        self.bl_scroll = ctk.CTkScrollableFrame(view, fg_color=C_PANEL, corner_radius=8)
        self.bl_scroll.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        self.bl_table = ctk.CTkFrame(self.bl_scroll, fg_color=C_PANEL)
        self.bl_table.pack(fill="both", expand=True)


        # Headers
        headers = ["Email", "Reason", "Source", "Added", "Action"]
        for col, h in enumerate(headers):
            ctk.CTkLabel(self.bl_table, text=h, font=("Segoe UI", 11, "bold"),
                        text_color=C_ACCENT).grid(row=0, column=col, padx=15, pady=8)

        self.bl_rows = []
        self._refresh_blacklist()

    def _refresh_blacklist(self):
        """Refresh blacklist table with individual remove buttons."""
        # Clear existing rows (keep header)
        for widget in self.bl_table.winfo_children()[len(["Email", "Reason", "Source", "Added", "Action"]):]:
            widget.destroy()

        self.bl_rows = []

        try:
            entries = self.engine.db.blacklist_get_all()
            for row_idx, entry in enumerate(entries, start=1):
                self._create_blacklist_row(row_idx, entry)

            # Summary
            total = len(entries)
            ctk.CTkLabel(self.bl_table, text=f"Total: {total} blacklisted | @robopirate.in protected",
                        font=("Segoe UI", 10), text_color=C_TEXT_DIM).grid(
                        row=row_idx + 1 if entries else 1, column=0, columnspan=5,
                        padx=15, pady=10, sticky="w")
        except Exception as e:
            print(f"Blacklist refresh error: {e}")

    def _create_blacklist_row(self, row_idx, entry):
        """Create a row in the blacklist table."""
        ctk.CTkLabel(self.bl_table, text=entry["email"], font=("Segoe UI", 10),
                    text_color=C_TEXT).grid(row=row_idx, column=0, padx=15, pady=5)

        ctk.CTkLabel(self.bl_table, text=entry.get("reason", "")[:30],
                    font=("Segoe UI", 10), text_color=C_TEXT_DIM).grid(row=row_idx, column=1, padx=15, pady=5)

        ctk.CTkLabel(self.bl_table, text=entry.get("source", "manual"),
                    font=("Segoe UI", 10), text_color=C_TEXT_DIM).grid(row=row_idx, column=2, padx=15, pady=5)

        added = entry.get("added_at", "")[:16] if entry.get("added_at") else ""
        ctk.CTkLabel(self.bl_table, text=added,
                    font=("Segoe UI", 10), text_color=C_TEXT_DIM).grid(row=row_idx, column=3, padx=15, pady=5)

        ctk.CTkButton(self.bl_table, text="🗑", width=30, height=22,
                     fg_color=C_PANEL, hover_color=C_DANGER,
                     command=lambda e=entry["email"]: self._remove_blacklist_item(e)).grid(
                     row=row_idx, column=4, padx=15, pady=5)

    def _remove_blacklist_item(self, email):
        """Remove individual email from blacklist."""
        if messagebox.askyesno("Confirm", f"Remove {email} from blacklist?"):
            self.engine.db.blacklist_remove(email)
            self.engine.db.log_action("blacklist_remove", f"Removed: {email}", "user")
            self._refresh_blacklist()
            self._refresh_dashboard()
            self._add_message("raj", f"Removed {email} from blacklist.")

    def _add_blacklist(self):
        email = self.bl_entry.get().strip()
        if email and "@" in email:
            self.engine.blacklist_add(email)
            self.bl_entry.delete(0, "end")
            self._refresh_blacklist()
            self._refresh_dashboard()
            self._add_message("raj", f"Added {email} to blacklist.")

    def _import_blacklist(self):
        path = filedialog.askopenfilename(filetypes=[("Text/CSV", "*.txt *.csv")])
        if path:
            try:
                import re
                with open(path, "r") as f:
                    emails = [e.strip() for e in re.split(r"[\n,;]", f.read()) if "@" in e.strip()]
                count = 0
                for email in emails:
                    if not self.engine.db.blacklist_has(email):
                        self.engine.db.blacklist_add(email, "imported", "user")
                        count += 1
                self._refresh_blacklist()
                self._refresh_dashboard()
                self._add_message("raj", f"Imported {count} emails to blacklist.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _clear_blacklist(self):
        if messagebox.askyesno("Confirm", "Clear ALL blacklisted emails?"):
            self.engine.db.execute("DELETE FROM blacklist")
            self.engine.db.commit()
            self._refresh_blacklist()
            self._refresh_dashboard()
            self._add_message("raj", "Blacklist cleared.")

    # ═══════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════
    #  CHARTS VIEW (Analytics Dashboard)
    # ═══════════════════════════════════════════════════════════
    def _build_charts_view(self):
        view = ctk.CTkFrame(self.content, fg_color="transparent")
        self.views["charts"] = view
        view.grid_columnconfigure(0, weight=1)
        view.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(view, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(header, text="📊  Campaign Analytics",
                     font=("Segoe UI", 28, "bold"),
                     text_color=C_ACCENT).pack(side="left")

        # Refresh button
        ctk.CTkButton(header, text="🔄 Refresh", command=self._refresh_charts,
                      font=("Segoe UI", 11, "bold"), height=35, width=120,
                      fg_color=C_ACCENT, text_color="white",
                      hover_color="#00b8e6").pack(side="right", padx=(0, 10))
        self.charts_status = ctk.CTkLabel(header, text="",
                                           font=("Segoe UI", 10), text_color=C_TEXT_DIM)
        self.charts_status.pack(side="right", padx=10)

        # Charts content frame
        self.charts_container = ctk.CTkFrame(view, fg_color="transparent")
        self.charts_container.grid(row=1, column=0, sticky="nsew")
        self.charts_container.grid_columnconfigure(0, weight=1)
        self.charts_container.grid_rowconfigure(0, weight=1)

        if CHARTS_AVAILABLE:
            self.charts_tab = ChartsTab(self.charts_container, self.engine.db)
        else:
            ctk.CTkLabel(self.charts_container,
                        text="Install matplotlib for charts:\npip install matplotlib",
                        font=("Segoe UI", 14), text_color=C_TEXT_DIM).pack(pady=100)

    def _refresh_charts(self):
        """Refresh chart data."""
        if CHARTS_AVAILABLE and hasattr(self, 'charts_tab'):
            self.charts_tab.refresh()
            from datetime import datetime
            self.charts_status.configure(
                text=f"Updated {datetime.now().strftime('%I:%M %p')}")

    #  SETTINGS VIEW (Enhanced — Import Feedback)
    # ═══════════════════════════════════════════════════════════
    def _build_settings_view(self):
        view = ctk.CTkFrame(self.content, fg_color="transparent")
        self.views["settings"] = view
        view.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(view, text="⚙️ Settings", font=("Segoe UI", 24, "bold"),
                    text_color="white").grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Import section
        import_frame = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=12)
        import_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(import_frame, text="📥 Import Recipients", font=("Segoe UI", 16, "bold"),
                    text_color=C_ACCENT).pack(anchor="w", padx=15, pady=(15, 10))

        ctk.CTkLabel(import_frame, text="Upload XLSX with columns: email, name, org, extra_json",
                    font=("Segoe UI", 10), text_color=C_TEXT_DIM).pack(anchor="w", padx=15)

        seq_frame = ctk.CTkFrame(import_frame, fg_color="transparent")
        seq_frame.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(seq_frame, text="Target Sequence:", font=("Segoe UI", 11)).pack(side="left")
        self.import_seq_var = ctk.StringVar(value="school")
        ctk.CTkOptionMenu(seq_frame, values=["school", "csr"], variable=self.import_seq_var,
                         width=150).pack(side="left", padx=(10, 0))

        ctk.CTkButton(import_frame, text="📁 Select XLSX", command=self._import_recipients,
                     fg_color=C_ACCENT, height=35).pack(pady=(10, 5))

        # Import results display
        self.import_result_frame = ctk.CTkFrame(import_frame, fg_color="transparent")
        self.import_result_frame.pack(fill="x", padx=15, pady=(5, 15))

        self.import_success_lbl = ctk.CTkLabel(self.import_result_frame, text="",
                                                font=("Segoe UI", 12), text_color=C_SUCCESS)
        self.import_success_lbl.pack(anchor="w")

        self.import_error_lbl = ctk.CTkLabel(self.import_result_frame, text="",
                                              font=("Segoe UI", 10), text_color=C_DANGER)
        self.import_error_lbl.pack(anchor="w")

        # Config section
        config_frame = ctk.CTkFrame(view, fg_color=C_PANEL, corner_radius=12)
        config_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(config_frame, text="🔧 Configuration", font=("Segoe UI", 16, "bold"),
                    text_color=C_ACCENT).pack(anchor="w", padx=15, pady=(15, 10))

        # Brief email
        be_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        be_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(be_frame, text="Brief Email:", font=("Segoe UI", 11)).pack(side="left")
        self.be_entry = ctk.CTkEntry(be_frame, placeholder_text="itsomkarsinghhh@gmail.com")
        self.be_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
        ctk.CTkButton(be_frame, text="Save", width=80, command=self._save_brief_email).pack(side="left", padx=10)

        # Ollama URL
        ol_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        ol_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(ol_frame, text="Ollama URL:", font=("Segoe UI", 11)).pack(side="left")
        self.ol_entry = ctk.CTkEntry(ol_frame, placeholder_text="http://localhost:11434")
        self.ol_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
        ctk.CTkButton(ol_frame, text="Save", width=80, command=self._save_ollama_url).pack(side="left", padx=10)

    def _import_recipients(self):
        path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx *.xls")])
        if not path:
            return

        seq_id = self.import_seq_var.get()
        success_count = 0
        fail_count = 0
        errors = []

        try:
            import pandas as pd
            df = pd.read_excel(path)

            for idx, row in df.iterrows():
                try:
                    email = str(row.get("email", "")).strip().lower()
                    if not email or "@" not in email or "***" in email:
                        fail_count += 1
                        errors.append(f"Row {idx+1}: Invalid email '{email}'")
                        continue

                    name = str(row.get("name", "Principal")).strip()
                    org = str(row.get("org", "")).strip()
                    extra = row.get("extra_json", "")
                    if pd.isna(extra):
                        extra = None

                    ok, err = self.engine.db.recipient_add(seq_id, email, name, org, extra)
                    if ok:
                        success_count += 1
                    else:
                        fail_count += 1
                        errors.append(f"Row {idx+1}: {err}")

                except Exception as e:
                    fail_count += 1
                    errors.append(f"Row {idx+1}: {str(e)}")

            # Show results
            self.import_success_lbl.configure(text=f"✅ Successfully imported: {success_count}")
            if fail_count > 0:
                error_text = f"❌ Failed: {fail_count}\n" + "\n".join(errors[:5])
                if len(errors) > 5:
                    error_text += f"\n... and {len(errors) - 5} more"
                self.import_error_lbl.configure(text=error_text)
            else:
                self.import_error_lbl.configure(text="")

            self.engine.db.log_action("import_recipients", 
                f"Seq: {seq_id}, Success: {success_count}, Failed: {fail_count}", "user")
            self._refresh_dashboard()
            self._add_message("raj", f"Import complete: {success_count} success, {fail_count} failed.")

        except Exception as e:
            messagebox.showerror("Import Error", str(e))

    def _save_brief_email(self):
        email = self.be_entry.get().strip()
        if email:
            self.engine.db.set_meta("brief_email", email)
            self.engine.brief_email = email
            self._add_message("raj", f"Brief email set to {email}")

    def _save_ollama_url(self):
        url = self.ol_entry.get().strip()
        if url:
            self.engine.db.set_meta("ollama_url", url)
            self.engine.ollama_url = url
            self._add_message("raj", f"Ollama URL set to {url}")

    # ═══════════════════════════════════════════════════════════
    #  TEMPLATE ACTIONS
    # ═══════════════════════════════════════════════════════════
    def _sync_templates(self):
        result = self.engine.sync_templates()
        self._refresh_template_status()
        if isinstance(result, dict):
            self._add_message("raj", f"Sync complete: {result.get('loaded', 0)} loaded, {len(result.get('skipped', []))} skipped, {len(result.get('missing', []))} missing.")
        else:
            self._add_message("raj", f"Sync complete. Result: {result}")
        self._log_activity("Templates synced")

    def _auto_generate_missing(self):
        templates = self.engine.get_templates()
        generated = 0
        for seq_id in ["school", "csr"]:
            for day in [1, 3, 5, 7, 10]:
                if not templates.get(seq_id, {}).get(day):
                    success = self.engine.save_generated_template(seq_id, day)
                    if success:
                        generated += 1
                        key = f"{seq_id}_{day}"
                        if key in self.template_cards:
                            status_lbl, preview_btn, gen_btn, lock_btn = self.template_cards[key]
                            status_lbl.configure(text="🟡 Generated", text_color=C_WARNING)
        self._add_message("raj", f"Auto-generated {generated} missing templates.")
        self._log_activity(f"Auto-generated {generated} templates")

    def _lock_all_templates(self):
        self.engine.lock_templates()
        self._refresh_template_status()
        self._add_message("raj", "All templates locked. Sync will not overwrite them.")

    def _preview_template(self, seq_id, day):
        tmpl = self.engine.db.template_get(seq_id, day)
        if not tmpl or not tmpl.get("html_body"):
            self._add_message("raj", f"No template for {seq_id.upper()} Day {day}. Generate first.")
            return
        html_content = tmpl["html_body"]
        if not html_content.strip().startswith("<"):
            html_content = f"<html><body>{html_content}</body></html>"
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_path = f.name
            webbrowser.open(f"file:///{temp_path}")
            self._add_message("raj", f"Opening {seq_id.upper()} Day {day} preview in browser.")
        except Exception as e:
            self._add_message("raj", f"Preview failed: {e}")

    def _generate_template(self, seq_id, day):
        success = self.engine.save_generated_template(seq_id, day)
        key = f"{seq_id}_{day}"
        if key in self.template_cards:
            status_lbl, preview_btn, gen_btn, lock_btn = self.template_cards[key]
            if success:
                status_lbl.configure(text="🟡 Generated", text_color=C_WARNING)
                self._add_message("raj", f"Generated {seq_id.upper()} Day {day}.")
            else:
                self._add_message("raj", f"Failed to generate {seq_id.upper()} Day {day}.")

    def _lock_template(self, seq_id, day):
        self.engine.db.template_lock(seq_id, day)
        key = f"{seq_id}_{day}"
        if key in self.template_cards:
            status_lbl, preview_btn, gen_btn, lock_btn = self.template_cards[key]
            status_lbl.configure(text="🔒 Locked", text_color="#9b59b6")
        self._add_message("raj", f"{seq_id.upper()} Day {day} locked.")

    def _refresh_template_status(self):
        templates = self.engine.get_templates()
        for seq_id in ["school", "csr"]:
            for day in [1, 3, 5, 7, 10]:
                key = f"{seq_id}_{day}"
                if key in self.template_cards:
                    status_lbl, preview_btn, gen_btn, lock_btn = self.template_cards[key]
                    t = templates.get(seq_id, {}).get(day)
                    if t:
                        source = t.get("source", "unknown")
                        locked = self.engine.is_template_locked(seq_id, day)
                        if locked:
                            status_lbl.configure(text="🔒 Locked", text_color="#9b59b6")
                        elif source == "synced":
                            status_lbl.configure(text="🟢 Synced", text_color=C_ACCENT)
                        elif source == "generated":
                            status_lbl.configure(text="🟡 Generated", text_color=C_WARNING)
                        else:
                            status_lbl.configure(text="✅ Ready", text_color=C_ACCENT)
                    else:
                        status_lbl.configure(text="❌ Missing", text_color=C_DANGER)

    # ═══════════════════════════════════════════════════════════
    #  NAVIGATION & UTILITIES
    # ═══════════════════════════════════════════════════════════
    def _show_view(self, key):
        for k, v in self.views.items():
            v.grid_forget()
        view = self.views[key]
        view.grid(row=0, column=0, sticky="nsew")
        # Ensure view content expands
        if hasattr(view, 'grid_columnconfigure'):
            view.grid_columnconfigure(0, weight=1)
        if hasattr(view, 'grid_rowconfigure'):
            # Find last row with content
            last_row = 0
            for child in view.winfo_children():
                try:
                    info = child.grid_info()
                    if info:
                        row = int(info.get('row', 0))
                        if row > last_row:
                            last_row = row
                except Exception:
                    pass
            for r in range(last_row + 1):
                view.grid_rowconfigure(r, weight=1 if r == last_row else 0)

        for k, btn in self.nav_buttons.items():
            btn.configure(fg_color=C_ACCENT if k == key else "transparent",
                         text_color="white" if k == key else C_TEXT_DIM)

        if key == "dashboard":
            self._refresh_dashboard()
        elif key == "templates":
            self._refresh_template_status()
        elif key == "blacklist":
            self._refresh_blacklist()
        elif key == "batches":
            self._refresh_batches_list()
        elif key == "import":
            pass  # Import view is self-contained

    def _pause_engine(self):
        if self.engine.is_paused():
            self.engine.resume()
            self.status_dot.configure(text_color=C_SUCCESS)
            self.status_text.configure(text="Running", text_color=C_SUCCESS)
            self.btn_pause.configure(text="⏸ Pause", fg_color=C_WARNING)
            self._add_message("raj", "Engine resumed.")
        else:
            self.engine.pause()
            self.status_dot.configure(text_color=C_WARNING)
            self.status_text.configure(text="Paused", text_color=C_WARNING)
            self.btn_pause.configure(text="▶ Resume", fg_color=C_SUCCESS)
            self._add_message("raj", "Engine paused.")


    def _scan_bounces_now(self):
        """Manual bounce scan triggered from UI."""
        self._add_message("raj", "🔍 Starting bounce scan...")
        self._log_activity("Manual bounce scan started")

        def do_scan():
            try:
                result = self.engine.scan_bounces(days_back=1)
                new_count = result.get("new_blacklisted", 0)
                deleted = result.get("deleted", 0)
                auto_replies = result.get("auto_replies", 0)

                msg = f"✅ Bounce scan complete. {new_count} new blacklisted, {auto_replies} auto-replies, {deleted} emails cleaned."
                self.after(0, lambda m=msg: self._add_message("raj", m))
                self.after(0, self._refresh_dashboard)
                self.after(0, self._refresh_blacklist)
            except Exception as e:
                error_msg = f"❌ Bounce scan error: {str(e)[:100]}"
                self.after(0, lambda m=error_msg: self._add_message("raj", m))

        threading.Thread(target=do_scan, daemon=True).start()

    def _log_activity(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] {msg}")


    def _deep_bounce_scan_15(self):
        self._run_deep_bounce_scan(15)

    def _deep_bounce_scan_30(self):
        self._run_deep_bounce_scan(30)

    def _run_deep_bounce_scan(self, days: int):
        """Run deep bounce scan and show results."""
        def do_scan():
            try:
                self._add_message("raj", f"🔍 Starting deep bounce scan for last {days} days...")
                results = self.engine.deep_bounce_scan(days)

                msg = f"✅ Deep Bounce Scan Complete ({days} Days)\n\n"
                msg += f"📊 Results:\n"
                msg += f"• Found: {results['found']} bounce emails\n"
                msg += f"• Blacklisted: {results['blacklisted']} new emails\n"
                msg += f"• Protected: {results['protected']} RoboPirate emails\n"

                if results['details']:
                    msg += f"\n📋 Details:\n"
                    for d in results['details'][:10]:
                        msg += f"🚫 {d['email']} — {d['action']}\n"
                    if len(results['details']) > 10:
                        msg += f"... and {len(results['details']) - 10} more\n"

                self.after(0, lambda: self._add_message("raj", msg))
                self.after(0, self._refresh_blacklist)
                self.after(0, self._refresh_dashboard)
            except Exception as e:
                self.after(0, lambda: self._add_message("raj", f"❌ Scan error: {e}"))

        threading.Thread(target=do_scan, daemon=True).start()

    def _on_window_resize(self, event=None):
        """Handle window resize — reflow content if needed."""
        # Only process if it's the main window (not child widgets)
        if event and event.widget is not self:
            return
        # Update sidebar height to match window
        try:
            h = self.winfo_height()
            self.sidebar.configure(height=h)
        except Exception:
            pass

    def _start_refresh_loop(self):
        def loop():
            while True:
                time.sleep(30)
                try:
                    if hasattr(self, 'views') and "dashboard" in self.views:
                        # Only refresh if dashboard is visible
                        pass
                except:
                    pass
        threading.Thread(target=loop, daemon=True).start()

    def mainloop(self, *args, **kwargs):
        super().mainloop(*args, **kwargs)