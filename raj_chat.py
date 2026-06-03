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
        self._build_settings_view()

        self._show_view("dashboard")

    # ═══════════════════════════════════════════════════════════
    # DASHBOARD VIEW
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
            ctk.CTkLabel(header, text=f" • {total_leads} recipients", font=("Segoe UI", 9),
                         text_color=C_TEXT_DIM).pack(side="left")

        # Pills row - RESPONSIVE GRID
        pills_row = ctk.CTkFrame(card, fg_color="transparent")
        pills_row.pack(fill="x", padx=6, pady=(2, 8))
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
            actual_status = status
            if status == "COMPLETED" and sent < total and total > 0:
                actual_status = "DRAFT"
            # FIX: If RUNNING but 0 sent, show as Ready
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

            # RESPONSIVE pill
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
            elif status == "NOT_CREATED":
                date_text = "Not scheduled"
            else:
                base_date = datetime.now()
                projected = base_date + timedelta(days=day_num)
                date_text = projected.strftime("%d %b")
            if date_text:
                color = "#484f58" if status == "NOT_CREATED" else "#4a5a6a"
                ctk.CTkLabel(day_frame, text=f" {date_text}", font=("Segoe UI", 7),
                             text_color=color).pack(side="left")

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
            scheduled = (datetime.now() + timedelta(days=2)).replace(hour=10, minute=0, second=0)
            scheduled_str = scheduled.strftime("%Y-%m-%d %H:%M:%S")

            batch_name = f"{family_name}-D{day_num}"
            day1_batch = None
            batches = self.engine.db.batch_get_all()
            for b in batches:
                if b.get("name", "").startswith(family_name) and "-D1" in b.get("name", ""):
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
                self._refresh_batch_list()
                self._refresh_dashboard()
            else:
                self._log_activity(f"Cannot create {batch_name}: No Day 1 batch found")
        except Exception as e:
            self._log_activity(f"Error creating day batch: {e}")

    def _start_batch(self, batch_id):
        """Start a batch."""
        try:
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
                status = r.get("status", "pending")
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
        """Start background refresh loop — thread-safe via after()."""
        def loop():
            while True:
                time.sleep(30)
                try:
                    if hasattr(self, 'views') and "dashboard" in self.views:
                        # FIX: Use after() for thread-safe UI updates
                        self.after(0, self._refresh_dashboard)
                except Exception:
                    pass

        t = threading.Thread(target=loop, daemon=True)
        t.start()

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

        # Sequence selector
        seq_frame = ctk.CTkFrame(view, fg_color="transparent")
        seq_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(seq_frame, text="Sequence:", font=("Segoe UI", 12), text_color=C_TEXT).pack(side="left")
        self.import_seq_var = ctk.StringVar(value="school")
        ctk.CTkOptionMenu(seq_frame, values=["school", "csr"], variable=self.import_seq_var,
                          font=("Segoe UI", 12)).pack(side="left", padx=(10, 0))

        # File selector
        file_frame = ctk.CTkFrame(view, fg_color="transparent")
        file_frame.pack(fill="x", pady=(0, 10))
        self.import_file_label = ctk.CTkLabel(file_frame, text="No file selected",
                                               font=("Segoe UI", 11), text_color=C_TEXT_DIM)
        self.import_file_label.pack(side="left")
        ctk.CTkButton(file_frame, text="Browse", font=("Segoe UI", 11),
                      fg_color=C_ACCENT, command=self._browse_import_file).pack(side="left", padx=(10, 0))

        # Import button
        ctk.CTkButton(view, text="Import to Pool", font=("Segoe UI", 14, "bold"),
                      fg_color=C_SUCCESS, hover_color="#2a8a4a", height=40,
                      command=self._do_import).pack(fill="x", pady=(10, 0))

        # Preview
        self.import_preview = ctk.CTkTextbox(view, fg_color=C_PANEL, text_color=C_TEXT,
                                             font=("Segoe UI", 11), wrap="word", height=200)
        self.import_preview.pack(fill="both", expand=True, pady=(10, 0))
        self.import_preview.configure(state="disabled")

        self.import_filepath = None

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
        try:
            result = self.engine.smart_import(self.import_filepath, seq_id)
            if result.get("success"):
                msg = f"Imported {result.get('imported', 0)} leads to {seq_id.upper()} pool\nSkipped: {result.get('skipped', 0)}"
                self._append_import_preview(msg)
                self._refresh_dashboard()
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

        ctk.CTkLabel(view, text="📝 Templates", font=("Segoe UI", 24, "bold"),
                     text_color="white").pack(anchor="w", pady=(0, 15))

        btn_frame = ctk.CTkFrame(view, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(btn_frame, text="🔄 Sync from Gmail", font=("Segoe UI", 12),
                      fg_color=C_ACCENT, command=self._sync_templates).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_frame, text="🔒 Lock All", font=("Segoe UI", 12),
                      fg_color=C_WARNING, command=self._lock_templates).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_frame, text="⚡ Generate Missing", font=("Segoe UI", 12),
                      fg_color=C_SUCCESS, command=self._generate_missing).pack(side="left")

        self.template_grid = ctk.CTkFrame(view, fg_color="transparent")
        self.template_grid.pack(fill="both", expand=True)

        self._refresh_templates()

    def _refresh_templates(self):
        for widget in self.template_grid.winfo_children():
            widget.destroy()

        status = self.engine.get_template_status()
        for seq_id, days in status.items():
            seq_frame = ctk.CTkFrame(self.template_grid, fg_color=C_PANEL, corner_radius=10)
            seq_frame.pack(fill="x", pady=8, padx=4)

            ctk.CTkLabel(seq_frame, text=seq_id.upper(), font=("Segoe UI", 16, "bold"),
                         text_color=C_ACCENT if seq_id == "school" else C_WARNING).pack(anchor="w", padx=15, pady=(10, 5))

            day_row = ctk.CTkFrame(seq_frame, fg_color="transparent")
            day_row.pack(fill="x", padx=10, pady=(0, 10))

            for day, info in days.items():
                color = C_SUCCESS if info["exists"] else C_DANGER
                lock_text = "🔒" if info["locked"] else ""
                ctk.CTkLabel(day_row, text=f"Day {day} {lock_text}", font=("Segoe UI", 11),
                             text_color=color).pack(side="left", padx=8)

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
    def _build_batches_view(self):
        view = ctk.CTkFrame(self.content, fg_color="transparent")
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

        # Sequence
        seq_row = ctk.CTkFrame(form, fg_color="transparent")
        seq_row.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(seq_row, text="Sequence:", font=("Segoe UI", 12), text_color=C_TEXT).pack(side="left")
        self.batch_seq = ctk.StringVar(value="school")
        ctk.CTkOptionMenu(seq_row, values=["school", "csr"], variable=self.batch_seq,
                          font=("Segoe UI", 12)).pack(side="left", padx=(10, 0))

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

        # Schedule
        sched_row = ctk.CTkFrame(form, fg_color="transparent")
        sched_row.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(sched_row, text="Schedule:", font=("Segoe UI", 12), text_color=C_TEXT).pack(side="left")
        self.batch_sched = ctk.CTkEntry(sched_row, fg_color=C_BG, text_color=C_TEXT, font=("Segoe UI", 12))
        self.batch_sched.insert(0, "2026-06-05 10:00:00")
        self.batch_sched.pack(side="left", fill="x", expand=True, padx=(10, 0))

        ctk.CTkButton(form, text="Create from Pool", font=("Segoe UI", 14, "bold"),
                      fg_color=C_SUCCESS, hover_color="#2a8a4a", height=40,
                      command=self._create_batch).pack(fill="x", padx=15, pady=(5, 15))

        # Batch list
        self.all_batches_frame = ctk.CTkFrame(view, fg_color="transparent")
        self.all_batches_frame.pack(fill="both", expand=True)

        self._refresh_all_batches()

    def _create_batch(self):
        try:
            name = self.batch_name.get().strip()
            seq_id = self.batch_seq.get()
            size = int(self.batch_size.get())
            day = int(self.batch_day.get())
            sched = self.batch_sched.get().strip()

            if not name:
                messagebox.showwarning("Missing Name", "Please enter a batch name")
                return

            result = self.engine.create_batch_from_pool(
                name=name, sequence_id=seq_id, batch_size=size,
                day_offset=day, scheduled_at=sched
            )

            if result.get("success"):
                self._log_activity(f"Created batch '{name}' with {result['size']} leads")
                self._refresh_all_batches()
                self._refresh_dashboard()
            else:
                messagebox.showwarning("Error", result.get("error", "Unknown error"))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _refresh_all_batches(self):
        for widget in self.all_batches_frame.winfo_children():
            widget.destroy()

        try:
            batches = self.engine.db.batch_get_all()
            if not batches:
                ctk.CTkLabel(self.all_batches_frame, text="No batches yet",
                             font=("Segoe UI", 12), text_color=C_TEXT_DIM).pack(pady=30)
                return

            for batch in batches:
                row = ctk.CTkFrame(self.all_batches_frame, fg_color=C_PANEL, corner_radius=8)
                row.pack(fill="x", pady=4, padx=4)

                status_color = C_SUCCESS if batch.get("status") == "completed" else C_WARNING if batch.get("status") == "running" else C_TEXT_DIM
                ctk.CTkLabel(row, text=f"● {batch.get('name', 'Unknown')}", font=("Segoe UI", 12, "bold"),
                             text_color=status_color).pack(side="left", padx=10, pady=8)

                ctk.CTkLabel(row, text=f"({batch.get('status', 'Unknown')})", font=("Segoe UI", 10),
                             text_color=C_TEXT_DIM).pack(side="left")

                ctk.CTkButton(row, text="Details", font=("Segoe UI", 10), width=60,
                              fg_color=C_ACCENT, command=lambda b=batch: self._show_batch_details(b["id"])).pack(side="right", padx=5)

                if batch.get("status") in ["draft", "scheduled", "paused"]:
                    ctk.CTkButton(row, text="▶ Start", font=("Segoe UI", 10), width=60,
                                  fg_color=C_SUCCESS, command=lambda b=batch: self._start_batch(b["id"])).pack(side="right", padx=5)
                elif batch.get("status") == "running":
                    ctk.CTkButton(row, text="⏸ Pause", font=("Segoe UI", 10), width=60,
                                  fg_color=C_WARNING, command=lambda b=batch: self._pause_batch(b["id"])).pack(side="right", padx=5)

        except Exception as e:
            ctk.CTkLabel(self.all_batches_frame, text=f"Error: {e}", text_color=C_DANGER).pack(pady=20)

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
        add_frame.pack(fill="x", pady=(0, 15))

        self.blacklist_entry = ctk.CTkEntry(add_frame, fg_color=C_BG, text_color=C_TEXT, font=("Segoe UI", 12))
        self.blacklist_entry.pack(side="left", fill="x", expand=True, padx=15, pady=10)
        ctk.CTkButton(add_frame, text="Add", font=("Segoe UI", 12), width=80,
                      fg_color=C_DANGER, command=self._add_to_blacklist).pack(side="right", padx=15, pady=10)

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
        for k, v in self.views.items():
            v.pack_forget()
        self.views[key].pack(fill="both", expand=True)

        # Update nav button colors
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color="#1a1a3e", text_color=C_ACCENT)
            else:
                btn.configure(fg_color="transparent", text_color=C_TEXT)

        # Refresh specific views
        if key == "dashboard":
            self._refresh_dashboard()
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
            self.after(0, lambda: self._log_activity(
                f"Bounce scan: {result['new_blacklisted']} new, {result['auto_replies']} auto-replies, {result['protected']} protected"
            ))
            self.after(0, self._refresh_dashboard)
        except Exception as e:
            self.after(0, lambda: self._log_activity(f"Bounce scan error: {e}"))

    def _pause_engine(self):
        if self.engine.is_paused():
            self.engine.resume()
            self.btn_pause.configure(text="⏸ Pause", fg_color=C_WARNING)
            self.status_text.configure(text="Running", text_color=C_SUCCESS)
            self.status_dot.configure(text_color=C_SUCCESS)
            self._log_activity("Engine resumed")
        else:
            self.engine.pause()
            self.btn_pause.configure(text="▶ Resume", fg_color=C_SUCCESS)
            self.status_text.configure(text="Paused", text_color=C_WARNING)
            self.status_dot.configure(text_color=C_WARNING)
            self._log_activity("Engine paused")

    def _log_activity(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] {msg}")

    def _on_window_resize(self, event):
        """Handle window resize — responsive layout adjustments."""
        # Only process actual resize events (not widget creation events)
        if event.widget == self:
            # Update any responsive elements here
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

                try:
                    self.engine.db.execute(
                        "INSERT INTO recipients (sequence_id, email, name, org, extra_json) VALUES (?, ?, ?, ?, ?)",
                        ("school", email, name, org, "{}")
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
