"""
analytics.py — Engagement analytics and chart generation for Raj.
Uses CustomTkinter native widgets (no matplotlib dependency).
"""

import customtkinter as ctk
from datetime import datetime, timedelta


class AnalyticsView:
    """Analytics dashboard rendered inside a CTkFrame."""

    def __init__(self, parent, db, engine):
        self.parent = parent
        self.db = db
        self.engine = engine
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.frame.pack(fill="both", expand=True)
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        # Title
        ctk.CTkLabel(self.frame, text="📊 Engagement Analytics", font=("Segoe UI", 20, "bold"),
                     text_color="white").pack(anchor="w", pady=(10, 20), padx=20)

        # Summary cards row
        self.cards_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.card_widgets = {}
        card_specs = [
            ("sent", "📧 Sent", "#3b82f6"),
            ("opened", "👁 Opened", "#10b981"),
            ("clicked", "🖱 Clicked", "#f59e0b"),
            ("open_rate", "📈 Open Rate", "#8b5cf6"),
            ("ctr", "🎯 CTR", "#ec4899"),
        ]
        for key, label, color in card_specs:
            card = ctk.CTkFrame(self.cards_frame, fg_color="#1a1a3e", corner_radius=10, width=160)
            card.pack(side="left", padx=(0, 12), fill="y")
            ctk.CTkLabel(card, text=label, font=("Segoe UI", 11), text_color="#888").pack(pady=(12, 4), padx=16)
            val_lbl = ctk.CTkLabel(card, text="—", font=("Segoe UI", 24, "bold"), text_color=color)
            val_lbl.pack(pady=(0, 12), padx=16)
            self.card_widgets[key] = val_lbl

        # Two-column layout: Daily chart + Funnel
        self.charts_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.charts_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Left: Daily breakdown
        self.daily_frame = ctk.CTkFrame(self.charts_frame, fg_color="#1a1a3e", corner_radius=10)
        self.daily_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        ctk.CTkLabel(self.daily_frame, text="Daily Activity (Last 30 Days)", font=("Segoe UI", 14, "bold"),
                     text_color="white").pack(anchor="w", padx=16, pady=(12, 8))
        self.daily_container = ctk.CTkFrame(self.daily_frame, fg_color="transparent")
        self.daily_container.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        # Right: Funnel + Top Links
        self.right_frame = ctk.CTkFrame(self.charts_frame, fg_color="transparent")
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Funnel
        self.funnel_frame = ctk.CTkFrame(self.right_frame, fg_color="#1a1a3e", corner_radius=10)
        self.funnel_frame.pack(fill="both", expand=True, pady=(0, 10))
        ctk.CTkLabel(self.funnel_frame, text="Conversion Funnel", font=("Segoe UI", 14, "bold"),
                     text_color="white").pack(anchor="w", padx=16, pady=(12, 8))
        self.funnel_container = ctk.CTkFrame(self.funnel_frame, fg_color="transparent")
        self.funnel_container.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        # Top clicked links
        self.links_frame = ctk.CTkFrame(self.right_frame, fg_color="#1a1a3e", corner_radius=10)
        self.links_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(self.links_frame, text="Top Clicked Links", font=("Segoe UI", 14, "bold"),
                     text_color="white").pack(anchor="w", padx=16, pady=(12, 8))
        self.links_container = ctk.CTkFrame(self.links_frame, fg_color="transparent")
        self.links_container.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        # Refresh button
        ctk.CTkButton(self.frame, text="🔄 Refresh", command=self._refresh, fg_color="#0d9b8a",
                      hover_color="#0bc5b0", font=("Segoe UI", 12)).pack(anchor="e", padx=20, pady=(0, 10))

    def _refresh(self):
        # Summary stats
        stats = self.db.get_engagement_stats(days_back=30)
        self.card_widgets["sent"].configure(text=str(stats.get("sent", 0)))
        self.card_widgets["opened"].configure(text=str(stats.get("opened", 0)))
        self.card_widgets["clicked"].configure(text=str(stats.get("clicked", 0)))
        self.card_widgets["open_rate"].configure(text=f"{stats.get('open_rate', 0)}%")
        self.card_widgets["ctr"].configure(text=f"{stats.get('ctr', 0)}%")

        # Daily chart
        self._render_daily_chart()

        # Funnel
        self._render_funnel(stats)

        # Top links
        self._render_top_links()

    def _render_daily_chart(self):
        for w in self.daily_container.winfo_children():
            w.destroy()

        data = self.db.get_engagement_by_day(days_back=14)
        if not data:
            ctk.CTkLabel(self.daily_container, text="No data yet. Emails need to be opened/clicked to appear here.",
                         font=("Segoe UI", 11), text_color="#666").pack(pady=20)
            return

        # Header row
        hdr = ctk.CTkFrame(self.daily_container, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(hdr, text="Date", font=("Segoe UI", 10, "bold"), text_color="#888", width=80).pack(side="left")
        ctk.CTkLabel(hdr, text="Sent", font=("Segoe UI", 10, "bold"), text_color="#3b82f6", width=50).pack(side="left")
        ctk.CTkLabel(hdr, text="Opened", font=("Segoe UI", 10, "bold"), text_color="#10b981", width=50).pack(side="left")
        ctk.CTkLabel(hdr, text="Clicked", font=("Segoe UI", 10, "bold"), text_color="#f59e0b", width=50).pack(side="left")

        max_sent = max((d.get("sent", 0) for d in data), default=1) or 1

        for row in data:
            day = row.get("day", "")
            sent = row.get("sent", 0)
            opened = row.get("opened", 0)
            clicked = row.get("clicked", 0)

            row_f = ctk.CTkFrame(self.daily_container, fg_color="transparent")
            row_f.pack(fill="x", pady=2)

            ctk.CTkLabel(row_f, text=day, font=("Segoe UI", 10), text_color="#aaa", width=80).pack(side="left")
            ctk.CTkLabel(row_f, text=str(sent), font=("Segoe UI", 10), text_color="#3b82f6", width=50).pack(side="left")
            ctk.CTkLabel(row_f, text=str(opened), font=("Segoe UI", 10), text_color="#10b981", width=50).pack(side="left")
            ctk.CTkLabel(row_f, text=str(clicked), font=("Segoe UI", 10), text_color="#f59e0b", width=50).pack(side="left")

            # Mini bar
            bar_w = 120
            bar = ctk.CTkFrame(row_f, fg_color="#2a2a4e", width=bar_w, height=12, corner_radius=6)
            bar.pack(side="left", padx=(8, 0))
            bar.pack_propagate(False)
            if sent > 0:
                fill_w = max(int(bar_w * (sent / max_sent)), 1)
                fill = ctk.CTkFrame(bar, fg_color="#3b82f6", width=fill_w, height=12, corner_radius=6)
                fill.pack(side="left")

    def _render_funnel(self, stats):
        for w in self.funnel_container.winfo_children():
            w.destroy()

        sent = stats.get("sent", 0)
        opened = stats.get("opened", 0)
        clicked = stats.get("clicked", 0)

        if sent == 0:
            ctk.CTkLabel(self.funnel_container, text="No sends yet.",
                         font=("Segoe UI", 11), text_color="#666").pack(pady=20)
            return

        stages = [
            ("Sent", sent, "#3b82f6", 1.0),
            ("Opened", opened, "#10b981", opened / sent if sent else 0),
            ("Clicked", clicked, "#f59e0b", clicked / sent if sent else 0),
        ]

        for label, value, color, pct in stages:
            row = ctk.CTkFrame(self.funnel_container, fg_color="transparent")
            row.pack(fill="x", pady=4)

            lbl = ctk.CTkLabel(row, text=f"{label}", font=("Segoe UI", 12), text_color="white", width=80)
            lbl.pack(side="left")

            bar_frame = ctk.CTkFrame(row, fg_color="#2a2a4e", height=20, corner_radius=10)
            bar_frame.pack(side="left", fill="x", expand=True, padx=(8, 8))
            bar_frame.pack_propagate(False)

            fill_w = max(int(300 * pct), 2)
            fill = ctk.CTkFrame(bar_frame, fg_color=color, height=20, corner_radius=10)
            fill.pack(side="left")
            fill.configure(width=fill_w)

            pct_text = f"{value} ({round(pct*100,1)}%)"
            ctk.CTkLabel(row, text=pct_text, font=("Segoe UI", 11), text_color=color, width=90).pack(side="left")

    def _render_top_links(self):
        for w in self.links_container.winfo_children():
            w.destroy()

        links = self.db.get_top_clicked_links(limit=8)
        if not links:
            ctk.CTkLabel(self.links_container, text="No clicks yet.",
                         font=("Segoe UI", 11), text_color="#666").pack(pady=10)
            return

        for link in links:
            url = link.get("url", "")[:60]
            clicks = link.get("clicks", 0)
            row = ctk.CTkFrame(self.links_container, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"{clicks}", font=("Segoe UI", 11, "bold"),
                         text_color="#f59e0b", width=30).pack(side="left")
            ctk.CTkLabel(row, text=url, font=("Segoe UI", 10),
                         text_color="#aaa").pack(side="left", padx=(8, 0))
