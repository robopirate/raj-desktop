# --- Calendar & Drive Integration (v4.0) ---
CALENDAR_AVAILABLE = False
DRIVE_AVAILABLE = False
try:
    from calendar_integration import CalendarManager
    CALENDAR_AVAILABLE = True
except ImportError:
    pass
try:
    from drive_integration import DriveManager
    DRIVE_AVAILABLE = True
except ImportError:
    pass
# --- End Integration ---

"""
engine.py -- RoboPirate Campaign Engine v5.0
SCHOOL + CSR sequences | Raj as manager | Auto-send | Draft-only replies
FIXED: HTML template, auto-advance scheduling, template sync regex
"""

import re
import json
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import deque

from db import Database
from gmail import GmailClient
from tracking_server import TrackingServer

try:
    from smart_importer import SmartImporter
    SMART_IMPORT_AVAILABLE = True
except ImportError:
    SMART_IMPORT_AVAILABLE = False

# Sequences: SCHOOL (private schools) and CSR (corporates)
SEQUENCES = {
    "school": {
        "days": [1, 3, 5, 7, 10],
        "template_prefix": "SCHOOL EMAIL ",
        "audience": "private_school",
        "persona": "school",
        "assets": {
            1: {
                "brochure": "https://drive.google.com/file/d/1vRMeFM22aajc5zfiYhqaev34UVQ87zyU/view",
                "video_wsl": "https://drive.google.com/file/d/1KPrC2IpdooxazGJiyVe79JgyWlJbOxzu/view",
                "video_abp": "https://youtu.be/FJ2_W53WjmA",
                "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/"
            },
            3: {
                "video_abp": "https://youtu.be/FJ2_W53WjmA",
                "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/"
            },
            5: {
                "report_vbv": "https://drive.google.com/file/d/1d7EEtC8YitbSj7U6ivHf_6WtUGuylT-B/view",
                "video_star": "https://youtube.com/watch?v=iziKPBSfGKU",
                "folder_vbv": "https://drive.google.com/drive/folders/1tWu3zrH0zIjJbkfS3hX0tnKXQY-9HTgN",
                "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/"
            },
            7: {
                "profile": "https://drive.google.com/file/d/1g9JJ4_VO_28QKYD7iVVDJZcv9l4uRbZu/view",
                "video_abp": "https://youtu.be/FJ2_W53WjmA",
                "video_star": "https://youtube.com/watch?v=iziKPBSfGKU",
                "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/"
            },
            10: {
                "plans": "https://drive.google.com/file/d/1vRMeFM22aajc5zfiYhqaev34UVQ87zyU/view",
                "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/"
            }
        }
    },
    "csr": {
        "days": [1, 3, 5, 7, 10],
        "template_prefix": "CSR EMAIL ",
        "audience": "csr",
        "persona": "csr",
        "assets": {
            1: {
                "report_sangli1": "https://drive.google.com/file/d/1HpNdnamA2k3H0xkKr58STEKMNu5RgHPx/view",
                "video_abp": "https://youtu.be/FJ2_W53WjmA",
                "video_sangli": "https://drive.google.com/file/d/1MUlsC87vRbhFaoW0XcX146WBLKYBk448/view",
                "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/"
            },
            3: {
                "report_sangli1": "https://drive.google.com/file/d/1HpNdnamA2k3H0xkKr58STEKMNu5RgHPx/view",
                "brochure": "https://drive.google.com/file/d/1vRMeFM22aajc5zfiYhqaev34UVQ87zyU/view",
                "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/"
            },
            5: {
                "report_sangli2": "https://drive.google.com/file/d/1pKSm1WPlPk-we4aC-uhqxEy8w-BYygSN/view",
                "report_vbv": "https://drive.google.com/file/d/1d7EEtC8YitbSj7U6ivHf_6WtUGuylT-B/view",
                "video_star": "https://youtube.com/watch?v=iziKPBSfGKU",
                "folder_sangli": "https://drive.google.com/drive/folders/15sc5iOIKTBZyenb2rCpGVAK1lExcG5BC",
                "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/"
            },
            7: {
                "plans": "https://drive.google.com/file/d/1vRMeFM22aajc5zfiYhqaev34UVQ87zyU/view",
                "video_wsl": "https://drive.google.com/file/d/1KPrC2IpdooxazGJiyVe79JgyWlJbOxzu/view",
                "video_abp": "https://youtu.be/FJ2_W53WjmA",
                "video_sangli": "https://drive.google.com/file/d/1MUlsC87vRbhFaoW0XcX146WBLKYBk448/view",
                "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/"
            },
            10: {
                "profile": "https://drive.google.com/file/d/1g9JJ4_VO_28QKYD7iVVDJZcv9l4uRbZu/view",
                "kits": "https://drive.google.com/file/d/1cvi4p8IHgx1MekanVRHN3Fo4Lk9vbubX/view",
                "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/"
            }
        }
    },
    "csr-wsl-5": {
        "days": [1, 3, 5, 7, 10],
        "template_prefix": "CSR-WSL-5 EMAIL ",
        "audience": "csr",
        "persona": "csr",
        "assets": {
            1: {
                "report_vbv": "https://drive.google.com/file/d/1d7EEtC8YitbSj7U6ivHf_6WtUGuylT-B/view",
                "brochure": "https://drive.google.com/file/d/1vRMeFM22aajc5zfiYhqaev34UVQ87zyU/view",
                "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/"
            },
            3: {
                "report_vbv": "https://drive.google.com/file/d/1d7EEtC8YitbSj7U6ivHf_6WtUGuylT-B/view",
                "video_abp": "https://youtu.be/FJ2_W53WjmA",
                "video_star": "https://youtube.com/watch?v=iziKPBSfGKU",
                "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/"
            },
            5: {
                "video_wsl": "https://drive.google.com/file/d/1KPrC2IpdooxazGJiyVe79JgyWlJbOxzu/view",
                "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/"
            },
            7: {
                "brochure": "https://drive.google.com/file/d/1vRMeFM22aajc5zfiYhqaev34UVQ87zyU/view",
                "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/"
            },
            10: {
                "profile": "https://drive.google.com/file/d/1g9JJ4_VO_28QKYD7iVVDJZcv9l4uRbZu/view",
                "video_ig": "https://www.instagram.com/reel/DMe2HzqofAk/"
            }
        }
    }
}

EMAIL_NUM_TO_DAY = {1: 1, 2: 3, 3: 5, 4: 7, 5: 10}
DAY_TO_EMAIL_NUM = {1: 1, 3: 2, 5: 3, 7: 4, 10: 5}

SEND_DELAY = 45
BOUNCE_INTERVAL = 6
REPLY_INTERVAL = 60
EMERGENCY_INTERVAL = 15
EOD_HOUR = 19
MORNING_HOUR = 8

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body{font-family:Segoe UI,Arial,sans-serif;background:#0A1628;color:#E6EDF3;padding:20px;margin:0}
.container{max-width:600px;margin:0 auto;background:#111D2E;border-radius:12px;padding:30px;border:1px solid #2a2a4e}
.header{text-align:center;border-bottom:2px solid #59ced9;padding-bottom:15px;margin-bottom:20px}
.logo{font-size:28px;font-weight:bold;color:#59ced9}
.sub{color:#8B949E;font-size:12px}
.content{line-height:1.6;font-size:14px}
.footer{margin-top:30px;padding-top:15px;border-top:1px solid #2a2a4e;text-align:center;color:#8B949E;font-size:11px}
.cta{display:inline-block;background:#59ced9;color:#0A1628;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:bold;margin:15px 0}
</style>
</head>
<body>
<div class="container">
<div class="header">
<div class="logo">🤖 RAJ by RoboPirate</div>
<div class="sub">Smart Labs for Smart Schools</div>
</div>
<div class="content">
{body}
</div>
<div class="footer">
© 2026 RoboPirate · robopirate.in · Unsubscribe: reply STOP
</div>
</div>
</body>
</html>"""

@dataclass
class Recipient:
    id: int
    sequence_id: str
    email: str
    name: str
    org: str
    extra_json: str
    import_status: str = ""
    import_error: str = ""
    imported_at: str = ""
    batched: int = 0

@dataclass
class BatchResult:
    queued: int
    sent: int = 0
    drafted: int = 0
    error: Optional[str] = None

class CampaignEngine:
    def __init__(self, db: Database, gmail: GmailClient, ollama_url="http://localhost:11434"):
        self.db = db
        self.gmail = gmail
        self.ollama_url = ollama_url
        self._running = False
        self._thread = None
        self._paused = False
        self._last_batch_process_time = None
        self.brief_email = db.get_meta("brief_email") or ""
        self.calendar = CalendarManager() if CALENDAR_AVAILABLE else None
        self.drive = DriveManager() if DRIVE_AVAILABLE else None
        self.logs = deque(maxlen=200)
        self._log_callbacks = []
        self.tracker = None

    def add_log_callback(self, fn):
        self._log_callbacks.append(fn)

    def _log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        self.logs.append(line)
        print(f"[Engine] {msg}")
        for fn in self._log_callbacks:
            try:
                fn(line)
            except:
                pass

    # -- Lifecycle --
    def start(self):
        if self._running: return
        self._running = True

        # Start tracking server for engagement analytics
        try:
            self.tracker = TrackingServer(self.db.db_path)
            self.tracker.start()
            self._log(f"[Tracking] Engagement tracking active at {self.tracker.base_url}")
        except Exception as e:
            self._log(f"[Tracking] Failed to start: {e}")

        # RESUME-ON-BOOT: Check for batches stuck in "running" status
        try:
            running_batches = self.db.get_running_batches()
            if running_batches:
                self._log(f"[RESUME] Found {len(running_batches)} batch(es) in RUNNING status from previous session")
                for batch in running_batches:
                    self._log(f"[RESUME] Will continue batch '{batch['name']}' (ID: {batch['id']})")
            else:
                self._log("[RESUME] No running batches from previous session")

            # Also check scheduled batches that may have missed their time
            scheduled_batches = self.db.get_scheduled_batches()
            if scheduled_batches:
                now = datetime.now()
                missed = 0
                for batch in scheduled_batches:
                    sched_str = batch.get("scheduled_at")
                    if sched_str:
                        try:
                            sched_dt = datetime.fromisoformat(sched_str)
                            if now > sched_dt:
                                missed += 1
                                self._log(f"[RESUME] Batch '{batch['name']}' missed schedule ({sched_dt.strftime('%d %b %H:%M')}) — will auto-start")
                        except:
                            pass
                if missed > 0:
                    self._log(f"[RESUME] {missed} scheduled batch(es) missed their time while system was off")
        except Exception as e:
            self._log(f"[RESUME] Error checking previous state: {e}")

        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        self._log("Raj Engine started")

    def stop(self):
        self._running = False
        self._log("Engine stopping...")

    def pause(self):
        self._paused = True
        self._log("PAUSED")

    def resume(self):
        self._paused = False
        self._log("RESUMED")

    def is_running(self): return self._running
    def is_paused(self): return self._paused

    # -- Main Loop --
    def _loop(self):
        while self._running:
            try:
                if not self._paused:
                    self._tick()
            except Exception as e:
                self._log(f"LOOP ERROR: {e}")
            time.sleep(60)

    def _tick(self):
        now = datetime.now()
        self._check_scheduled_sends(now)
        self._process_running_batches(now)
        self._check_auto_start_scheduled_batches(now)
        self._check_bounce_scan(now)
        self._check_reply_scan(now)
        self._check_emergency_commands(now)
        self._check_eod(now)
        self._check_morning_brief(now)

    # -- Batch Processing (NEW) --
    def _process_running_batches(self, now: datetime):
        """Process running batches and send emails at staggered intervals."""
        try:
            running_batches = self.db.execute(
                "SELECT * FROM batches WHERE status='running' ORDER BY created_at"
            ).fetchall()

            if not running_batches:
                return

            # BATCH SLOT LOCK: Only process one batch at a time
            if hasattr(self, '_last_batch_process_time') and self._last_batch_process_time:
                if (now - self._last_batch_process_time).total_seconds() < 2:
                    return
            self._last_batch_process_time = now

            for batch_row in running_batches:
                batch = dict(batch_row)
                batch_id = batch["id"]
                seq_id = batch["sequence_id"]
                stagger = batch.get("stagger_minutes", 0) or 1
                day_offset = batch.get("day_offset", 1)

                # Find next pending recipient
                next_recipient = self.db.execute("""
                    SELECT r.id, r.sequence_id, r.email, r.name, r.org, r.extra_json, r.import_status, r.import_error, r.imported_at, r.batched
                    FROM recipients r
                    JOIN batch_recipients br ON r.id = br.recipient_id
                    WHERE br.batch_id = ? AND br.status = 'pending'
                    ORDER BY r.id
                    LIMIT 1
                """, (batch_id,)).fetchone()

                if not next_recipient:
                    # All sent - mark completed and auto-advance
                    self.db.batch_update_status(batch_id, "completed")
                    self._log(f"[Batch {batch_id}] Completed: all recipients processed")
                    self._auto_advance_batch(batch)
                    continue

                # Check if enough time passed since last send
                last_send = self.db.execute("""
                    SELECT MAX(sent_at) FROM batch_recipients
                    WHERE batch_id = ? AND status = 'sent'
                """, (batch_id,)).fetchone()[0]

                if last_send:
                    last_dt = datetime.fromisoformat(last_send)
                    minutes_since = (now - last_dt).total_seconds() / 60
                    if minutes_since < stagger:
                        continue

                # BLACKLIST CHECK: Skip if email was blacklisted
                rec_email = next_recipient[2]
                if self.db.blacklist_has(rec_email):
                    self._log(f"[Batch {batch_id}] SKIPPING blacklisted: {rec_email}")
                    self.db.execute("""
                        UPDATE batch_recipients SET status='skipped'
                        WHERE batch_id=? AND recipient_id=?
                    """, (batch_id, next_recipient[0]))
                    self.db.commit()
                    continue

                # SUNDAY FILTER: Skip sends on Sunday
                if now.weekday() == 6:
                    self._log(f"[Batch {batch_id}] SUNDAY — skipping send for {rec_email}, will resume Monday")
                    continue

                # DEDUP: Skip if this recipient already received this sequence/day
                already_sent = self.db.execute("""
                    SELECT 1 FROM sends s
                    JOIN recipients r ON s.recipient_id = r.id
                    WHERE r.email = ? AND s.day = ? AND s.status = 'sent'
                    LIMIT 1
                """, (rec_email.lower().strip(), day_offset)).fetchone()
                if already_sent:
                    self._log(f"[DEDUP] {rec_email} already sent Day {day_offset} — marking skipped in batch {batch_id}")
                    self.db.execute("""
                        UPDATE batch_recipients SET status='sent'
                        WHERE batch_id=? AND recipient_id=?
                    """, (batch_id, next_recipient[0]))
                    self.db.commit()
                    continue

                # Send email
                rec = Recipient(*next_recipient)
                subj, body = self.render(seq_id, day_offset, rec)
                if not subj:
                    self._log(f"[Batch {batch_id}] No template for {rec.email} Day {day_offset}, skipping")
                    self.db.execute("UPDATE batch_recipients SET status='failed' WHERE batch_id=? AND recipient_id=?",
                        (batch_id, rec.id))
                    continue

                try:
                    # Determine if draft or immediate send
                    sched_str = batch.get("scheduled_at")
                    use_draft = False
                    if sched_str:
                        try:
                            sched_dt = datetime.fromisoformat(sched_str.replace("Z", "+00:00"))
                            use_draft = sched_dt > now
                        except:
                            pass

                    # Pre-insert sends record to get send_id for tracking
                    placeholder_status = "drafted" if use_draft else "pending"
                    send_id = self.db.campaign_queue_send(rec.id, day_offset, subj, "pending", placeholder_status, batch_id)

                    # Inject tracking pixel and wrapped links with real send_id
                    if self.tracker and self.tracker.base_url and send_id:
                        body = self.tracker.inject_tracking(body, rec.id, batch_id, send_id)

                    if use_draft:
                        draft = self.gmail.create_scheduled_draft(rec.email, subj, body, sched_str)
                        self.db.execute("""
                            UPDATE batch_recipients SET status='drafted', sent_at=?
                            WHERE batch_id=? AND recipient_id=?
                        """, (now.isoformat(), batch_id, rec.id))
                        self.db.execute("UPDATE sends SET draft_id=?, status='drafted' WHERE id=?",
                                        (draft.get("id"), send_id))
                        self.db.commit()
                        self._log(f"[Batch {batch['name']}] Scheduled draft for {rec.email} ({seq_id.upper()} Day {day_offset})")
                    else:
                        # Delete any old scheduled draft before sending for real
                        old_draft = self.db.execute("""
                            SELECT draft_id FROM sends 
                            WHERE recipient_id=? AND batch_id=? AND status='drafted' AND draft_id IS NOT NULL
                            ORDER BY id DESC LIMIT 1
                        """, (rec.id, batch_id)).fetchone()
                        if old_draft and old_draft[0]:
                            try:
                                self.gmail.delete_draft(old_draft[0])
                                self._log(f"[Batch {batch['name']}] Deleted old draft for {rec.email}")
                            except Exception as del_err:
                                self._log(f"[Batch {batch['name']}] Draft delete skipped: {del_err}")

                        msg = self.gmail.send_email(rec.email, subj, body)
                        self.db.execute("""
                            UPDATE batch_recipients SET status='sent', sent_at=?
                            WHERE batch_id=? AND recipient_id=?
                        """, (now.isoformat(), batch_id, rec.id))
                        self.db.execute("UPDATE sends SET draft_id=?, status='sent', sent_at=? WHERE id=?",
                                        (msg.get("id"), now.isoformat(), send_id))
                        self.db.commit()
                        self._log(f"[Batch {batch['name']}] Sent to {rec.email} ({seq_id.upper()} Day {day_offset})")
                except Exception as e:
                    err = str(e).lower()
                    self._log(f"[Batch {batch_id}] Failed to send to {rec.email}: {e}")
                    self.db.execute("UPDATE batch_recipients SET status='failed' WHERE batch_id=? AND recipient_id=?",
                        (batch_id, rec.id))
                    # Permanent failures: blacklist immediately so next day skips them
                    permanent = ["invalid", "not found", "does not exist", "user unknown",
                                 "address rejected", "domain not found", "recipient address"]
                    if any(p in err for p in permanent):
                        self.db.blacklist_add(rec.email, f"send_failed:{err[:80]}")
                        self._log(f"[BLACKLIST] {rec.email} — permanent failure")

        except Exception as e:
            self._log(f"DEBUG ERROR in _process_running_batches: {e}")
            import traceback
            self._log(f"DEBUG TRACEBACK: {traceback.format_exc()}")

    def _auto_advance_batch(self, completed_batch: dict):
        """Auto-create next day batch and schedule it. Like Brevo — next day starts after delay."""
        seq_id = completed_batch["sequence_id"]
        current_day = completed_batch.get("day_offset", 1)
        cfg = SEQUENCES.get(seq_id)
        if not cfg:
            return

        days = cfg["days"]
        try:
            idx = days.index(current_day)
        except ValueError:
            return

        if idx >= len(days) - 1:
            self._log(f"[AUTO-ADVANCE] {seq_id.upper()} sequence complete! All {len(days)} days done.")
            return

        next_day = days[idx + 1]
        parent_name = completed_batch["name"]
        base_name = parent_name.split("-D")[0] if "-D" in parent_name else parent_name
        next_name = f"{base_name}-D{next_day}"

        # DEDUP: Skip if next-day batch already exists
        existing = self.db.execute(
            "SELECT id FROM batches WHERE name=? AND day_offset=? AND sequence_id=?",
            (next_name, next_day, seq_id)
        ).fetchone()
        if existing:
            self._log(f"[AUTO-ADVANCE] Skip: {next_name} already exists (ID: {existing[0]})")
            return

        # Schedule for +2 days at 10 AM (from completion time, not now)
        completed_at = completed_batch.get('completed_at')
        if completed_at:
            try:
                base_dt = datetime.fromisoformat(completed_at)
            except:
                base_dt = datetime.now()
        else:
            base_dt = datetime.now()
        scheduled = (base_dt + timedelta(days=2)).replace(hour=10, minute=0, second=0, microsecond=0)

        # Get parent_batch_id (link to original batch)
        parent_batch_id = completed_batch.get("parent_batch_id") or completed_batch["id"]

        # Get recipients from the completed batch to copy to next batch
        prev_recipients = self.db.batch_get_recipients(completed_batch["id"])

        # FIX: Create batch with status='scheduled' so auto-start picks it up
        new_batch_id = self.db.batch_create(
            next_name, seq_id, scheduled.isoformat(),
            stagger_minutes=completed_batch.get("stagger_minutes", 2),
            day_offset=next_day,
            parent_batch_id=parent_batch_id
        )

        # FIX: Set status to 'scheduled' after creation (batch_create defaults to 'draft')
        self.db.execute("UPDATE batches SET status='scheduled' WHERE id=?", (new_batch_id,))
        self.db.commit()

        # Only carry forward recipients who were successfully sent AND not blacklisted
        carried = 0
        for r in prev_recipients:
            if r.get("batch_status") == "sent":
                # Skip if email was blacklisted after send (bounce, etc.)
                if self.db.blacklist_has(r.get("email", "")):
                    continue
                self.db.batch_add_recipient(new_batch_id, r["id"])
                carried += 1

        self._log(f"[AUTO-ADVANCE] Created {next_name} for {scheduled.strftime('%d %b %H:%M')} ({carried}/{len(prev_recipients)} recipients carried forward)")
        self._log(f"[AUTO-ADVANCE] Pipeline: {base_name} Day {current_day} → Day {next_day} (parent: {parent_batch_id})")

    def _check_auto_start_scheduled_batches(self, now: datetime):
        """Auto-start scheduled batches when their time arrives.
        Includes draft/paused batches that have a scheduled_at date set."""
        scheduled = self.db.execute("""
            SELECT * FROM batches
            WHERE scheduled_at IS NOT NULL AND scheduled_at != ''
              AND status IN ('scheduled', 'draft', 'paused')
        """).fetchall()

        for batch_row in scheduled:
            batch = dict(batch_row)
            sched_str = batch.get("scheduled_at")
            if not sched_str:
                continue
            try:
                sched_dt = datetime.fromisoformat(sched_str)
                if now >= sched_dt:
                    # DEDUP: Don't start if another batch with same name/day/seq is already running
                    dup = self.db.execute("""
                        SELECT id FROM batches
                        WHERE name=? AND day_offset=? AND sequence_id=? AND status='running' AND id != ?
                        LIMIT 1
                    """, (batch["name"], batch.get("day_offset", 1), batch["sequence_id"], batch["id"])).fetchone()
                    if dup:
                        self.db.batch_update_status(batch["id"], "paused")
                        self._log(f"[AUTO-START] Skip '{batch['name']}' — duplicate already running (ID: {dup[0]})")
                        continue
                    self.db.batch_update_status(batch["id"], "running")
                    self._log(f"[AUTO-START] Batch '{batch['name']}' is now running")
            except:
                pass

    # -- Scheduled Sends (10 AM, auto-send sequences) --
    def _check_scheduled_sends(self, now: datetime):
        if now.weekday() == 6:
            return

        if now.hour != 10 or now.minute > 5:
            return
        today = now.strftime("%Y-%m-%d")
        if self.db.get_meta("last_scheduled_send_date") == today:
            return

        self._log(f"Scheduled send check: {today}")
        for seq_id in SEQUENCES:
            if self.db.get_meta(f"pause_{seq_id}") == "true":
                self._log(f"{seq_id.upper()} is paused, skipping")
                continue
            for day in SEQUENCES[seq_id]["days"]:
                due = self.due_recipients(seq_id, day)
                if due:
                    self._log(f"{seq_id.upper()} Day {day}: {len(due)} due. Auto-sending...")
                    result = self.send_batch(seq_id, day)
                    self._log(f"Sent {result.sent}/{result.queued}")
        self.db.set_meta("last_scheduled_send_date", today)

    # -- Import --
    def smart_import(self, filepath: str, sequence_id: str) -> dict:
        """Smart import to POOL only (no batch creation). Leads go to DB first."""
        if not SMART_IMPORT_AVAILABLE:
            return {"success": False, "error": "smart_importer.py not available"}
        try:
            importer = SmartImporter(self.db, self)
            return importer.import_to_pool(filepath, sequence_id)
        except Exception as e:
            self._log(f"Smart import error: {e}")
            return {"success": False, "error": str(e)}

    def import_recipients(self, path: str, sequence_id: str, mapping: dict) -> Tuple[int, int]:
        try:
            import openpyxl
        except ImportError:
            self._log("openpyxl not installed. Run: pip install openpyxl")
            return 0, 0

        wb = openpyxl.load_workbook(path)
        ws = wb.active
        headers = [str(c.value).strip() if c.value else "" for c in ws[1]]
        imported, skipped = 0, 0

        for row in ws.iter_rows(min_row=2, values_only=True):
            row_dict = dict(zip(headers, row))
            email = str(row_dict.get(mapping.get("email", "Email"), "")).strip().lower()
            name = str(row_dict.get(mapping.get("name", "Name"), "")).strip()
            org = str(row_dict.get(mapping.get("org", "Organization"), "")).strip()

            if not email or "@" not in email:
                skipped += 1
                continue
            if self.db.blacklist_has(email):
                skipped += 1
                continue

            extra = {k: v for k, v in row_dict.items() if k not in mapping.values()}
            try:
                self.db.execute("INSERT INTO recipients (sequence_id, email, name, org, extra_json) VALUES (?, ?, ?, ?, ?)",
                    (sequence_id, email, name, org, json.dumps(extra)))
                imported += 1
            except:
                skipped += 1

        self.db.commit()
        self._log(f"Imported {imported} leads, skipped {skipped}")
        return imported, skipped

    def import_blacklist(self, emails: List[str], reason: str = "imported"):
        count = 0
        for email in emails:
            email = email.strip().lower()
            if email and "@" in email:
                self.db.blacklist_add(email, reason)
                count += 1
        self._log(f"Imported {count} blacklisted emails")
        return count

    # -- Templates --
    def sync_templates(self) -> dict:
        self._log("Syncing templates from Gmail...")
        drafts = self.gmail.list_drafts(100)
        loaded = 0
        found_names = []
        skipped = []

        for d in drafts:
            subject = d.get("subject", "")
            found_names.append(subject)
            draft_id = d.get("id", "")

            # FIX: Updated regex to handle [TEMPLATE] prefix and various formats
            # Pattern 1: SCHOOL EMAIL 1, CSR-EMAIL-3, SCHOOL EMAIL 5
            m = re.search(r"(SCHOOL|CSR)[\s\-]*EMAIL[\s\-]*(\d+)", subject, re.IGNORECASE)
            if not m:
                # Pattern 2: [TEMPLATE] SCHOOL Day 1, [TEMPLATE] CSR Day 3
                m = re.search(r"(SCHOOL|CSR).*?Day\s*(\d+)", subject, re.IGNORECASE)
            if not m:
                # Pattern 3: Just SCHOOL 1, CSR 3 anywhere in subject
                m = re.search(r"(SCHOOL|CSR)[\s\-]*(\d+)", subject, re.IGNORECASE)

            if not m:
                skipped.append(f"No match: {subject}")
                continue

            seq = m.group(1).lower()
            num = int(m.group(2))
            day = EMAIL_NUM_TO_DAY.get(num)
            if day is None:
                skipped.append(f"Invalid day num {num}: {subject}")
                continue

            if seq not in SEQUENCES:
                skipped.append(f"Unknown seq {seq}: {subject}")
                continue

            if day not in SEQUENCES[seq]["days"]:
                skipped.append(f"Invalid day {day} for {seq}: {subject}")
                continue

            # RESPECT LOCK STATUS
            if self.is_template_locked(seq, day):
                skipped.append(f"Locked: {seq.upper()} Day {day} - skipping")
                self._log(f"Skipping locked template: {seq.upper()} Day {day}")
                continue

            full = self.gmail.get_draft_full(draft_id)
            if full and full.get("html_body"):
                self.db.template_put(seq, day, full["subject"], full["html_body"])
                loaded += 1
                self._log(f"Loaded: {subject} -> {seq.upper()} Day {day}")
            else:
                skipped.append(f"Failed to fetch body: {subject} (draft_id={draft_id})")
                self._log(f"WARNING: Found matching draft but could not fetch body: {subject}")

        missing = []
        for seq_id, cfg in SEQUENCES.items():
            for day in cfg["days"]:
                if self.db.template_get(seq_id, day) is None:
                    missing.append(f"{seq_id.upper()} Day {day}")

        self._log(f"Sync complete: {loaded} loaded, {len(skipped)} skipped, {len(missing)} missing")
        if skipped:
            for s in skipped[:10]:
                self._log(f"  Skip reason: {s}")

        return {"loaded": loaded, "missing": missing, "found_names": found_names, "skipped": skipped}

    # -- Template Locking System --
    def lock_templates(self) -> dict:
        locked = 0
        for seq_id in SEQUENCES:
            for day in SEQUENCES[seq_id]["days"]:
                tmpl = self.db.template_get(seq_id, day)
                if tmpl:
                    self.db.set_meta(f"locked_{seq_id}_{day}", "true")
                    locked += 1
        self._log(f"Locked {locked} templates. Sync will not overwrite locked templates.")
        return {"locked": locked}

    def unlock_template(self, seq_id: str, day: int):
        self.db.set_meta(f"locked_{seq_id}_{day}", "false")
        self._log(f"Unlocked {seq_id.upper()} Day {day} for updates")

    def lock_template(self, seq_id: str, day: int):
        self.db.set_meta(f"locked_{seq_id}_{day}", "true")
        self._log(f"Locked {seq_id.upper()} Day {day}")

    def is_template_locked(self, seq_id: str, day: int) -> bool:
        return self.db.get_meta(f"locked_{seq_id}_{day}") == "true"

    def create_missing_drafts(self) -> dict:
        created = []
        for seq_id in SEQUENCES:
            for day in SEQUENCES[seq_id]["days"]:
                if self.db.template_get(seq_id, day) is None:
                    tmpl = self.generate_template(seq_id, day)
                    if "error" not in tmpl:
                        self.db.template_put(seq_id, day, tmpl["subject"], tmpl["html_body"])
                        try:
                            draft = self.gmail.draft_email(
                                "om@robopirate.in",
                                f"[TEMPLATE] {tmpl['subject']}",
                                tmpl["html_body"]
                            )
                            created.append(f"{seq_id.upper()} Day {day}")
                            self._log(f"Created draft for {seq_id.upper()} Day {day} — review in Gmail")
                        except Exception as e:
                            self._log(f"DB saved but Gmail draft failed for {seq_id.upper()} Day {day}: {e}")
        return {"created": created, "count": len(created)}

    def get_template_status(self) -> dict:
        status = {}
        for seq_id in SEQUENCES:
            status[seq_id] = {}
            for day in SEQUENCES[seq_id]["days"]:
                tmpl = self.db.template_get(seq_id, day)
                locked = self.is_template_locked(seq_id, day)
                if tmpl:
                    source = self.db.get_meta(f"source_{seq_id}_{day}") or "unknown"
                    status[seq_id][day] = {
                        "exists": True,
                        "locked": locked,
                        "source": source,
                        "subject": tmpl["subject"][:60]
                    }
                else:
                    status[seq_id][day] = {
                        "exists": False,
                        "locked": False,
                        "source": None,
                        "subject": None
                    }
        return status

    def get_templates(self) -> dict:
        out = {}
        for seq_id in SEQUENCES:
            out[seq_id] = {}
            for day in SEQUENCES[seq_id]["days"]:
                t = self.db.template_get(seq_id, day)
                out[seq_id][day] = t
        return out

    # -- Generate Missing Template --
    def generate_template(self, seq_id: str, day: int) -> dict:
        cfg = SEQUENCES.get(seq_id)
        if not cfg:
            return {"error": "Invalid sequence"}

        assets = cfg.get("assets", {}).get(day, {})
        persona = cfg.get("persona", "school")

        content = self._generate_content(seq_id, day, assets)
        subject = self._generate_subject(seq_id, day)

        html = HTML_TEMPLATE.format(body=content)

        return {
            "subject": subject,
            "html_body": html,
            "seq_id": seq_id,
            "day": day,
            "assets_used": list(assets.keys())
        }

    def _generate_subject(self, seq_id: str, day: int) -> str:
        subjects = {
            "school": {
                1: "{{SCHOOL_NAME}} — Transform Your School with Hands-On STEM Labs",
                3: "{{SCHOOL_NAME}} — NEP 2020 Compliance: Is Your School Ready?",
                5: "{{PRINCIPAL_NAME}}, See How {{SCHOOL_NAME}} Can Lead STEM Education",
                7: "{{SCHOOL_NAME}} — Join 85+ Schools Already Using WSL",
                10: "{{PRINCIPAL_NAME}}, Final Call: WSL Subscription Plans for {{SCHOOL_NAME}}"
            },
            "csr": {
                1: "{{COMPANY_NAME}} — CSR Impact: 65,000+ Students Reached",
                3: "{{COMPANY_NAME}} — Schedule VII Alignment + STEM Education",
                5: "{{CSR_HEAD_NAME}}, Sangli Success Story for {{COMPANY_NAME}}",
                7: "{{COMPANY_NAME}} — FY Budget Planning: STEM Investment ROI",
                10: "{{CSR_HEAD_NAME}}, Partner with RoboPirate: Company Profile for {{COMPANY_NAME}}"
            },
            "csr-wsl-5": {
                1: "{{COMPANY_NAME}} — A 5-Year STEM Lab Where You Fund Only Year 1",
                3: "{{CSR_HEAD_NAME}}, We Already Did This — First WE Smart Lab, Full Academic Year, Government School",
                5: "{{CSR_HEAD_NAME}}, The Job Your CSR Creates — 1 Trainer, 5 Years, Trained from Underprivileged Background",
                7: "{{COMPANY_NAME}} — The Math: Rs.12L CSR + Rs.28L Government = 400 Students x 5 Years",
                10: "{{CSR_HEAD_NAME}}, Final Call — FY 2026-27 Budget Window + 90-Day Launch Plan"
            }
        }
        return subjects.get(seq_id, {}).get(day, f"RoboPirate {seq_id.upper()} - Day {day}")

    def _generate_content(self, seq_id: str, day: int, assets: dict) -> str:
        if seq_id == "school":
            return self._generate_school_content(day, assets)
        elif seq_id in ("csr", "csr-wsl-5"):
            return self._generate_csr_content(day, assets)
        else:
            return self._generate_csr_content(day, assets)

    def _generate_school_content(self, day: int, assets: dict) -> str:
        contents = {
            1: """
<p>Dear Principal,</p>
<p>Imagine your students building robots, coding drones, and exploring AI — all within your school walls. For the 2026-27 academic year, this is no longer optional.</p>
<p><strong>WE Smart Lab</strong> by RoboPirate brings cutting-edge STEAM/AI education to Indian schools. We're already in <strong>85+ labs</strong> across <strong>6 states</strong>, impacting <strong>65,000+ students</strong>.</p>
<p>Everything is included — lab setup, 120+ DIY kits, full-time trained teacher, NEP 2020 aligned curriculum, LMS portal, and ongoing support. Schools simply open the door; we handle the rest.</p>
<p>Would you be open to a 15-minute call to discuss how WSL can transform your school?</p>
<p>Best regards,<br><strong>RoboPirate Team</strong><br>WSL Initiative</p>
""",

            3: """
<p>Dear Principal,</p>
<p>With NEP 2020 now in full implementation and the 2026-27 academic year approaching, schools across India are racing to comply with experiential learning and coding mandates from Class 6.</p>
<p><strong>The question is:</strong> Will your school lead this change or play catch-up?</p>
<p>WSL provides:</p>
<ul>
<li>Ready-to-deploy STEM labs</li>
<li>NEP-aligned curriculum</li>
<li>Teacher training programs</li>
<li>Progress tracking dashboards</li>
</ul>
<p>Let's discuss how your school can be NEP-ready this academic year.</p>
<p>Best regards,<br><strong>RoboPirate Team</strong><br>WSL Initiative</p>
""",

            5: """
<p>Dear Principal,</p>
<p>Let me share a story that might resonate with you.</p>
<p><strong>Veer Baji Prabhu Vidyalay</strong> — a school much like yours — partnered with us in 2024-25 through our WE Smart Lab program. Today, their students have built 12+ working robots, participated in state-level competitions, and seen measurable improvement in science engagement.</p>
<p>Your school could be our next success story.</p>
<p>Best regards,<br><strong>RoboPirate Team</strong><br>WSL Initiative</p>
""",

            7: """
<p>Dear Principal,</p>
<p>You're not alone in this journey. <strong>85+ schools</strong> across Maharashtra, Karnataka, Gujarat, and more have already chosen WSL.</p>
<p>Ready to join them?</p>
<p>Best regards,<br><strong>RoboPirate Team</strong><br>WSL Initiative</p>
""",

            10: """
<p>Dear Principal,</p>
<p>This is my final email for the 2026-27 academic year planning. With admissions season approaching, I don't want your students to miss this opportunity.</p>
<p>We've prepared flexible WE Smart Lab subscription plans for schools of all sizes. Every plan includes: complete lab setup, 120+ DIY kits, full-time trained teacher, NEP 2020 + NCF aligned curriculum, LMS portal, assessments, and ongoing support.</p>
<p>If now isn't the right time, I understand. But if you're even slightly curious, let's have a 10-minute conversation. No obligation.</p>
<p>Best regards,<br><strong>RoboPirate Team</strong><br>WSL Initiative</p>
"""
        }
        return contents.get(day, f"<p>Template content for Day {day}</p>")

    def _generate_csr_content(self, day: int, assets: dict) -> str:
        contents = {
            1: """
<p>Dear CSR Head,</p>
<p>Your CSR budget has the power to change <strong>thousands</strong> of young lives.</p>
<p>RoboPirate's <strong>WE Smart Lab</strong> sets up fully managed STEAM/AI Smart Labs inside schools across India. As of May 2026, we've reached <strong>65,000+ students</strong> across <strong>6 states</strong> with <strong>85+ labs</strong> delivered through strategic CSR partnerships.</p>
<p>Would you be open to exploring how your CSR mandate can create measurable STEM impact?</p>
<p>Best regards,<br><strong>RoboPirate CSR Team</strong></p>
""",

            3: """
<p>Dear CSR Head,</p>
<p>Schedule VII of the Companies Act explicitly supports:</p>
<ul>
<li>Education (item ii)</li>
<li>Skill development (item x)</li>
<li>Rural development (item xii)</li>
</ul>
<p>WSL aligns perfectly with all three.</p>
<p>Best regards,<br><strong>RoboPirate CSR Team</strong></p>
""",

            5: """
<p>Dear CSR Head,</p>
<p>Numbers tell stories better than words.</p>
<p><strong>Sangli District Phase 2 Results — WE Smart Lab Impact (Delivered 2025-26):</strong></p>
<ul>
<li>15 schools equipped with fully managed STEAM/AI labs</li>
<li>4,500+ students trained in robotics, coding, AI & IoT</li>
<li>87% teacher satisfaction rate</li>
<li>3 students won state-level competitions</li>
<li>1.5L+ student projects completed across all programs</li>
</ul>
<p>This could be your company's legacy.</p>
<p>Best regards,<br><strong>RoboPirate CSR Team</strong></p>
""",

            7: """
<p>Dear CSR Head,</p>
<p>FY 2026-27 budget season is here — May 2026 is when CSR allocations are locked. Where will your CSR rupees create the most impact?</p>
<p>Consider the WE Smart Lab model:</p>
<ul>
<li>Setup cost: Rs.2.5L – 8L per school (one-time, based on tier)</li>
<li>Annual program cost: Rs.7L per school (CSR School Model)</li>
<li>Cost per student impacted: Under Rs.500/year</li>
<li>Tax benefits: 100% deductible under Companies Act 2013 Schedule VII</li>
<li>Full compliance documentation + quarterly impact reports included</li>
</ul>
<p>Let's discuss a pilot program for Q1.</p>
<p>Best regards,<br><strong>RoboPirate CSR Team</strong></p>
""",

            10: """
<p>Dear CSR Head,</p>
<p>This is my final outreach for FY 2026-27 planning. With budgets being locked in May 2026, I respect your time and decision.</p>
<p>If you've been considering STEM education as part of your CSR strategy, let's not let another quarter pass.</p>
<p>I'm available for a 20-minute presentation at your office or via video call. No pitch, just facts and possibilities.</p>
<p>Best regards,<br><strong>RoboPirate CSR Team</strong></p>
"""
        }
        return contents.get(day, f"<p>Template content for Day {day}</p>")

    def save_generated_template(self, seq_id: str, day: int) -> bool:
        template = self.generate_template(seq_id, day)
        if "error" in template:
            self._log(f"Failed to generate {seq_id.upper()} Day {day}: {template['error']}")
            return False

        self.db.template_put(seq_id, day, template["subject"], template["html_body"], "generated")

        try:
            draft = self.gmail.draft_email(
                "om@robopirate.in",
                f"[TEMPLATE] {template['subject']}",
                template["html_body"]
            )
            self._log(f"Generated {seq_id.upper()} Day {day} template + Gmail draft created")
            return True
        except Exception as e:
            self._log(f"Saved to DB but Gmail draft failed: {e}")
            return True

    # -- Due Recipients --
    def due_recipients(self, sequence_id: str, day: int, limit=None) -> List[Recipient]:
        cfg = SEQUENCES.get(sequence_id)
        if not cfg or day not in cfg["days"]: return []

        idx = cfg["days"].index(day)
        if idx == 0:
            sql = """SELECT r.* FROM recipients r WHERE r.sequence_id=?
                AND NOT EXISTS (SELECT 1 FROM sends s WHERE s.recipient_id=r.id)
                AND NOT EXISTS (SELECT 1 FROM blacklist b WHERE b.email=r.email)
                ORDER BY r.id"""
            params = (sequence_id,)
        else:
            prev = cfg["days"][idx - 1]
            gap = day - prev
            cutoff = (datetime.now() - timedelta(days=gap)).isoformat()
            sql = """SELECT r.* FROM recipients r
                JOIN sends s ON s.recipient_id=r.id AND s.day=? AND s.status IN ('sent','drafted')
                WHERE r.sequence_id=? AND s.created_at<=?
                AND NOT EXISTS (SELECT 1 FROM sends s2 WHERE s2.recipient_id=r.id AND s2.day=?)
                AND NOT EXISTS (SELECT 1 FROM blacklist b WHERE b.email=r.email)
                AND NOT EXISTS (SELECT 1 FROM sends s3 WHERE s3.recipient_id=r.id AND s3.status='replied')
                ORDER BY s.created_at"""
            params = (prev, sequence_id, cutoff, day)

        rows = self.db.execute(sql, params).fetchall()
        return [Recipient(*r) for r in rows][:limit] if limit else [Recipient(*r) for r in rows]

    # -- Render --
    def render(self, seq_id: str, day: int, rec: Recipient) -> Tuple[Optional[str], Optional[str]]:
        tmpl = self.db.template_get(seq_id, day)
        if not tmpl: return None, None

        subj, body = tmpl["subject"] or "", tmpl["html_body"] or ""
        extra = json.loads(rec.extra_json or "{}")

        placeholders = {
            "{{PRINCIPAL_NAME}}": rec.name, "{{SCHOOL_NAME}}": rec.org,
            "{{CSR_HEAD_NAME}}": rec.name, "{{COMPANY_NAME}}": rec.org,
            "{{OPENING_LINE}}": extra.get("Opening Line", extra.get("opening_line", "")),
            "{{NAME}}": rec.name, "{{ORG}}": rec.org, "{{EMAIL}}": rec.email,
        }
        for ph, val in placeholders.items():
            subj = subj.replace(ph, str(val))
            body = body.replace(ph, str(val))
        return subj, body

    # -- Send Batch (AUTO-SEND for sequences) --
    def send_batch(self, seq_id: str, day: int, limit=None, dry_run=False) -> BatchResult:
        due = self.due_recipients(seq_id, day, limit)
        if not due: return BatchResult(queued=0, sent=0)
        if dry_run: return BatchResult(queued=len(due), sent=0)

        sent = 0
        for i, rec in enumerate(due):
            subj, body = self.render(seq_id, day, rec)
            if not subj:
                self._log(f"No template for {rec.email}, skipping")
                continue
            try:
                # Inject tracking
                send_id = self.db.campaign_queue_send(rec.id, day, subj, "pending", "pending")
                if self.tracker and self.tracker.base_url and send_id:
                    body = self.tracker.inject_tracking(body, rec.id, None, send_id)
                msg = self.gmail.send_email(rec.email, subj, body)
                self.db.execute("UPDATE sends SET draft_id=?, status='sent' WHERE id=?",
                                (msg.get("id"), send_id))
                self.db.commit()
                sent += 1
                self._log(f"Sent to {rec.email}")
                time.sleep(SEND_DELAY)
            except Exception as e:
                err = str(e)
                if "quota" in err.lower() or "rate" in err.lower() or "limit" in err.lower():
                    self._log("Rate limit hit. Saving remaining to pending_resumes...")
                    for r in due[i:]:
                        rs, rb = self.render(seq_id, day, r)
                        self.db.execute(
                            "INSERT INTO pending_resumes (sequence_id, day, recipient_id, subject, status, error) VALUES (?, ?, ?, ?, ?, ?)",
                            (seq_id, day, r.id, rs or subj, "pending", err[:200])
                        )
                    self.db.commit()
                    remaining = len(due) - i
                    self._log(f"Saved {remaining} emails to pending_resumes. Type 'resume batch {seq_id} day {day}' to continue.")
                    return BatchResult(queued=len(due), sent=sent, error="quota_hit")
                self._log(f"Failed: {rec.email} -- {e}")
        return BatchResult(queued=len(due), sent=sent)

    # -- Test Send --
    def test_send(self, email: str, seq_id: str, day: int) -> bool:
        tmpl = self.db.template_get(seq_id, day)
        if not tmpl:
            self._log("No template found")
            return False
        try:
            self.gmail.send_email(email, f"[TEST] {tmpl['subject']}", tmpl["html_body"])
            self._log(f"Test sent to {email}")
            return True
        except Exception as e:
            self._log(f"Test failed: {e}")
            return False

    # -- Summary --
    def get_summary(self) -> dict:
        return self.db.get_dashboard_summary()

    def get_catch_up(self) -> List[dict]:
        catch = []
        for seq_id in SEQUENCES:
            for day in SEQUENCES[seq_id]["days"]:
                due = self.due_recipients(seq_id, day)
                if due:
                    overdue = 0
                    if day != 1:
                        prev = SEQUENCES[seq_id]["days"][SEQUENCES[seq_id]["days"].index(day) - 1]
                        oldest = self.db.execute("SELECT MIN(created_at) FROM sends s JOIN recipients r ON r.id=s.recipient_id WHERE r.sequence_id=? AND s.day=?", (seq_id, prev)).fetchone()[0]
                        if oldest:
                            expected = datetime.fromisoformat(oldest) + timedelta(days=(day - prev))
                            overdue = max(0, (datetime.now() - expected).days)
                    catch.append({"sequence": seq_id, "day": day, "count": len(due), "overdue_by_days": overdue})
        return catch

    # -- Batch Pipeline --
    def get_batch_pipeline(self, batch_id: int) -> dict:
        return self.db.batch_get_pipeline(batch_id)

    def get_all_batch_pipelines(self, sequence_id: str = None) -> list:
        return self.db.batch_get_all_pipelines(sequence_id)

    # -- POOL METHODS (NEW) --
    def get_pool(self, sequence_id: str, limit: int = None) -> list:
        return self.db.get_pool(sequence_id, limit)

    def get_pool_count(self, sequence_id: str) -> int:
        return self.db.get_pool_count(sequence_id)

    def create_batch_from_pool(self, name: str, sequence_id: str, batch_size: int,
                                day_offset: int = 1, scheduled_at: str = None,
                                timezone: str = 'Asia/Kolkata', send_rate: int = 0,
                                stagger_minutes: int = 2) -> dict:
        pool_count = self.get_pool_count(sequence_id)
        if pool_count == 0:
            return {"success": False, "error": f"No unbatched leads in {sequence_id.upper()} pool"}

        batch_id, error = self.db.batch_from_pool(
            name=name,
            sequence_id=sequence_id,
            batch_size=batch_size,
            day_offset=day_offset,
            scheduled_at=scheduled_at,
            timezone=timezone,
            send_rate=send_rate,
            stagger_minutes=stagger_minutes
        )

        if error:
            return {"success": False, "error": error}

        batch = self.db.batch_get(batch_id)
        actual_size = self.db.batch_count_recipients(batch_id)
        self._log(f"[POOL] Created batch '{name}' with {actual_size}/{batch_size} leads from {sequence_id.upper()} pool ({pool_count} available)")
        return {
            "success": True,
            "batch_id": batch_id,
            "name": name,
            "sequence_id": sequence_id,
            "size": actual_size,
            "requested_size": batch_size,
            "pool_remaining": pool_count - actual_size,
            "day_offset": day_offset,
            "scheduled_at": scheduled_at
        }

    # -- Blacklist --
    def blacklist_add(self, email: str, reason: str = "manual"):
        self.db.blacklist_add(email, reason)
        self._log(f"Blacklisted: {email}")

    def blacklist_remove(self, email: str):
        self.db.blacklist_remove(email)
        self._log(f"Removed from blacklist: {email}")

    # -- Bounce Scan --
    def _check_bounce_scan(self, now: datetime):
        last = self.db.get_meta("last_bounce_scan")
        if last and (now - datetime.fromisoformat(last)) < timedelta(hours=BOUNCE_INTERVAL): return
        self.scan_bounces(days_back=15)

    def scan_bounces(self, days_back: int = 1) -> dict:
        """Scan for bounces and auto-replies. Deletes processed emails from Gmail."""
        last = self.db.get_meta("last_bounce_scan")
        if last:
            last_dt = datetime.fromisoformat(last)
            scan_since = max(last_dt, datetime.now() - timedelta(days=days_back))
        else:
            scan_since = datetime.now() - timedelta(days=days_back)

        after_str = scan_since.strftime("%Y/%m/%d")

        queries = [
            f"after:{after_str} (from:mailer-daemon OR from:postmaster OR from:Mail Delivery Subsystem OR from:MAILER-DAEMON)",
            f"after:{after_str} (subject:undelivered OR subject:bounce OR subject:'delivery status' OR subject:'delivery failure' OR subject:'failed delivery' OR subject:'address not found' OR subject:'recipient not found' OR subject:'Mail delivery failed' OR subject:'Returned mail')",
            f"after:{after_str} (subject:out of office OR subject:vacation OR subject:'auto reply' OR subject:'automated response' OR subject:'automatic reply' OR subject:'away from office')",
        ]

        all_msgs = []
        seen_ids = set()

        for q in queries:
            try:
                msgs = self.gmail.search_messages(q, 100)
                for m in msgs:
                    if m['id'] not in seen_ids:
                        seen_ids.add(m['id'])
                        all_msgs.append(m)
            except Exception as e:
                self._log(f"Bounce query failed: {e}")

        self._log(f"Bounce scan: {len(all_msgs)} messages to check")

        new_blacklisted = 0
        auto_reply_count = 0
        protected_count = 0
        deleted_count = 0
        skipped = 0
        processed_this_scan = set()

        for msg in all_msgs:
            subject = msg.get("subject", "").lower()
            body = msg.get("body", "") or ""
            from_addr = msg.get("from", "").lower()
            snippet = msg.get("snippet", "") or ""
            msg_id = msg["id"]

            if "robopirate" in from_addr and "mailer-daemon" not in from_addr:
                continue

            is_bounce = self._looks_like_bounce(from_addr, subject, body)
            is_auto_reply = self._is_auto_reply(subject, body)

            if is_auto_reply and not is_bounce:
                auto_reply_count += 1
                self._log(f"[AUTO-REPLY] {from_addr[:40]}: {subject[:50]}")
                self._delete_bounce_email(msg_id)
                continue

            if not is_bounce:
                self._delete_bounce_email(msg_id)
                continue

            addrs = self._extract_bounced(body) or []

            try:
                full = self.gmail.get_message_full(msg_id)
                if full:
                    full_addrs = self._extract_bounced(full.get("body", "") or "")
                    for a in full_addrs:
                        if a not in addrs:
                            addrs.append(a)
            except:
                pass

            snippet_addrs = self._extract_bounced(snippet)
            for a in snippet_addrs:
                if a not in addrs:
                    addrs.append(a)

            if not addrs:
                self._log(f"[BOUNCE] No address extracted: {subject[:60]}")
                self._delete_bounce_email(msg_id)
                continue

            for addr in addrs:
                addr = addr.lower().strip()

                if not addr or "@" not in addr:
                    continue
                if addr.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".css", ".js")):
                    continue
                if "/" in addr or "?" in addr or "&" in addr:
                    continue
                if addr.startswith(("wght@", "size@", "color@", "font@")):
                    continue
                if self.is_protected_email(addr):
                    protected_count += 1
                    continue
                if self.db.blacklist_has(addr):
                    if addr not in processed_this_scan:
                        skipped += 1
                        processed_this_scan.add(addr)
                    continue
                if addr in processed_this_scan:
                    continue

                processed_this_scan.add(addr)

                # ── Layer 1: Verify email is in our recipient pool ──
                if not self.db.recipient_exists(addr):
                    self._log(f"[BOUNCE-SKIP] {addr} — not in recipient pool")
                    continue

                # ── Layer 2: Verify we actually sent to them ──
                if not self.db.was_sent_to(addr):
                    self._log(f"[BOUNCE-SKIP] {addr} — no send record")
                    continue

                # ── Layer 3: Classify hard vs soft bounce ──
                bounce_type, reason = self._classify_bounce(body)
                if bounce_type == "soft":
                    self._log(f"[BOUNCE-SOFT] {addr} — {reason}")
                    continue

                # ── All checks passed — blacklist with reason ──
                self.db.blacklist_add(addr, f"bounce: {reason}")
                new_blacklisted += 1
                self._log(f"[BLACKLIST] {addr} — {reason}")

            self._delete_bounce_email(msg_id)
            deleted_count += 1

        self.db.set_meta("last_bounce_scan", datetime.now().isoformat())
        self._log(f"Bounce scan: {new_blacklisted} new blacklisted, {auto_reply_count} auto-replies, {protected_count} protected, {deleted_count} deleted, {skipped} already blacklisted")
        return {
            "new_blacklisted": new_blacklisted,
            "auto_replies": auto_reply_count,
            "protected": protected_count,
            "deleted": deleted_count,
            "skipped": skipped
        }

    def _delete_bounce_email(self, msg_id: str):
        """Delete a bounce email from Gmail."""
        try:
            self.gmail.trash_message(msg_id)
        except Exception as e:
            try:
                self.gmail.delete_message(msg_id)
            except:
                self._log(f"Could not delete bounce email {msg_id}: {e}")

    def deep_bounce_scan(self, days: int = 30) -> dict:
        """Deep scan inbox for bounce emails over last N days."""
        results = {'found': 0, 'blacklisted': 0, 'protected': 0, 'details': []}
        try:
            after_date = (datetime.now() - timedelta(days=days)).strftime("%Y/%m/%d")
            query = f"after:{after_date} (from:mailer-daemon OR from:postmaster OR 'delivery status notification' OR 'undeliverable' OR 'message not delivered')"
            messages = self.gmail.search_messages(query, max_results=200)
            if not messages:
                self._log(f"[DEEP BOUNCE SCAN] No bounce emails found in last {days} days")
                return results

            self._log(f"[DEEP BOUNCE SCAN] Checking {len(messages)} potential bounce emails (last {days} days)...")

            sent_rows = self.db.execute("SELECT DISTINCT email FROM recipients").fetchall()
            our_emails = {r[0].lower().strip() for r in sent_rows}

            for msg in messages:
                try:
                    from_addr = msg.get('from', '').lower()
                    subject = msg.get('subject', '').lower()
                    body = msg.get('body', '').lower()

                    is_mailer = any(x in from_addr for x in ['mailer-daemon', 'postmaster', 'mail delivery subsystem'])
                    is_bounce_subject = any(x in subject for x in [
                        'delivery status notification', 'undeliverable', 'permanent failure',
                        'message not delivered', 'failure notice', 'returned mail'
                    ])
                    if not (is_mailer or is_bounce_subject):
                        continue

                    results['found'] += 1

                    bounced_email = None
                    patterns = [
                        r'final-recipient:\s*rfc822;\s*([^\s<>]+)',
                        r'original-recipient:\s*rfc822;\s*([^\s<>]+)',
                        r'to:\s*([^\s<>]+@[^\s<>]+)',
                        r'does not exist[:\s]+([^\s<>]+@[^\s<>]+)',
                    ]
                    for pat in patterns:
                        m = re.search(pat, body)
                        if m:
                            bounced_email = m.group(1).strip()
                            break

                    if not bounced_email:
                        emails_in_body = re.findall(r'[\w.-]+@[\w.-]+\.\w+', body)
                        for e in emails_in_body:
                            if e.lower() in our_emails:
                                bounced_email = e
                                break

                    if not bounced_email:
                        continue

                    bounced_email = bounced_email.lower().strip()
                    bounced_email = re.sub(r"[.,;:!?)\'\"]+$", "", bounced_email)

                    if not re.match(r'^[\w.-]+@[\w.-]+\.\w+$', bounced_email):
                        continue
                    if self.db.blacklist_has(bounced_email):
                        continue
                    if self.is_protected_email(bounced_email):
                        results['protected'] += 1
                        continue
                    if bounced_email not in our_emails:
                        continue

                    # Layer 2: Verify we actually sent to them
                    if not self.db.was_sent_to(bounced_email):
                        continue

                    # Layer 3: Classify hard vs soft
                    bounce_type, reason = self._classify_bounce(body)
                    if bounce_type == "soft":
                        results['details'].append({'email': bounced_email, 'action': 'SKIPPED (soft bounce)'})
                        continue

                    self.db.blacklist_add(bounced_email, f"bounce: {reason} (deep scan {days}d)")
                    results['blacklisted'] += 1
                    results['details'].append({'email': bounced_email, 'action': 'BLACKLISTED'})
                    self.gmail.trash_message(msg['id'])

                except Exception as e:
                    continue

            self._log(f"[DEEP BOUNCE SCAN] Complete: {results['found']} found, {results['blacklisted']} blacklisted, {results['protected']} protected")
            return results

        except Exception as e:
            self._log(f"[Engine] Deep bounce scan error: {e}")
            return results

    @staticmethod
    def is_protected_email(email: str) -> bool:
        """Check if an email is protected from blacklisting."""
        if not email:
            return False
        email = email.lower().strip()
        return email.endswith("@robopirate.in") or email == "itsomkarsinghhh@gmail.com"

    def _classify_bounce(self, body: str) -> tuple:
        """Classify bounce as hard (permanent) or soft (temporary).
        Returns (type, reason) where type is 'hard' or 'soft'.
        """
        if not body:
            return "hard", "unknown"
        body_lower = body.lower()

        # Check SMTP status codes first (most reliable)
        for m in re.finditer(r'status:\s*(\d\.\d\.\d)|(\d{3})', body_lower):
            code = m.group(1) or m.group(2)
            if code and (code.startswith('5') or code.startswith('2.')):
                return "hard", f"SMTP {code}"
            if code and (code.startswith('4') or code.startswith('1.')):
                return "soft", f"SMTP {code}"

        # Hard bounce keywords (permanent failures)
        hard_keywords = [
            "user unknown", "no such user", "address does not exist",
            "invalid address", "domain not found", "mailbox unavailable",
            "recipient address rejected", "permanent failure", "does not exist",
            "unable to deliver", "delivery permanently", "not a valid",
            "host unknown", "unrouteable address", "relay access denied"
        ]
        for kw in hard_keywords:
            if kw in body_lower:
                return "hard", kw

        # Soft bounce keywords (temporary failures)
        soft_keywords = [
            "mailbox full", "quota exceeded", "temporary failure",
            "try again later", "server busy", "defer", "delayed",
            "greylisted", "temporarily rejected", "soft bounce",
            "resource temporarily unavailable"
        ]
        for kw in soft_keywords:
            if kw in body_lower:
                return "soft", kw

        # Default: treat unknown as hard (better safe than sorry for bounces)
        return "hard", "unknown"

    def _looks_like_bounce(self, from_addr: str, subject: str, body: str) -> bool:
        """Quick heuristic check if an email looks like a bounce or auto-reply."""
        from_lower = from_addr.lower()
        subj_lower = subject.lower()
        body_lower = body.lower()

        bounce_senders = [
            "mailer-daemon", "postmaster", "mail delivery subsystem",
            "daemon", "bounce", "undeliverable", "noreply"
        ]
        for sender in bounce_senders:
            if sender in from_lower:
                return True

        bounce_subjects = [
            "undelivered", "bounce", "delivery status", "delivery failure",
            "failed delivery", "address not found", "recipient not found",
            "returned mail", "mail delivery failed", "message not delivered"
        ]
        for pattern in bounce_subjects:
            if pattern in subj_lower:
                return True

        auto_subjects = [
            "out of office", "auto reply", "automated response", "automatic reply",
            "vacation", "on leave", "away from office", "abwesenheitsnotiz"
        ]
        for pattern in auto_subjects:
            if pattern in subj_lower:
                return True

        body_bounce_patterns = [
            "final-recipient", "diagnostic-code", "action: failed",
            "status:", "remote server", "smtp error", "550 ", "551 ",
            "552 ", "553 ", "554 ", "recipient address rejected",
            "user unknown", "no such user", "mailbox unavailable"
        ]
        for pattern in body_bounce_patterns:
            if pattern in body_lower:
                return True

        auto_body_patterns = [
            "auto-submitted:", "x-autoreply:", "precedence: auto_reply",
            "x-auto-response-suppress:", "i am currently out of",
            "i will be out of", "i am away", "on vacation until",
            "return on", "back on", "this is an automated"
        ]
        for pattern in auto_body_patterns:
            if pattern in body_lower:
                return True

        return False

    @staticmethod
    def _is_auto_reply(subject: str, body: str) -> bool:
        """Detect if message is an auto-reply/out-of-office/vacation response."""
        subject_lower = subject.lower()
        body_lower = body.lower()

        auto_reply_keywords = [
            "out of office", "out of the office", "away from office", "on vacation",
            "on leave", "auto reply", "automated response", "automatic reply",
            "automatic response", "auto-response", "out of office reply",
            "abwesenheitsnotiz", "risposta automatica", "respuesta automatica",
            "reponse automatique", "automatikus valasz", "automatski odgovor",
            "automatisch antwoord", "automaattinen vastaus", "automatsvar",
            "i am currently out of", "i will be out of", "i am away",
            "not in office", "not available", "currently unavailable",
            "thank you for your email", "we have received your email",
            "this is an automated", "this email is automatically",
            "do not reply to this", "noreply", "no reply",
            "i am on holiday", "i am on vacation", "annual leave",
            "maternity leave", "paternity leave", "sick leave",
            "traveling until", "back on", "return on", "will return",
            "limited access to email", "intermittent access",
            "email access limited", "delayed response"
        ]

        for keyword in auto_reply_keywords:
            if keyword in subject_lower or keyword in body_lower:
                return True

        header_patterns = [
            "auto-submitted:", "x-autoreply:", "x-auto-response-suppress:",
            "precedence: auto_reply", "precedence: bulk",
            "x-mailer: autoreply", "x-autoresponder:",
            "vacation:", "x-vacation:", "autoreply:"
        ]
        for pattern in header_patterns:
            if pattern in body_lower:
                return True

        return False

    def _extract_original_sender(self, subject: str, body: str, msg_or_full: dict = None) -> Optional[str]:
        """Extract the original sender email from an auto-reply or bounce message."""
        patterns = [
            r"Original-From:\s*<?([\w.+-]+@[\w.-]+)>?",
            r"From:\s*<?([\w.+-]+@[\w.-]+)>?",
            r"Sender:\s*<?([\w.+-]+@[\w.-]+)>?",
            r"Reply-To:\s*<?([\w.+-]+@[\w.-]+)>?",
            r"was sent by\s+([\w.+-]+@[\w.-]+)",
            r"sent by\s+([\w.+-]+@[\w.-]+)",
            r"original message was sent by\s+([\w.+-]+@[\w.-]+)",
            r"your message to\s+([\w.+-]+@[\w.-]+)",
            r"email sent to\s+([\w.+-]+@[\w.-]+)",
            r"message to\s+([\w.+-]+@[\w.-]+)\s+was",
        ]

        texts = [body]
        if msg_or_full:
            texts.append(msg_or_full.get("body", ""))
            texts.append(msg_or_full.get("snippet", ""))

        for text in texts:
            if not text:
                continue
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    email = match.group(1).strip().strip("<>").lower()
                    if "@" in email and "mailer-daemon" not in email and "postmaster" not in email:
                        return email
            to_match = re.search(r"To:\s*<?([\w.+-]+@[\w.-]+)>?", text, re.IGNORECASE)
            if to_match:
                email = to_match.group(1).strip().strip("<>").lower()
                if "@" in email and "mailer-daemon" not in email and "postmaster" not in email:
                    return email

        return None

    @staticmethod
    def _extract_bounced(text: str) -> List[str]:
        if not text:
            return []
        addrs = []

        patterns = [
            r"Final-Recipient:\s*rfc822;\s*([\w.+-]+@[\w.-]+)",
            r"Original-Recipient:\s*rfc822;\s*([\w.+-]+@[\w.-]+)",
            r"To:\s*<([\w.+-]+@[\w.-]+)>",
            r"Your message to\s+([\w.+-]+@[\w.-]+)\s+couldn'?t be delivered",
            r"message to\s+([\w.+-]+@[\w.-]+)\s+was undeliverable",
            r"(?:was not delivered to|wasn'?t delivered to|could not be delivered to|couldn't be delivered to|failed to deliver to)\s+([\w.+-]+@[\w.-]+)",
            r"Address not found.*?(?:to|for)\s+([\w.+-]+@[\w.-]+)",
            r"^\s*<([\w.+-]+@[\w.-]+)>:?\s*$",
            r"([\w.+-]+@[\w.-]+):\s*(?:user unknown|mailbox unavailable|no such user|does not exist|mailbox full|invalid user|unknown local-part)",
            r"did not reach.*?([\w.+-]+@[\w.-]+)",
            r"address(?:es)? failed.*?([\w.+-]+@[\w.-]+)",
        ]

        for pat in patterns:
            for m in re.finditer(pat, text, re.I | re.M | re.DOTALL):
                email = m.group(1).strip().strip("<>").lower()
                if "@" in email and "mailer-daemon" not in email and "postmaster" not in email:
                    if email not in addrs:
                        addrs.append(email)

        if not addrs:
            for m in re.finditer(r"<([\w.+-]+@[\w.-]+)>", text):
                email = m.group(1).strip().lower()
                if "mailer-daemon" not in email and "postmaster" not in email:
                    if email not in addrs:
                        addrs.append(email)

        if not addrs and any(k in text.lower() for k in ["delivery", "bounce", "failed", "undelivered", "address not found", "recipient", "mailer-daemon", "postmaster"]):
            for m in re.finditer(r"[\w.+-]+@[\w.-]+", text):
                email = m.group().lower()
                if any(x in email for x in ["mailer-daemon", "postmaster", "robopirate.in", "google.com", "gmail.com", "instagram", "facebook", "twitter", "linkedin", "youtube", "2x", "3x", "1x", "wght", "size", "color", "font"]):
                    continue
                if "@" in email:
                    domain = email.split("@")[1]
                    if "." not in domain or len(domain) < 4:
                        continue
                if email not in addrs:
                    addrs.append(email)

        return addrs

    def _check_reply_scan(self, now: datetime):
        last = self.db.get_meta("last_reply_scan")
        if last and (now - datetime.fromisoformat(last)) < timedelta(minutes=REPLY_INTERVAL): return
        self.scan_replies()

    def scan_replies(self, days_back: int = 3) -> int:
        """Scan inbox for replies from recipients."""
        after = int((datetime.now() - timedelta(days=days_back)).timestamp())

        msgs_all = self.gmail.search_messages(f"in:inbox after:{after}", 200)
        msgs_sent = self.gmail.search_messages(f"in:sent after:{after}", 100)
        msgs_re = self.gmail.search_messages(f"in:inbox subject:Re: after:{after}", 100)

        seen_ids = set()
        all_msgs = []
        for m in msgs_all + msgs_sent + msgs_re:
            if m['id'] not in seen_ids:
                seen_ids.add(m['id'])
                all_msgs.append(m)

        self._log(f"DEBUG REPLY SCAN: {len(all_msgs)} unique messages to check")

        new_count = 0
        checked_count = 0

        for msg in all_msgs:
            from_addr = msg.get("from", "").lower()
            subject = msg.get("subject", "").lower()
            body = msg.get("body", "") or ""

            if "robopirate" in from_addr:
                continue

            if self._is_auto_reply(subject, body):
                continue
            if "mailer-daemon" in from_addr or "postmaster" in from_addr:
                continue

            checked_count += 1

            rows = self.db.execute("""SELECT r.id, s.id as send_id, s.draft_id, s.day
                FROM recipients r JOIN sends s ON s.recipient_id=r.id
                WHERE r.email=? AND s.status!='replied'""", (from_addr,)).fetchall()

            if not rows:
                continue

            for rec_id, send_id, draft_id, day in rows:
                if self.db.execute("SELECT 1 FROM replies WHERE message_id=?", (msg["id"],)).fetchone():
                    continue
                body = msg.get("body", "")[:2000]
                self.db.execute("""INSERT INTO replies (send_id, thread_id, message_id, from_addr, subject, body, received_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (send_id, msg.get("threadId", ""), msg["id"], from_addr, msg.get("subject", ""), body, datetime.now().isoformat()))
                self.db.execute("UPDATE sends SET status='replied' WHERE id=?", (send_id,))
                new_count += 1
                self._log(f"New reply from {from_addr}: {msg.get('subject', '')[:60]}")
                break

        self.db.set_meta("last_reply_scan", datetime.now().isoformat())
        if new_count:
            self._log(f"Found {new_count} new replies (checked {checked_count} messages)")
        else:
            self._log(f"No new replies found (checked {checked_count} messages)")
        return new_count

    def _check_eod(self, now: datetime):
        if now.hour != EOD_HOUR or now.minute > 5: return
        last = self.db.get_meta("last_eod_run")
        today = now.replace(hour=EOD_HOUR, minute=0, second=0, microsecond=0)
        if last and datetime.fromisoformat(last) >= today: return
        self.draft_replies_eod()

    def draft_replies_eod(self) -> dict:
        import requests
        pending = self.db.execute("SELECT * FROM replies WHERE status='pending'").fetchall()
        counts = {"positive": 0, "neutral": 0, "hostile": 0, "unsubscribe": 0, "drafted": 0}

        for row in pending:
            reply_id, send_id, thread_id, message_id, from_addr, subject, body, *_ = row
            rec = self.db.execute("""SELECT r.*, s.day, s.subject as orig_subject
                FROM recipients r JOIN sends s ON s.recipient_id=r.id WHERE s.id=?""", (send_id,)).fetchone()
            if not rec: continue

            seq_id = rec[1]
            persona = SEQUENCES.get(seq_id, {}).get("persona", "school")
            name, org = rec[3], rec[4]

            system = self._persona_prompt(persona)
            user = f"Recipient: {name} from {org}. Original: {rec[10]}. Reply: --- {body} --- Return JSON: {{sentiment, summary, draft_html}}"

            try:
                r = requests.post(f"{self.ollama_url}/api/chat", json={
                    "model": "gpt-oss:20b-cloud",
                    "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                    "stream": False
                }, timeout=120)
                content = r.json()["message"]["content"]
                m = re.search(r"\{.*\}", content, re.DOTALL)
                if not m: continue
                result = json.loads(m.group())

                sentiment = result.get("sentiment", "neutral")
                counts[sentiment] = counts.get(sentiment, 0) + 1

                if sentiment in ("hostile", "unsubscribe"):
                    self.db.blacklist_add(from_addr, f"sentiment:{sentiment}")
                    self.db.execute("UPDATE replies SET status='handled', sentiment=? WHERE id=?", (sentiment, reply_id))
                    self._log(f"Auto-blacklisted {from_addr} ({sentiment})")
                    continue

                draft = self.gmail.draft_reply(thread_id, result.get("draft_html", ""), f"Re: {subject}" if not subject.startswith("Re:") else subject)
                draft_id = draft.get("id") if draft else None
                self.db.execute("UPDATE replies SET status='drafted', sentiment=?, summary=?, draft_reply_id=? WHERE id=?",
                    (sentiment, result.get("summary", ""), draft_id, reply_id))
                counts["drafted"] += 1
                self._log(f"Drafted reply for {from_addr} ({sentiment}) -- waiting for your approval")
            except Exception as e:
                self._log(f"EOD draft failed: {e}")

        self.db.set_meta("last_eod_run", datetime.now().isoformat())
        self._log(f"EOD complete: {counts}")
        return counts

    def _persona_prompt(self, persona: str) -> str:
        return {
            "school": "You are the RoboPirate school outreach team. Warm, professional HTML emails to Indian private school principals. Never salesy.",
            "csr": "You are the RoboPirate CSR team. Formal, impact-focused emails to CSR heads. Data-driven and professional.",
            "csr-wsl-5": "You are the RoboPirate CSR team. Formal, impact-focused emails to CSR heads about the 5-year co-funded pilot model. Data-driven, employment-focused, and professional.",
        }.get(persona, "")

    # -- Morning Brief --
    def _check_morning_brief(self, now: datetime):
        if now.hour != MORNING_HOUR or now.minute > 5: return
        last = self.db.get_meta("last_morning_brief")
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if last and datetime.fromisoformat(last) >= today: return

        brief = self.morning_brief()
        if self.brief_email:
            try:
                self.gmail.send_email(self.brief_email, f"Raj Brief -- {now.strftime('%d %b %Y')}", brief.replace("\n", "<br>"))
                self._log("Morning brief sent")
            except Exception as e:
                self._log(f"Brief failed: {e}")
        self.db.set_meta("last_morning_brief", now.isoformat())

    def morning_brief(self) -> str:
        today = datetime.now().strftime("%d %b %Y")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        lines = ["=" * 40, f"RAJ BRIEF -- {today}", "=" * 40, "YESTERDAY"]

        for seq_id in SEQUENCES:
            stats = self.db.execute("SELECT day, COUNT(*) FROM sends WHERE recipient_id IN (SELECT id FROM recipients WHERE sequence_id=?) AND DATE(created_at)=? GROUP BY day", (seq_id, yesterday)).fetchall()
            if stats:
                for day, count in stats: lines.append(f"  {seq_id.upper()} Day {day}: {count} sent")
            else: lines.append(f"  {seq_id.upper()}: No batches")

        replies = self.db.execute("SELECT sentiment, COUNT(*) FROM replies WHERE DATE(received_at)=? OR status IN ('pending','drafted') GROUP BY sentiment", (yesterday,)).fetchall()
        rc = {k: 0 for k in ["positive", "neutral", "hostile", "unsubscribe"]}
        for s, c in replies:
            if s in rc: rc[s] = c
        lines.extend(["", f"REPLIES ({sum(rc.values())} total)", f"  -- {rc['positive']} positive", f"  -- {rc['neutral']} neutral", f"  -- {rc['hostile'] + rc['unsubscribe']} hostile -- blacklisted", "  -> Review drafts in Gmail before sending"])

        bounces = self.db.execute("SELECT email, reason FROM blacklist WHERE DATE(added_at)=? OR reason LIKE 'bounce %'", (yesterday,)).fetchall()
        lines.extend(["", f"BOUNCES ({len(bounces)} overnight)"])
        for email, reason in bounces[:5]: lines.append(f"  {email} -- {reason}")

        lines.extend(["", "DUE TODAY"])
        for seq_id in SEQUENCES:
            for day in SEQUENCES[seq_id]["days"]:
                due = len(self.due_recipients(seq_id, day))
                if due: lines.append(f"  {seq_id.upper()} Day {day}: {due} recipients")

        lines.extend(["", "YOUR ACTIONS", "  1. Review reply drafts in Gmail (DRAFT-ONLY for approval)", "  2. Sequences auto-send at 10 AM -- no action needed", "  3. Reply STOP SCHOOL / STOP CSR / STOP ALL to pause", "=" * 40])
        return "\n".join(lines)

    # -- Emergency Commands --
    def _check_emergency_commands(self, now: datetime):
        last = self.db.get_meta("last_emergency_scan")
        if last and (now - datetime.fromisoformat(last)) < timedelta(minutes=EMERGENCY_INTERVAL): return

        after = int((datetime.now() - timedelta(hours=1)).timestamp())
        msgs = self.gmail.search_messages(f"in:inbox from:me subject:(STOP SCHOOL OR STOP CSR OR STOP ALL OR RESUME) after:{after}", 10)

        for msg in msgs:
            subj = msg.get("subject", "").upper()
            if "STOP SCHOOL" in subj: self.db.set_meta("pause_school", "true"); self._log("SCHOOL paused")
            elif "STOP CSR" in subj: self.db.set_meta("pause_csr", "true"); self._log("CSR paused")
            elif "STOP ALL" in subj: self.pause(); self._log("ALL paused")
            elif "RESUME" in subj: self.resume(); self.db.execute("DELETE FROM meta WHERE key LIKE 'pause_%'"); self._log("All resumed")

        self.db.set_meta("last_emergency_scan", now.isoformat())

    # -- Campaign State Export --
    def export_campaign_state(self) -> str:
        from pathlib import Path
        now = datetime.now().strftime("%d %b %Y %H:%M")
        lines = [
            f"# Raj Campaign State -- {now}",
            "",
            "## Sequences",
            ""
        ]

        for seq_id in SEQUENCES:
            lines.append(f"### {seq_id.upper()}")
            cfg = SEQUENCES[seq_id]
            for day in cfg["days"]:
                due = self.due_recipients(seq_id, day)
                sent = self.db.execute(
                    "SELECT COUNT(DISTINCT recipient_id) FROM sends WHERE day=? AND status IN ('sent','drafted') AND recipient_id IN (SELECT id FROM recipients WHERE sequence_id=?)",
                    (day, seq_id)
                ).fetchone()[0]
                total = self.db.execute("SELECT COUNT(*) FROM recipients WHERE sequence_id=?", (seq_id,)).fetchone()[0]
                lines.append(f"- Day {day}: {sent}/{total} sent | {len(due)} due")
            lines.append("")

        pending = self.db.execute("SELECT sequence_id, day, COUNT(*) FROM pending_resumes WHERE status='pending' GROUP BY sequence_id, day").fetchall()
        if pending:
            lines.append("## Pending Resumes (Quota Interruptions)")
            for seq_id, day, count in pending:
                lines.append(f"- {seq_id.upper()} Day {day}: {count} emails waiting to resume")
            lines.append("")
        else:
            lines.append("## Pending Resumes")
            lines.append("- None. All batches completed cleanly.")
            lines.append("")

        pending_replies = self.db.execute("SELECT COUNT(*) FROM replies WHERE status='pending'").fetchone()[0]
        drafted_replies = self.db.execute("SELECT COUNT(*) FROM replies WHERE status='drafted'").fetchone()[0]
        lines.append("## Replies")
        lines.append(f"- Pending: {pending_replies}")
        lines.append(f"- Drafted (awaiting approval): {drafted_replies}")
        lines.append("")

        bl_count = self.db.execute("SELECT COUNT(*) FROM blacklist").fetchone()[0]
        bl_recent = self.db.execute("SELECT email, reason FROM blacklist ORDER BY added_at DESC LIMIT 10").fetchall()
        lines.append(f"## Blacklist ({bl_count} total)")
        for email, reason in bl_recent:
            lines.append(f"- `{email}` -- {reason}")
        lines.append("")

        lines.append("## Engine Status")
        lines.append(f"- Running: {self.is_running()}")
        lines.append(f"- Paused: {self.is_paused()}")
        lines.append(f"- Last bounce scan: {self.db.get_meta('last_bounce_scan') or 'Never'}")
        lines.append(f"- Last reply scan: {self.db.get_meta('last_reply_scan') or 'Never'}")
        lines.append("")

        lines.append("---")
        lines.append("*Auto-generated by Raj Campaign Engine*")

        md = "\n".join(lines)

        state_path = Path(__file__).parent / "campaign_state.md"
        with open(state_path, "w", encoding="utf-8") as f:
            f.write(md)

        self._log(f"Campaign state exported to {state_path}")
        return md

    # -- Quota Rollback & Resume --
    def resume_batch(self, seq_id: str, day: int, limit=None) -> BatchResult:
        pending = self.db.execute(
            "SELECT recipient_id, subject FROM pending_resumes WHERE sequence_id=? AND day=? AND status='pending' ORDER BY id",
            (seq_id, day)
        ).fetchall()

        if not pending:
            self._log(f"No pending resumes for {seq_id.upper()} Day {day}")
            return BatchResult(queued=0, sent=0)

        if limit:
            pending = pending[:limit]

        self._log(f"Resuming {seq_id.upper()} Day {day}: {len(pending)} pending")
        sent = 0

        for rec_id, subject in pending:
            rec_row = self.db.execute("SELECT * FROM recipients WHERE id=?", (rec_id,)).fetchone()
            if not rec_row:
                continue
            rec = Recipient(*rec_row)

            subj, body = self.render(seq_id, day, rec)
            if not subj:
                subj = subject

            try:
                msg = self.gmail.send_email(rec.email, subj, body)
                self.db.campaign_queue_send(rec.id, day, subj, msg.get("id"), "sent")
                self.db.execute(
                    "UPDATE pending_resumes SET status='sent', resumed_at=? WHERE recipient_id=? AND sequence_id=? AND day=? AND status='pending'",
                    (datetime.now().isoformat(), rec.id, seq_id, day)
                )
                sent += 1
                self._log(f"Resumed send to {rec.email}")
                time.sleep(SEND_DELAY)
            except Exception as e:
                err = str(e)
                if "quota" in err.lower() or "rate" in err.lower() or "limit" in err.lower():
                    self._log("Rate limit hit again during resume. Stopping.")
                    break
                self._log(f"Resume failed for {rec.email}: {e}")
                self.db.execute(
                    "UPDATE pending_resumes SET status='error', error=? WHERE recipient_id=? AND sequence_id=? AND day=? AND status='pending'",
                    (str(e)[:200], rec.id, seq_id, day)
                )

        self.db.commit()
        self._log(f"Resume complete: {sent}/{len(pending)} sent")
        return BatchResult(queued=len(pending), sent=sent)

    def backdate_sequence(self, seq_id: str, day: int, days_ago: int) -> int:
        cutoff = (datetime.now() - timedelta(days=days_ago)).isoformat()
        rows = self.db.execute(
            "SELECT id, created_at FROM sends WHERE recipient_id IN (SELECT id FROM recipients WHERE sequence_id=?) AND day=? AND created_at > ?",
            (seq_id, day, cutoff)
        ).fetchall()

        count = 0
        for send_id, created_at in rows:
            new_time = (datetime.fromisoformat(created_at) - timedelta(days=days_ago)).isoformat()
            self.db.execute("UPDATE sends SET created_at=? WHERE id=?", (new_time, send_id))
            count += 1

        self.db.commit()
        self._log(f"Backdated {count} sends for {seq_id.upper()} Day {day} by {days_ago} days")
        return count

    def import_blacklist_file(self, filepath: str) -> int:
        from pathlib import Path
        path = Path(filepath)
        if not path.exists():
            self._log(f"Blacklist file not found: {filepath}")
            return 0

        emails = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                found = re.findall(r"[\w.+\-]+@[\w.\-]+", line)
                emails.extend(found)

        unique = list(set(e.lower().strip() for e in emails if "@" in e))
        count = 0
        for email in unique:
            if not self.db.blacklist_has(email):
                self.db.blacklist_add(email, f"imported_from_file {path.name}")
                count += 1

        self._log(f"Imported {count} new blacklisted emails from {path.name} ({len(unique)} found)")
        return count
