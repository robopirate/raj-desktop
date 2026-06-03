"""
raj_clay_ui.py -- Claymorphism UI System for Raj v4.4
Drop-in claymorphic cards, buttons, and frames.
Import this and use the ClayUI helpers to build beautiful 3D clay interfaces.

Usage in raj_chat.py:
    from raj_clay_ui import ClayUI, CLAY
    
    # Then replace your view builders with clay versions:
    ClayUI.build_clay_dashboard(self)
    ClayUI.build_clay_batches(self)
"""

import customtkinter as ctk
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════
# CLAYMORPHISM DESIGN SYSTEM (Dark Theme Adaptation)
# ═══════════════════════════════════════════════════════════════════

class CLAY:
    """Claymorphism color and shadow system."""
    
    # ── Background layers ──
    BG = "#0f0f1a"           # Deepest background
    BG_LIGHT = "#16162a"      # Slightly lifted surface
    SURFACE = "#1e1e36"       # Card/clay surface
    SURFACE_HOVER = "#252540"  # Hover state
    
    # ── Clay shadow system (the magic) ──
    # Inner highlight (top-left light source)
    SHADOW_INSET = "#2a2a4e"   # Inner shadow color
    SHADOW_HIGHLIGHT = "#3a3a5e"  # Inner highlight (top-left)
    
    # Outer soft shadow (creates floating effect)
    SHADOW_OUTER = "#0a0a14"   # Dark outer shadow
    SHADOW_GLOW = "#59ced9"     # Accent glow
    
    # ── Brand colors (muted for clay look) ──
    CYAN = "#4ecdc4"           # Muted teal-cyan
    CYAN_SOFT = "rgba(78,205,196,0.15)"
    GOLD = "#f7b731"           # Muted gold
    GOLD_SOFT = "rgba(247,183,49,0.15)"
    GREEN = "#6bcb77"          # Soft green
    GREEN_SOFT = "rgba(107,203,119,0.15)"
    RED = "#e76f6f"            # Soft red
    RED_SOFT = "rgba(231,111,111,0.15)"
    PURPLE = "#a78bfa"         # Soft purple
    
    # ── Text ──
    TEXT = "#e8e8f0"
    TEXT_DIM = "#9ca3af"
    TEXT_MUTED = "#6b7280"
    
    # ── Clay geometry ──
    RADIUS_SMALL = 12
    RADIUS_MED = 20
    RADIUS_LARGE = 28
    RADIUS_PILL = 50
    
    # ── Shadows ──
    @staticmethod
    def shadow_outset():
        """Soft outer shadow for floating clay effect."""
        return {
            "corner_radius": CLAY.RADIUS_MED,
            "border_width": 0,
        }
    
    @staticmethod
    def shadow_inset():
        """Inner shadow for pressed/clay effect."""
        return {
            "corner_radius": CLAY.RADIUS_MED,
            "border_width": 2,
            "border_color": CLAY.SHADOW_INSET,
        }


# ═══════════════════════════════════════════════════════════════════
# CLAY UI BUILDER
# ═══════════════════════════════════════════════════════════════════

class ClayUI:
    """Claymorphism UI component factory."""
    
    # ── Card Builders ──
    
    @staticmethod
    def clay_card(parent, fg_color=None, radius=None, height=None):
        """Create a claymorphic card with soft 3D appearance."""
        fg = fg_color or CLAY.SURFACE
        r = radius or CLAY.RADIUS_MED
        
        card = ctk.CTkFrame(
            parent,
            fg_color=fg,
            corner_radius=r,
            border_width=0,
        )
        if height:
            card.configure(height=height)
            card.pack_propagate(False)
        return card
    
    @staticmethod
    def clay_card_inset(parent, fg_color=None):
        """Create a pressed/clay-inset card."""
        fg = fg_color or CLAY.BG_LIGHT
        
        card = ctk.CTkFrame(
            parent,
            fg_color=fg,
            corner_radius=CLAY.RADIUS_MED,
            border_width=2,
            border_color=CLAY.SHADOW_INSET,
        )
        return card
    
    @staticmethod
    def clay_kpi_card(parent, title, value, color, subtitle=""):
        """A beautiful claymorphic KPI card."""
        card = ctk.CTkFrame(
            parent,
            fg_color=CLAY.SURFACE,
            corner_radius=CLAY.RADIUS_MED,
            border_width=0,
            height=100,
        )
        card.pack_propagate(False)
        
        # Top color accent bar
        accent = ctk.CTkFrame(card, fg_color=color, height=4,
                               corner_radius=2)
        accent.pack(fill="x", padx=16, pady=(12, 0))
        
        # Value
        ctk.CTkLabel(card, text=value,
                     font=("Segoe UI", 26, "bold"),
                     text_color=color).pack(anchor="w", padx=16, pady=(6, 0))
        
        # Title
        ctk.CTkLabel(card, text=title.upper(),
                     font=("Segoe UI", 9),
                     text_color=CLAY.TEXT_DIM).pack(anchor="w", padx=16)
        
        if subtitle:
            ctk.CTkLabel(card, text=subtitle,
                         font=("Segoe UI", 8),
                         text_color=CLAY.TEXT_MUTED).pack(anchor="w", padx=16)
        
        return card
    
    @staticmethod
    def clay_batch_card(parent, batch_name, sequence, day, sent, total,
                        status, scheduled, rate):
        """Beautiful claymorphic batch card (like Dashboard cards)."""
        
        # Status color
        status_colors = {
            "running": (CLAY.GREEN, "▶ Running"),
            "scheduled": (CLAY.GOLD, "⏳ Scheduled"),
            "draft": (CLAY.TEXT_DIM, "📝 Draft"),
            "paused": (CLAY.RED, "⏸ Paused"),
            "completed": (CLAY.CYAN, "✓ Completed"),
        }
        status_color, status_text = status_colors.get(
            status.lower(), (CLAY.TEXT_DIM, status))
        
        # Sequence color
        seq_color = CLAY.CYAN if sequence.lower() == "school" else CLAY.GOLD
        
        # Card
        card = ctk.CTkFrame(
            parent,
            fg_color=CLAY.SURFACE,
            corner_radius=CLAY.RADIUS_MED,
            border_width=0,
        )
        
        # ── Card Header ──
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 6))
        
        # Batch name + sequence badge
        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left", fill="y")
        
        ctk.CTkLabel(left, text=batch_name,
                     font=("Segoe UI", 14, "bold"),
                     text_color=CLAY.TEXT).pack(anchor="w")
        
        # Sequence badge (clay pill)
        badge = ctk.CTkFrame(left, fg_color=f"{seq_color}20",
                              corner_radius=CLAY.RADIUS_PILL,
                              height=20)
        badge.pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(badge, text=sequence.upper(),
                     font=("Segoe UI", 8, "bold"),
                     text_color=seq_color).pack(padx=8, pady=1)
        
        # Status badge (right side)
        ctk.CTkLabel(header, text=status_text,
                     font=("Segoe UI", 10, "bold"),
                     text_color=status_color).pack(side="right")
        
        # ── Day indicator ──
        day_row = ctk.CTkFrame(card, fg_color="transparent")
        day_row.pack(fill="x", padx=16, pady=2)
        
        ctk.CTkLabel(day_row, text=f"Day {day}",
                     font=("Segoe UI", 11),
                     text_color=CLAY.TEXT_DIM).pack(side="left")
        ctk.CTkLabel(day_row, text=scheduled,
                     font=("Segoe UI", 9),
                     text_color=CLAY.TEXT_MUTED).pack(side="right")
        
        # ── Progress ──
        progress_row = ctk.CTkFrame(card, fg_color="transparent")
        progress_row.pack(fill="x", padx=16, pady=(4, 4))
        
        pct = (sent / total * 100) if total > 0 else 0
        
        ctk.CTkLabel(progress_row,
                     text=f"{sent}/{total} sent",
                     font=("Segoe UI", 11, "bold"),
                     text_color=CLAY.TEXT).pack(side="left")
        ctk.CTkLabel(progress_row,
                     text=f"{pct:.0f}%",
                     font=("Segoe UI", 11, "bold"),
                     text_color=status_color).pack(side="right")
        
        # ── Progress Bar (clay style) ──
        bar_bg = ctk.CTkFrame(card, fg_color=CLAY.BG,
                               corner_radius=CLAY.RADIUS_PILL,
                               height=8)
        bar_bg.pack(fill="x", padx=16, pady=(0, 4))
        
        if pct > 0:
            bar_fill = ctk.CTkFrame(bar_bg, fg_color=status_color,
                                     corner_radius=CLAY.RADIUS_PILL,
                                     height=8)
            bar_fill.place(relx=0, rely=0, relwidth=pct/100, relheight=1)
        
        # ── Action Buttons ──
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(4, 12))
        
        if status.lower() in ("draft", "scheduled"):
            ClayUI.clay_button(btn_row, "▶ Start", CLAY.GREEN,
                               command=lambda: None).pack(side="left", padx=(0, 6))
        elif status.lower() == "running":
            ClayUI.clay_button(btn_row, "⏸ Pause", CLAY.GOLD,
                               command=lambda: None).pack(side="left", padx=(0, 6))
        
        ClayUI.clay_button(btn_row, "🗑 Delete", CLAY.RED,
                           fg_color=f"{CLAY.RED}20",
                           command=lambda: None).pack(side="left", padx=(0, 6))
        ClayUI.clay_button(btn_row, "📋 Details", CLAY.TEXT_DIM,
                           fg_color=CLAY.BG_LIGHT,
                           command=lambda: None).pack(side="left")
        
        return card
    
    @staticmethod
    def clay_button(parent, text, text_color, fg_color=None,
                    hover_color=None, height=32, width=None,
                    font_size=11, command=None):
        """Claymorphic pill button with soft 3D look."""
        fg = fg_color or f"{text_color}20"
        
        # Derive hover color
        if hover_color:
            hc = hover_color
        elif fg_color and fg_color != f"{text_color}20":
            hc = fg_color
        else:
            hc = f"{text_color}35"
        
        btn = ctk.CTkButton(
            parent,
            text=text,
            font=("Segoe UI", font_size, "bold"),
            text_color=text_color,
            fg_color=fg,
            hover_color=hc,
            height=height,
            width=width,
            corner_radius=CLAY.RADIUS_PILL,
            border_width=0,
            command=command,
        )
        return btn
    
    @staticmethod
    def clay_day_card(parent, day, total, sent, bounced, replied, status):
        """Claymorphic day pipeline card (D1, D3, D5, D7, D10)."""
        
        status_config = {
            "completed": (CLAY.GREEN, "✓ Done"),
            "running": (CLAY.CYAN, "▶ Active"),
            "pending": (CLAY.GOLD, "⏳ Pending"),
            "draft": (CLAY.TEXT_DIM, "Draft"),
        }
        color, label = status_config.get(status.lower(),
                                          (CLAY.TEXT_DIM, status))
        
        pct = (sent / total * 100) if total > 0 else 0
        
        card = ctk.CTkFrame(
            parent,
            fg_color=CLAY.SURFACE,
            corner_radius=CLAY.RADIUS_MED,
            border_width=0,
            width=140,
            height=160,
        )
        card.pack_propagate(False)
        
        # Day header
        ctk.CTkLabel(card, text=f"DAY {day}",
                     font=("Segoe UI", 10, "bold"),
                     text_color=color).pack(anchor="w", padx=12, pady=(10, 2))
        
        # Sent count (big)
        ctk.CTkLabel(card, text=f"{sent}/{total}",
                     font=("Segoe UI", 20, "bold"),
                     text_color=CLAY.TEXT).pack(anchor="w", padx=12)
        
        # Replied/bounced
        if replied > 0:
            ctk.CTkLabel(card, text=f"💬 {replied} replies",
                         font=("Segoe UI", 8),
                         text_color=CLAY.CYAN).pack(anchor="w", padx=12)
        if bounced > 0:
            ctk.CTkLabel(card, text=f"⚠ {bounced} bounced",
                         font=("Segoe UI", 8),
                         text_color=CLAY.RED).pack(anchor="w", padx=12)
        
        # Progress bar
        bar_bg = ctk.CTkFrame(card, fg_color=CLAY.BG,
                               corner_radius=CLAY.RADIUS_PILL,
                               height=6)
        bar_bg.pack(fill="x", padx=12, pady=(6, 4))
        
        if pct > 0:
            bar = ctk.CTkFrame(bar_bg, fg_color=color,
                                corner_radius=CLAY.RADIUS_PILL,
                                height=6)
            bar.place(relx=0, rely=0, relwidth=pct/100, relheight=1)
        
        # Status badge
        badge = ctk.CTkFrame(card, fg_color=f"{color}15",
                              corner_radius=CLAY.RADIUS_PILL)
        badge.pack(anchor="w", padx=12, pady=(2, 0))
        ctk.CTkLabel(badge, text=label,
                     font=("Segoe UI", 8, "bold"),
                     text_color=color).pack(padx=8, pady=2)
        
        return card
    
    # ═══════════════════════════════════════════════════════════
    # COMPLETE VIEW BUILDERS (Drop-in replacements)
    # ═══════════════════════════════════════════════════════════
    
    @staticmethod
    def build_clay_batches(ui_instance):
        """Build the Batches tab with claymorphism + card layout."""
        
        view = ctk.CTkFrame(ui_instance.content, fg_color=CLAY.BG)
        ui_instance.views["batches"] = view
        view.grid_columnconfigure(0, weight=1)
        view.grid_rowconfigure(2, weight=1)
        
        # ── Header ──
        header = ctk.CTkFrame(view, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(header, text="🚀 Batches",
                     font=("Segoe UI", 22, "bold"),
                     text_color=CLAY.TEXT).pack(side="left")
        
        ClayUI.clay_button(header, "+ From Pool", CLAY.CYAN,
                           command=lambda: None).pack(side="right")
        
        # ── Stats Row ──
        stats = ctk.CTkFrame(view, fg_color="transparent")
        stats.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        # Get batch counts from DB
        try:
            db = ui_instance.engine.db
            running = db.execute(
                "SELECT COUNT(*) FROM batches WHERE status='running'"
            ).fetchone()[0]
            scheduled = db.execute(
                "SELECT COUNT(*) FROM batches WHERE status='scheduled'"
            ).fetchone()[0]
            completed = db.execute(
                "SELECT COUNT(*) FROM batches WHERE status='completed'"
            ).fetchone()[0]
        except Exception:
            running = scheduled = completed = 0
        
        ClayUI.clay_kpi_card(stats, "Running", str(running),
                             CLAY.CYAN).pack(side="left", fill="x",
                                              expand=True, padx=4)
        ClayUI.clay_kpi_card(stats, "Scheduled", str(scheduled),
                             CLAY.GOLD).pack(side="left", fill="x",
                                              expand=True, padx=4)
        ClayUI.clay_kpi_card(stats, "Completed", str(completed),
                             CLAY.GREEN).pack(side="left", fill="x",
                                              expand=True, padx=4)
        
        # ── Scrollable Batch Cards ──
        scroll = ctk.CTkScrollableFrame(
            view, fg_color=CLAY.BG,
            scrollbar_button_color=CLAY.SURFACE,
            scrollbar_button_hover_color=CLAY.CYAN,
        )
        scroll.grid(row=2, column=0, sticky="nsew", padx=15, pady=5)
        
        # Load batches from DB
        try:
            db = ui_instance.engine.db
            rows = db.execute("""
                SELECT b.id, b.name, b.sequence_id, b.status,
                       b.scheduled_at, b.day_offset, b.stagger_minutes,
                       COUNT(DISTINCT br.recipient_id) as total,
                       COUNT(DISTINCT CASE WHEN br.status='sent'
                              THEN br.recipient_id END) as sent
                FROM batches b
                LEFT JOIN batch_recipients br ON br.batch_id = b.id
                GROUP BY b.id
                ORDER BY b.created_at DESC
            """).fetchall()
        except Exception:
            rows = []
        
        if not rows:
            ctk.CTkLabel(scroll, text="No batches yet",
                         font=("Segoe UI", 14),
                         text_color=CLAY.TEXT_DIM).pack(pady=50)
        
        # Two-column grid for cards
        cards_container = ctk.CTkFrame(scroll, fg_color="transparent")
        cards_container.pack(fill="x", expand=True)
        cards_container.grid_columnconfigure(0, weight=1)
        cards_container.grid_columnconfigure(1, weight=1)
        
        for i, row in enumerate(rows):
            bid, name, seq, status, sched, day, stagger, total, sent = row
            sched_str = str(sched) if sched else "Not scheduled"
            
            card = ClayUI.clay_batch_card(
                cards_container, name, seq, day, sent or 0, total or 0,
                status, sched_str, stagger or 2,
            )
            card.grid(row=i // 2, column=i % 2, sticky="ew",
                       padx=6, pady=6)
    
    @staticmethod
    def build_clay_dashboard(ui_instance):
        """Build Dashboard with claymorphism + pipeline cards."""
        
        view = ctk.CTkFrame(ui_instance.content, fg_color=CLAY.BG)
        ui_instance.views["dashboard"] = view
        view.grid_columnconfigure(0, weight=1)
        view.grid_rowconfigure(3, weight=1)
        
        # ── KPI Cards Row ──
        kpi = ctk.CTkFrame(view, fg_color="transparent")
        kpi.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        
        try:
            db = ui_instance.engine.db
            total_leads = db.execute(
                "SELECT COUNT(*) FROM recipients"
            ).fetchone()[0]
            total_sent = db.execute(
                "SELECT COUNT(DISTINCT recipient_id) FROM sends "
                "WHERE status='sent'"
            ).fetchone()[0]
            total_replied = db.execute(
                "SELECT COUNT(DISTINCT recipient_id) FROM sends "
                "WHERE status='replied'"
            ).fetchone()[0]
            rate = round((total_replied / total_sent * 100), 1) \
                if total_sent > 0 else 0
        except Exception:
            total_leads = total_sent = total_replied = rate = 0
        
        ClayUI.clay_kpi_card(kpi, "Total Leads", f"{total_leads:,}",
                             CLAY.CYAN).pack(side="left", fill="x",
                                              expand=True, padx=4)
        ClayUI.clay_kpi_card(kpi, "Emails Sent", f"{total_sent:,}",
                             CLAY.GREEN).pack(side="left", fill="x",
                                              expand=True, padx=4)
        ClayUI.clay_kpi_card(kpi, "Replied", f"{total_replied:,}",
                             CLAY.GOLD).pack(side="left", fill="x",
                                              expand=True, padx=4)
        ClayUI.clay_kpi_card(kpi, "Reply Rate", f"{rate}%",
                             CLAY.PURPLE).pack(side="left", fill="x",
                                              expand=True, padx=4)
        
        # ── Pipeline Section ──
        pipe_header = ctk.CTkFrame(view, fg_color="transparent")
        pipe_header.grid(row=1, column=0, sticky="ew",
                          padx=20, pady=(15, 5))
        ctk.CTkLabel(pipe_header, text="📊 Day-wise Pipeline",
                     font=("Segoe UI", 18, "bold"),
                     text_color=CLAY.TEXT).pack(side="left")
        
        # Pipeline for each sequence
        pipe_frame = ctk.CTkFrame(view, fg_color="transparent")
        pipe_frame.grid(row=2, column=0, sticky="ew",
                         padx=15, pady=5)
        
        for seq_id, seq_name, seq_color in [
            ("school", "SCHOOL", CLAY.CYAN),
            ("csr", "CSR", CLAY.GOLD),
        ]:
            # Sequence section
            seq_frame = ClayUI.clay_card(pipe_frame, radius=CLAY.RADIUS_LARGE)
            seq_frame.pack(fill="x", pady=8, padx=5)
            
            # Sequence header
            sh = ctk.CTkFrame(seq_frame, fg_color="transparent")
            sh.pack(fill="x", padx=16, pady=(10, 6))
            
            dot = ctk.CTkFrame(sh, fg_color=seq_color,
                                width=10, height=10,
                                corner_radius=5)
            dot.pack(side="left", padx=(0, 8))
            ctk.CTkLabel(sh, text=seq_name,
                         font=("Segoe UI", 13, "bold"),
                         text_color=seq_color).pack(side="left")
            
            # Day cards row
            days_frame = ctk.CTkFrame(seq_frame, fg_color="transparent")
            days_frame.pack(fill="x", padx=12, pady=(0, 12))
            
            for day in [1, 3, 5, 7, 10]:
                try:
                    db = ui_instance.engine.db
                    total = db.execute(
                        "SELECT COUNT(DISTINCT s.recipient_id) "
                        "FROM sends s JOIN recipients r ON r.id=s.recipient_id "
                        "WHERE r.sequence_id=? AND s.day=?",
                        (seq_id, day)
                    ).fetchone()[0]
                    sent = db.execute(
                        "SELECT COUNT(DISTINCT s.recipient_id) "
                        "FROM sends s JOIN recipients r ON r.id=s.recipient_id "
                        "WHERE r.sequence_id=? AND s.day=? AND s.status='sent'",
                        (seq_id, day)
                    ).fetchone()[0]
                    bounced = db.execute(
                        "SELECT COUNT(DISTINCT s.recipient_id) "
                        "FROM sends s JOIN recipients r ON r.id=s.recipient_id "
                        "WHERE r.sequence_id=? AND s.day=? AND s.status='bounced'",
                        (seq_id, day)
                    ).fetchone()[0]
                    replied = db.execute(
                        "SELECT COUNT(DISTINCT s.recipient_id) "
                        "FROM sends s JOIN recipients r ON r.id=s.recipient_id "
                        "WHERE r.sequence_id=? AND s.day=? AND s.status='replied'",
                        (seq_id, day)
                    ).fetchone()[0]
                except Exception:
                    total = sent = bounced = replied = 0
                
                status = "completed" if sent >= total and total > 0 else \
                         "running" if sent > 0 else \
                         "pending" if total > 0 else "draft"
                
                day_card = ClayUI.clay_day_card(
                    days_frame, day, total, sent, bounced, replied, status
                )
                day_card.pack(side="left", fill="y", expand=True,
                               padx=4)
        
        # ── Active Batches Section ──
        batch_header = ctk.CTkFrame(view, fg_color="transparent")
        batch_header.grid(row=3, column=0, sticky="ew",
                           padx=20, pady=(15, 5))
        ctk.CTkLabel(batch_header, text="🚀 Active Batches",
                     font=("Segoe UI", 18, "bold"),
                     text_color=CLAY.TEXT).pack(side="left")
        
        # Mini batch cards
        try:
            db = ui_instance.engine.db
            active = db.execute("""
                SELECT b.name, b.sequence_id, b.status, b.day_offset,
                       COUNT(DISTINCT br.recipient_id) as total,
                       COUNT(DISTINCT CASE WHEN br.status='sent'
                              THEN br.recipient_id END) as sent
                FROM batches b
                LEFT JOIN batch_recipients br ON br.batch_id = b.id
                WHERE b.status IN ('running', 'scheduled', 'draft')
                GROUP BY b.id
                ORDER BY b.created_at DESC
                LIMIT 6
            """).fetchall()
        except Exception:
            active = []
        
        if active:
            ab_frame = ctk.CTkFrame(view, fg_color="transparent")
            ab_frame.grid(row=4, column=0, sticky="ew",
                           padx=15, pady=5)
            
            for i, (name, seq, status, day, total, sent) in enumerate(active[:6]):
                mini = ClayUI.clay_batch_card(
                    ab_frame, name, seq, day, sent or 0, total or 0,
                    status, "", 2
                )
                mini.grid(row=i // 2, column=i % 2, sticky="ew",
                           padx=6, pady=6)


# ═══════════════════════════════════════════════════════════════════
# EASY INTEGRATION (What to add to raj_chat.py)
# ═══════════════════════════════════════════════════════════════════

"""
STEP 1: Add this import at the top of raj_chat.py (after other imports):
    
    try:
        from raj_clay_ui import ClayUI, CLAY
        CLAY_AVAILABLE = True
    except ImportError:
        CLAY_AVAILABLE = False

STEP 2: In your __init__ or view builder, replace:
    
    OLD: self._build_batches_view()
    NEW: 
        if CLAY_AVAILABLE:
            ClayUI.build_clay_batches(self)
        else:
            self._build_batches_view()
    
    OLD: self._build_dashboard_view()  
    NEW:
        if CLAY_AVAILABLE:
            ClayUI.build_clay_dashboard(self)
        else:
            self._build_dashboard_view()

STEP 3: Optionally, update sidebar buttons to use clay style:
    
    Replace flat buttons with:
        ClayUI.clay_button(parent, text, color, command=...)

That's it. Drop the file, add the import, change 2 lines.
"""
