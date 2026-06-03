"""
raj_charts.py -- Analytics Charts for Raj Desktop v4.3
Drop this file into your raj-desktop folder.
No other changes needed except 2 lines in raj_chat.py (see bottom).
"""

import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime, timedelta
from collections import defaultdict


class ChartsTab:
    """Analytics dashboard embedded in Raj's desktop UI."""

    # RoboPirate brand colors (LOCKED from UI_CHECKLIST.txt)
    BG = "#0A1628"
    PANEL = "#111D2E"
    CYAN = "#59ced9"
    GOLD = "#febe32"
    GREEN = "#34c759"
    RED = "#ff3b30"
    PURPLE = "#6d45a5"
    TEXT = "#E6EDF3"
    DIM = "#8B949E"
    BORDER = "#2a2a4e"

    def __init__(self, parent_frame, db_connection):
        """
        parent_frame: the CTkFrame tab to draw charts inside
        db_connection: your db object (same as engine.db)
        """
        self.db = db_connection
        self.frame = parent_frame

        # ── Style matplotlib for dark theme ──
        plt.style.use("dark_background")
        matplotlib.rcParams.update({
            "figure.facecolor": self.PANEL,
            "axes.facecolor": self.PANEL,
            "axes.edgecolor": self.BORDER,
            "axes.labelcolor": self.TEXT,
            "xtick.color": self.DIM,
            "ytick.color": self.DIM,
            "text.color": self.TEXT,
            "grid.color": self.BORDER,
            "grid.alpha": 0.3,
        })

        self._build_ui()
        self.refresh()

    # ═══════════════════════════════════════════════════════════
    # BUILD UI
    # ═══════════════════════════════════════════════════════════

    def _build_ui(self):
        """Create the full charts dashboard."""

        # ── Header ──
        header = ctk.CTkLabel(
            self.frame, text="📊  Campaign Analytics",
            font=("Segoe UI", 22, "bold"),
            text_color=self.CYAN
        )
        header.pack(anchor="w", padx=20, pady=(15, 5))

        # ── KPI Cards Row ──
        self.kpi_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.kpi_frame.pack(fill="x", padx=15, pady=5)
        self._build_kpi_cards()

        # ── Charts Row: Trends (left) + Sentiment (right) ──
        charts_row = ctk.CTkFrame(self.frame, fg_color="transparent")
        charts_row.pack(fill="both", expand=True, padx=15, pady=5)

        # Left: Send trends
        left_card = ctk.CTkFrame(charts_row, fg_color=self.PANEL, corner_radius=10,
                                  border_color=self.BORDER, border_width=1)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self._build_trends_chart(left_card)

        # Right: Sentiment pie
        right_card = ctk.CTkFrame(charts_row, fg_color=self.PANEL, corner_radius=10,
                                   border_color=self.BORDER, border_width=1)
        right_card.pack(side="right", fill="both", expand=True, padx=(8, 0))
        self._build_sentiment_chart(right_card)

        # ── Bottom Row: Sequence Compare + Activity ──
        bottom_row = ctk.CTkFrame(self.frame, fg_color="transparent")
        bottom_row.pack(fill="both", expand=True, padx=15, pady=5)

        # Left: Sequence comparison bar chart
        bl_card = ctk.CTkFrame(bottom_row, fg_color=self.PANEL, corner_radius=10,
                                border_color=self.BORDER, border_width=1)
        bl_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self._build_sequence_chart(bl_card)

        # Right: Recent activity feed
        br_card = ctk.CTkFrame(bottom_row, fg_color=self.PANEL, corner_radius=10,
                                border_color=self.BORDER, border_width=1)
        br_card.pack(side="right", fill="both", expand=True, padx=(8, 0))
        self._build_activity_feed(br_card)

        # ── Refresh Button ──
        btn_row = ctk.CTkFrame(self.frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=15, pady=(5, 10))

        refresh_btn = ctk.CTkButton(
            btn_row, text="🔄  Refresh Data", command=self.refresh,
            font=("Segoe UI", 12, "bold"), height=36, width=160,
            fg_color=self.CYAN, hover_color="#4ab8c4",
            text_color=self.BG, corner_radius=8
        )
        refresh_btn.pack(side="right")

        self.status_label = ctk.CTkLabel(
            btn_row, text="", font=("Segoe UI", 10), text_color=self.DIM
        )
        self.status_label.pack(side="right", padx=15)

    def _build_kpi_cards(self):
        """4 summary cards at the top."""
        self.kpi_labels = {}
        metrics = [
            ("TOTAL LEADS", self.CYAN, "total"),
            ("EMAILS SENT", self.GREEN, "sent"),
            ("REPLIES", self.GOLD, "replied"),
            ("REPLY RATE", self.PURPLE, "rate"),
        ]
        for title, color, key in metrics:
            card = ctk.CTkFrame(self.kpi_frame, fg_color=self.PANEL, corner_radius=10,
                                border_color=self.BORDER, border_width=1, height=85)
            card.pack(side="left", fill="x", expand=True, padx=5)
            card.pack_propagate(False)

            # Color indicator bar at top
            bar = ctk.CTkFrame(card, fg_color=color, height=3, corner_radius=0)
            bar.pack(fill="x", padx=0, pady=0)

            ctk.CTkLabel(card, text=title, font=("Segoe UI", 9),
                         text_color=self.DIM).pack(pady=(8, 0))

            val = ctk.CTkLabel(card, text="—", font=("Segoe UI", 22, "bold"),
                               text_color=color)
            val.pack()
            self.kpi_labels[key] = val

    def _build_trends_chart(self, parent):
        """14-day send trends area chart."""
        ctk.CTkLabel(parent, text="Send Trends (14 Days)",
                     font=("Segoe UI", 11, "bold"),
                     text_color=self.TEXT).pack(anchor="w", padx=10, pady=(8, 0))

        self.fig_trends = Figure(figsize=(5.5, 3), dpi=85)
        self.ax_trends = self.fig_trends.add_subplot(111)
        self.ax_trends.set_facecolor(self.PANEL)

        canvas = FigureCanvasTkAgg(self.fig_trends, parent)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=5)
        self.trends_canvas = canvas

    def _build_sentiment_chart(self, parent):
        """Reply sentiment pie chart."""
        ctk.CTkLabel(parent, text="Reply Sentiment",
                     font=("Segoe UI", 11, "bold"),
                     text_color=self.TEXT).pack(anchor="w", padx=10, pady=(8, 0))

        self.fig_sent = Figure(figsize=(3.8, 3), dpi=85)
        self.ax_sent = self.fig_sent.add_subplot(111)
        self.ax_sent.set_facecolor(self.PANEL)

        canvas = FigureCanvasTkAgg(self.fig_sent, parent)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=5)
        self.sent_canvas = canvas

    def _build_sequence_chart(self, parent):
        """School vs CSR comparison bar chart."""
        ctk.CTkLabel(parent, text="Sequence Performance",
                     font=("Segoe UI", 11, "bold"),
                     text_color=self.TEXT).pack(anchor="w", padx=10, pady=(8, 0))

        self.fig_seq = Figure(figsize=(5.5, 3), dpi=85)
        self.ax_seq = self.fig_seq.add_subplot(111)
        self.ax_seq.set_facecolor(self.PANEL)

        canvas = FigureCanvasTkAgg(self.fig_seq, parent)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=5)
        self.seq_canvas = canvas

    def _build_activity_feed(self, parent):
        """Recent activity scrollable list."""
        ctk.CTkLabel(parent, text="Recent Activity",
                     font=("Segoe UI", 11, "bold"),
                     text_color=self.TEXT).pack(anchor="w", padx=10, pady=(8, 0))

        self.activity_frame = ctk.CTkScrollableFrame(
            parent, fg_color="transparent", scrollbar_button_color=self.BORDER,
            scrollbar_button_hover_color=self.CYAN
        )
        self.activity_frame.pack(fill="both", expand=True, padx=8, pady=5)

    # ═══════════════════════════════════════════════════════════
    # REFRESH DATA
    # ═══════════════════════════════════════════════════════════

    def refresh(self):
        """Load fresh data from the database and redraw all charts."""
        if not self.db:
            self.status_label.configure(text="No database connected")
            return

        try:
            self._refresh_kpis()
            self._refresh_trends()
            self._refresh_sentiment()
            self._refresh_sequence()
            self._refresh_activity()

            now = datetime.now().strftime("%I:%M %p")
            self.status_label.configure(text=f"Last updated: {now}")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")

    def _refresh_kpis(self):
        """Update the 4 KPI cards."""
        db = self.db

        # Total leads
        row = db.execute("SELECT COUNT(*) FROM recipients").fetchone()
        total = row[0] if row else 0
        self.kpi_labels["total"].configure(text=f"{total:,}")

        # Sent
        row = db.execute(
            "SELECT COUNT(DISTINCT recipient_id) FROM sends WHERE status='sent'"
        ).fetchone()
        sent = row[0] if row else 0
        self.kpi_labels["sent"].configure(text=f"{sent:,}")

        # Replied
        row = db.execute(
            "SELECT COUNT(DISTINCT recipient_id) FROM sends WHERE status='replied'"
        ).fetchone()
        replied = row[0] if row else 0
        self.kpi_labels["replied"].configure(text=f"{replied:,}")

        # Reply rate
        rate = round((replied / sent * 100), 1) if sent > 0 else 0.0
        self.kpi_labels["rate"].configure(text=f"{rate}%")

    def _refresh_trends(self):
        """Redraw the 14-day trends area chart."""
        self.ax_trends.clear()
        self.ax_trends.set_facecolor(self.PANEL)

        since = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
        rows = self.db.execute("""
            SELECT DATE(created_at) as d, sequence_id, COUNT(*) as c
            FROM sends WHERE status='sent' AND DATE(created_at) >= ?
            GROUP BY DATE(created_at), sequence_id ORDER BY d
        """, (since,)).fetchall()

        daily = defaultdict(lambda: {"school": 0, "csr": 0})
        for d, seq, c in rows:
            daily[d][seq] = c

        dates = sorted(daily.keys())
        if not dates:
            self.ax_trends.text(0.5, 0.5, "No send data yet",
                                ha="center", va="center",
                                color=self.DIM, fontsize=11,
                                transform=self.ax_trends.transAxes)
            self.trends_canvas.draw()
            return

        school_vals = [daily[d]["school"] for d in dates]
        csr_vals = [daily[d]["csr"] for d in dates]
        x = range(len(dates))

        # Area fill
        self.ax_trends.fill_between(x, school_vals, alpha=0.25, color=self.CYAN)
        self.ax_trends.fill_between(x, csr_vals, alpha=0.25, color=self.GOLD)

        # Lines
        self.ax_trends.plot(x, school_vals, color=self.CYAN, linewidth=2,
                            label="School", marker="o", markersize=3)
        self.ax_trends.plot(x, csr_vals, color=self.GOLD, linewidth=2,
                            label="CSR", marker="o", markersize=3)

        # X labels
        step = max(1, len(dates) // 6)
        self.ax_trends.set_xticks(range(0, len(dates), step))
        self.ax_trends.set_xticklabels([d[5:] for d in dates[::step]],
                                        rotation=25, fontsize=7)

        self.ax_trends.legend(loc="upper left", fontsize=8,
                              facecolor=self.PANEL, edgecolor=self.BORDER)
        self.ax_trends.grid(True, alpha=0.2)
        self.ax_trends.set_ylabel("Emails Sent", fontsize=9)

        self.trends_canvas.draw()

    def _refresh_sentiment(self):
        """Redraw the sentiment pie chart."""
        self.ax_sent.clear()
        self.ax_sent.set_facecolor(self.PANEL)

        rows = self.db.execute(
            "SELECT sentiment, COUNT(*) FROM replies GROUP BY sentiment"
        ).fetchall()

        labels, sizes, colors = [], [], []
        color_map = {
            "positive": self.GREEN, "neutral": self.DIM,
            "hostile": self.RED, None: self.PURPLE
        }
        for sentiment, count in rows:
            labels.append((sentiment or "unknown").title())
            sizes.append(count)
            colors.append(color_map.get(sentiment, self.PURPLE))

        if not sizes:
            self.ax_sent.text(0.5, 0.5, "No reply data",
                              ha="center", va="center",
                              color=self.DIM, fontsize=11,
                              transform=self.ax_sent.transAxes)
        else:
            self.ax_sent.pie(
                sizes, labels=labels, colors=colors,
                autopct="%1.0f%%", startangle=140,
                textprops={"fontsize": 9, "color": self.TEXT},
                pctdistance=0.75, labeldistance=1.1
            )

        self.sent_canvas.draw()

    def _refresh_sequence(self):
        """Redraw the sequence comparison bar chart."""
        self.ax_seq.clear()
        self.ax_seq.set_facecolor(self.PANEL)

        seqs = ["school", "csr"]
        sent_vals, replied_vals, bounced_vals = [], [], []

        for seq in seqs:
            row = self.db.execute("""
                SELECT COUNT(DISTINCT s.recipient_id)
                FROM sends s JOIN recipients r ON r.id = s.recipient_id
                WHERE r.sequence_id=? AND s.status='sent'
            """, (seq,)).fetchone()
            sent_vals.append(row[0] if row else 0)

            row = self.db.execute("""
                SELECT COUNT(DISTINCT s.recipient_id)
                FROM sends s JOIN recipients r ON r.id = s.recipient_id
                WHERE r.sequence_id=? AND s.status='replied'
            """, (seq,)).fetchone()
            replied_vals.append(row[0] if row else 0)

            row = self.db.execute("""
                SELECT COUNT(DISTINCT s.recipient_id)
                FROM sends s JOIN recipients r ON r.id = s.recipient_id
                WHERE r.sequence_id=? AND s.status='bounced'
            """, (seq,)).fetchone()
            bounced_vals.append(row[0] if row else 0)

        x = range(len(seqs))
        w = 0.25

        self.ax_seq.bar([i - w for i in x], sent_vals, w,
                        label="Sent", color=self.CYAN, edgecolor="none")
        self.ax_seq.bar(x, replied_vals, w,
                        label="Replied", color=self.GREEN, edgecolor="none")
        self.ax_seq.bar([i + w for i in x], bounced_vals, w,
                        label="Bounced", color=self.RED, edgecolor="none")

        self.ax_seq.set_xticks(x)
        self.ax_seq.set_xticklabels([s.upper() for s in seqs], fontsize=10)
        self.ax_seq.legend(fontsize=8, facecolor=self.PANEL,
                           edgecolor=self.BORDER)
        self.ax_seq.grid(True, alpha=0.2, axis="y")
        self.ax_seq.set_ylabel("Count", fontsize=9)

        self.seq_canvas.draw()

    def _refresh_activity(self):
        """Update the recent activity feed."""
        # Clear old items
        for child in self.activity_frame.winfo_children():
            child.destroy()

        rows = self.db.execute("""
            SELECT s.created_at, r.sequence_id, r.email, s.day, s.status
            FROM sends s JOIN recipients r ON r.id = s.recipient_id
            ORDER BY s.created_at DESC LIMIT 20
        """).fetchall()

        if not rows:
            ctk.CTkLabel(self.activity_frame, text="No activity yet",
                         text_color=self.DIM, font=("Segoe UI", 10))
            return

        for created_at, seq, email, day, status in rows:
            row_frame = ctk.CTkFrame(self.activity_frame, fg_color="transparent",
                                      height=26)
            row_frame.pack(fill="x", pady=1)
            row_frame.pack_propagate(False)

            # Status dot
            dot_color = {
                "sent": self.GREEN, "replied": self.CYAN,
                "bounced": self.RED
            }.get(status, self.DIM)
            dot = ctk.CTkFrame(row_frame, fg_color=dot_color, width=6, height=6,
                               corner_radius=3)
            dot.pack(side="left", padx=(5, 8), pady=0)

            # Day badge
            ctk.CTkLabel(row_frame, text=f"D{day}", font=("Segoe UI", 8, "bold"),
                         text_color=self.CYAN, width=20).pack(side="left")

            # Sequence badge
            seq_color = self.CYAN if seq == "school" else self.GOLD
            ctk.CTkLabel(row_frame, text=seq.upper(), font=("Segoe UI", 7, "bold"),
                         text_color=seq_color, width=35).pack(side="left")

            # Email
            ctk.CTkLabel(row_frame, text=email, font=("Consolas", 9),
                         text_color=self.TEXT).pack(side="left", padx=(5, 0))

            # Status pill
            pill_color = {
                "sent": (self.GREEN, f"rgba(52,199,89,0.15)"),
                "replied": (self.CYAN, f"rgba(89,206,217,0.15)"),
                "bounced": (self.RED, f"rgba(255,59,48,0.15)")
            }.get(status, (self.DIM, self.PANEL))
            ctk.CTkLabel(row_frame, text=status.upper(), font=("Segoe UI", 7, "bold"),
                         text_color=pill_color[0], width=50).pack(side="right", padx=5)


# ═══════════════════════════════════════════════════════════════════
# HOW TO ADD TO RAJ (2 lines only)
# ═══════════════════════════════════════════════════════════════════
#
# STEP 1: Save this file as raj_charts.py in your raj-desktop folder.
#         (Same folder as raj_chat.py, engine.py, main.py)
#
# STEP 2: Open raj_chat.py and find where tabs are created.
#         Look for something like:
#             self.tabview.add("Chat")
#             self.tabview.add("Settings")
#
# STEP 3: Add these 2 lines RIGHT AFTER the other tabview.add() lines:
#
#             self.tabview.add("Charts")
#
# STEP 4: Find where tab contents are built (usually after the add lines).
#         Add these 2 lines there:
#
#             from raj_charts import ChartsTab
#             ChartsTab(self.tabview.tab("Charts"), self.engine.db)
#
# STEP 5: Make sure you have matplotlib installed:
#         Open Command Prompt and run:  pip install matplotlib
#
# STEP 6: Double-click START.bat to run. Click the "Charts" tab.
#
# Done. No other changes needed.
# ═══════════════════════════════════════════════════════════════════
