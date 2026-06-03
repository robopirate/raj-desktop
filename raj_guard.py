"""
RAJ AI GUARD v1.0
Background daemon that watches Raj, detects issues, auto-heals, and learns.
Runs in parallel with Raj — never blocks startup.
"""

import os
import sys
import time
import json
import re
import ast
import sqlite3
import threading
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ───────────────────────────────────────────────
# CONFIGURATION
# ───────────────────────────────────────────────
GUARD_VERSION = "1.0"
CHECK_INTERVAL = 30  # seconds between health checks
MORNING_BRIEF_HOUR = 8  # 8 AM IST
MORNING_BRIEF_MINUTE = 0

# Known bug patterns from Raj history (learned from 42+ bugs)
BUG_PATTERNS = {
    "empty_html_template": {
        "pattern": r'HTML_TEMPLATE\s*=\s*"""\s*"""',
        "fix_type": "replace",
        "description": "Empty HTML template — emails sent without branding"
    },
    "dead_refresh_loop": {
        "pattern": r'if\s+hasattr\(self,\s*[\'"\"]views[\'"\"]\)\s+and\s+[\'"\"]dashboard[\'"\"]\s+in\s+self\.views:\s*\n\s*pass\s*#',
        "fix_type": "replace",
        "description": "Dashboard auto-refresh dead — pass does nothing"
    },
    "duplicate_import_method": {
        "pattern": r'def\s+_import_batch_recipients\(self,\s*batch_id,\s*filepath\):.*?PANDAS_AVAILABLE\s*=\s*True.*?def\s+_import_batch_recipients\(self,\s*batch_id,\s*filepath\):',
        "fix_type": "remove_duplicate",
        "description": "Duplicate _import_batch_recipients method"
    },
    "calendar_not_defined": {
        "pattern": r'^\s*#\s*CALENDAR_AVAILABLE\s*=\s*False',
        "fix_type": "inject",
        "description": "CALENDAR_AVAILABLE not defined at module level"
    },
    "clay_width_none": {
        "pattern": r'width\s*=\s*None\s*,\s*command\s*=\s*command',
        "fix_type": "replace",
        "description": "CustomTkinter width=None crashes"
    },
    "clay_alpha_color": {
        "pattern": r'fg_color\s*=\s*f"\{color\}15"',
        "fix_type": "replace",
        "description": "Invalid alpha hex color in CustomTkinter"
    },
    "engine_not_started": {
        "pattern": r'engine\s*=\s*CampaignEngine\(.*\)\s*\n(?!.*engine\.start)',
        "fix_type": "inject_after",
        "description": "Engine created but never started"
    },
    "missing_bracket_sql": {
        "pattern": r'SELECT\s+r\.\*\s*,\s*br\.status\s+FROM\s+batch_recipients',
        "fix_type": "replace",
        "description": "SQL query selects too many columns — will crash batch processing"
    },
    "blacklist_own_email": {
        "pattern": r'def\s+_scan_bounces\(self\):',
        "fix_type": "inject_after_first",
        "description": "Missing protection for own domain in bounce scan"
    }
}

# HTML Template replacement (used when empty template detected)
HTML_TEMPLATE_REPLACEMENT = """<!DOCTYPE html>
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

# ───────────────────────────────────────────────
# GUARD CLASS
# ───────────────────────────────────────────────

class RajGuard:
    """Background daemon that watches Raj and heals it."""

    def __init__(self, app_folder: str, db_path: str = None):
        self.app_folder = Path(app_folder)
        self.db_path = db_path or self.app_folder / "campaign_data.db"
        self.memory_file = self.app_folder / "raj_guard_memory.json"
        self.sop_file = self.app_folder / "raj_guard_sop.md"
        self.log_file = self.app_folder / "raj_guard.log"
        self.memory = self._load_memory()
        self.running = False
        self.thread = None
        self.last_check = None
        self.fixes_applied = []
        self.issues_found = []
        self._log(f"🛡️ Raj Guard v{GUARD_VERSION} initialized")
        self._log(f"📁 Watching folder: {self.app_folder}")
        self._log(f"🗄️  Database: {self.db_path}")

    # ─── Memory ─────────────────────────────────

    def _load_memory(self) -> Dict:
        """Load learning memory from JSON file."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f2:
                    return json.load(f2)
            except:
                pass
        return {
            "version": GUARD_VERSION,
            "created_at": datetime.now().isoformat(),
            "bugs_encountered": [],
            "fixes_applied": [],
            "performance_baseline": {},
            "user_preferences": {},
            "industry_insights": [],
            "last_morning_brief": None
        }

    def _save_memory(self):
        """Save learning memory to JSON file."""
        self.memory["updated_at"] = datetime.now().isoformat()
        with open(self.memory_file, "w", encoding="utf-8") as f2:
            json.dump(self.memory, f2, indent=2, default=str)

    def _log(self, message: str):
        """Write to guard log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}"
        print(f"🛡️  {line}")
        try:
            with open(self.log_file, "a", encoding="utf-8") as f2:
                f2.write(line + "\n")
        except:
            pass

    # ─── Core Checks ────────────────────────────

    def check_syntax(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Check Python file for syntax errors using AST."""
        try:
            with open(file_path, "r", encoding="utf-8") as f2:
                source = f2.read()
            ast.parse(source)
            return True, []
        except SyntaxError as e:
            return False, [f"Syntax error in {file_path.name} line {e.lineno}: {e.msg}"]
        except Exception as e:
            return False, [f"Parse error in {file_path.name}: {str(e)}"]

    def check_all_files(self) -> Dict[str, List[str]]:
        """Check all core Python files for syntax errors."""
        core_files = [
            "main.py", "engine.py", "raj_chat.py", "raj_brain.py",
            "db.py", "gmail.py", "smart_importer.py"
        ]
        results = {}
        for fname in core_files:
            fpath = self.app_folder / fname
            if fpath.exists():
                ok, errors = self.check_syntax(fpath)
                if not ok:
                    results[fname] = errors
                    self._log(f"❌ Syntax error in {fname}: {errors[0]}")
        return results

    def check_database_integrity(self) -> Dict:
        """Check SQLite database for corruption and orphans."""
        issues = []
        stats = {}
        if not self.db_path.exists():
            return {"status": "missing", "issues": ["Database file not found"]}
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [t[0] for t in cursor.fetchall()]
            required = ["recipients", "batches", "batch_recipients", "sends", "replies", "blacklist", "templates", "audit_log"]
            missing = [t for t in required if t not in tables]
            if missing:
                issues.append(f"Missing tables: {missing}")
            for table in required:
                if table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[table] = cursor.fetchone()[0]
            if "batch_recipients" in tables and "batches" in tables:
                cursor.execute("SELECT COUNT(*) FROM batch_recipients WHERE batch_id NOT IN (SELECT id FROM batches)")
                orphan_batches = cursor.fetchone()[0]
                if orphan_batches > 0:
                    issues.append(f"{orphan_batches} orphaned batch_recipients (bad batch_id)")
            if "batch_recipients" in tables and "recipients" in tables:
                cursor.execute("SELECT COUNT(*) FROM batch_recipients WHERE recipient_id NOT IN (SELECT id FROM recipients)")
                orphan_recipients = cursor.fetchone()[0]
                if orphan_recipients > 0:
                    issues.append(f"{orphan_recipients} orphaned batch_recipients (bad recipient_id)")
            if "batches" in tables:
                cursor.execute("SELECT name, COUNT(*) as cnt FROM batches GROUP BY name HAVING cnt > 1")
                dups = cursor.fetchall()
                if dups:
                    issues.append(f"{len(dups)} duplicate batch names: {[d[0] for d in dups]}")
            if "batches" in tables and "sends" in tables:
                cursor.execute("SELECT b.id, b.name FROM batches b WHERE b.status = 'running' AND b.id NOT IN (SELECT DISTINCT batch_id FROM sends)")
                stuck = cursor.fetchall()
                if stuck:
                    issues.append(f"{len(stuck)} stuck batches (running but 0 sends): {[s[1] for s in stuck]}")
            conn.close()
        except Exception as e:
            issues.append(f"DB check failed: {str(e)}")
        return {"status": "ok" if not issues else "issues", "stats": stats, "issues": issues}

    def check_engine_health(self) -> Dict:
        """Check if engine.py has known broken patterns."""
        issues = []
        fixes = []
        engine_path = self.app_folder / "engine.py"
        if not engine_path.exists():
            return {"status": "missing", "issues": ["engine.py not found"]}
        with open(engine_path, "r", encoding="utf-8") as f2:
            engine_code = f2.read()
        if re.search(BUG_PATTERNS["empty_html_template"]["pattern"], engine_code, re.DOTALL):
            issues.append("Empty HTML template — emails sent without branding")
            if self._try_fix_file(engine_path, "empty_html_template"):
                fixes.append("Fixed empty HTML template")
        if "CALENDAR_AVAILABLE" not in engine_code:
            issues.append("CALENDAR_AVAILABLE not defined")
        elif re.search(BUG_PATTERNS["calendar_not_defined"]["pattern"], engine_code, re.MULTILINE):
            issues.append("CALENDAR_AVAILABLE commented out")
        if re.search(BUG_PATTERNS["missing_bracket_sql"]["pattern"], engine_code):
            issues.append("SQL query selects too many columns — will crash batch processing")
        if "is_protected_email" not in engine_code:
            issues.append("Missing @robopirate.in protection in bounce scan")
        return {"status": "ok" if not issues else "issues", "issues": issues, "fixes": fixes}

    def check_ui_health(self) -> Dict:
        """Check raj_chat.py for known broken patterns."""
        issues = []
        fixes = []
        chat_path = self.app_folder / "raj_chat.py"
        if not chat_path.exists():
            return {"status": "missing", "issues": ["raj_chat.py not found"]}
        with open(chat_path, "r", encoding="utf-8") as f2:
            chat_code = f2.read()
        if re.search(BUG_PATTERNS["dead_refresh_loop"]["pattern"], chat_code):
            issues.append("Dashboard auto-refresh has 'pass' — never updates")
            if self._try_fix_file(chat_path, "dead_refresh_loop"):
                fixes.append("Fixed dashboard auto-refresh")
        matches = list(re.finditer(r"def\s+_import_batch_recipients\(self,\s*batch_id,\s*filepath\):", chat_code))
        if len(matches) > 1:
            issues.append(f"Duplicate _import_batch_recipients method ({len(matches)} times)")
        if "ClayUI.build_clay_dashboard" in chat_code:
            issues.append("raj_chat.py still calls broken ClayUI — will crash")
        return {"status": "ok" if not issues else "issues", "issues": issues, "fixes": fixes}

    # ─── Auto-Fix Engine ────────────────────────

    def _try_fix_file(self, file_path: Path, bug_key: str) -> bool:
        """Attempt to auto-fix a known bug pattern."""
        bug = BUG_PATTERNS.get(bug_key)
        if not bug:
            return False
        try:
            with open(file_path, "r", encoding="utf-8") as f2:
                content = f2.read()
            original = content
            if bug["fix_type"] == "replace":
                if bug_key == "empty_html_template":
                    content = re.sub(bug["pattern"], 'HTML_TEMPLATE = """' + HTML_TEMPLATE_REPLACEMENT + '"""', content, flags=re.DOTALL)
                elif bug_key == "dead_refresh_loop":
                    # Simple string replacement for dead refresh loop
                    content = content.replace("pass  # <-- DOES NOTHING", "self._refresh_dashboard()  # Fixed by Guard")
                elif bug_key == "clay_width_none":
                    content = re.sub(r"width\s*=\s*None\s*,\s*command\s*=\s*command", "width=0, command=command", content)
                elif bug_key == "clay_alpha_color":
                    content = re.sub(r"fg_color\s*=\s*f\"\{color\}15\"", 'fg_color="transparent"', content)
                elif bug_key == "missing_bracket_sql":
                    content = re.sub(r"SELECT\s+r\.\*\s*,\s*br\.status\s+FROM\s+batch_recipients", "SELECT r.id, r.sequence_id, r.email, r.name, r.org, r.extra_json, r.imported_at, br.status FROM batch_recipients", content)
            elif bug["fix_type"] == "inject":
                if bug_key == "calendar_not_defined":
                    if "CALENDAR_AVAILABLE = False" not in content:
                        content = "CALENDAR_AVAILABLE = False\nDRIVE_AVAILABLE = False\n" + content
            elif bug["fix_type"] == "remove_duplicate":
                pattern = r"def\s+_import_batch_recipients\(self,\s*batch_id,\s*filepath\):"
                matches = list(re.finditer(pattern, content))
                if len(matches) > 1:
                    start = matches[1].start()
                    next_def = re.search(r"\n\s{4}def\s+", content[start:])
                    if next_def:
                        end = start + next_def.start()
                    else:
                        end = len(content)
                    content = content[:start] + content[end:]
            if content != original:
                backup = file_path.with_suffix(file_path.suffix + ".guard_backup")
                with open(backup, "w", encoding="utf-8") as f2:
                    f2.write(original)
                with open(file_path, "w", encoding="utf-8") as f2:
                    f2.write(content)
                self._log(f"🔧 Auto-fixed: {bug['description']} in {file_path.name}")
                self.memory["fixes_applied"].append({
                    "timestamp": datetime.now().isoformat(),
                    "file": file_path.name,
                    "bug": bug_key,
                    "description": bug["description"]
                })
                self._save_memory()
                return True
        except Exception as e:
            self._log(f"❌ Auto-fix failed for {bug_key}: {str(e)}")
        return False

    # ─── Morning Brief ──────────────────────────

    def generate_morning_brief(self) -> str:
        """Generate daily morning brief email content."""
        brief = []
        brief.append("🤖 RAJ DAILY BRIEF — " + datetime.now().strftime("%B %d, %Y"))
        brief.append("=" * 50)
        db_check = self.check_database_integrity()
        if db_check["status"] == "ok":
            stats = db_check.get("stats", {})
            brief.append("\n📊 YESTERDAY'S NUMBERS")
            brief.append(f"   • Leads in pool: {stats.get('recipients', 0)}")
            brief.append(f"   • Total sends: {stats.get('sends', 0)}")
            brief.append(f"   • Replies: {stats.get('replies', 0)}")
            brief.append(f"   • Blacklisted: {stats.get('blacklist', 0)}")
        if self.issues_found:
            brief.append(f"\n⚠️  ISSUES DETECTED ({len(self.issues_found)})")
            for issue in self.issues_found[-5:]:
                brief.append(f"   • {issue}")
        recent_fixes = [f for f in self.memory.get("fixes_applied", []) 
                       if datetime.fromisoformat(f["timestamp"]) > datetime.now() - timedelta(days=1)]
        if recent_fixes:
            brief.append(f"\n🔧 AUTO-FIXES APPLIED ({len(recent_fixes)})")
            for fix in recent_fixes:
                brief.append(f"   • {fix['file']}: {fix['description']}")
        insights = self.memory.get("industry_insights", [])
        if insights:
            brief.append(f"\n💡 INDUSTRY INSIGHT")
            brief.append(f"   {insights[-1]}")
        else:
            brief.append(f"\n💡 TIP")
            brief.append(f"   Send-time optimization: Indian principals check email at 8:30 AM and 2:00 PM.")
            brief.append(f"   Consider adjusting your D1 send time from 10:00 AM to 8:30 AM.")
        brief.append(f"\n🎯 TODAY'S FOCUS")
        brief.append(f"   • Review stuck batches (if any)")
        brief.append(f"   • Check reply sentiment for hostile responses")
        brief.append(f"   • Verify template locking before any edits")
        brief.append(f"\n— Raj Guard v{GUARD_VERSION}")
        brief.append(f"Sent at {datetime.now().strftime('%H:%M IST')}")
        return "\n".join(brief)

    def send_morning_brief(self, email_address: str = "itsomkarsinghhh@gmail.com"):
        """Send morning brief via Gmail API if available."""
        try:
            sys.path.insert(0, str(self.app_folder))
            from gmail import GmailClient
            client = GmailClient()
            subject = f"Raj Daily Brief — {datetime.now().strftime('%B %d, %Y')}"
            body = self.generate_morning_brief()
            client.send_email(email_address, subject, body)
            self._log(f"📧 Morning brief sent to {email_address}")
            self.memory["last_morning_brief"] = datetime.now().isoformat()
            self._save_memory()
        except Exception as e:
            self._log(f"⚠️  Could not send morning brief: {str(e)}")
            brief_path = self.app_folder / "morning_brief.txt"
            with open(brief_path, "w", encoding="utf-8") as f2:
                f2.write(self.generate_morning_brief())
            self._log(f"📝 Morning brief saved to {brief_path}")

    # ─── Main Loop ──────────────────────────────

    def _check_once(self):
        """Run one full health check cycle."""
        self._log("🔍 Running health check...")
        self.issues_found = []
        self.fixes_applied = []
        syntax_issues = self.check_all_files()
        if syntax_issues:
            for fname, errors in syntax_issues.items():
                self.issues_found.extend(errors)
        else:
            self._log("✅ All core files syntax OK")
        db_check = self.check_database_integrity()
        if db_check["status"] == "ok":
            self._log(f"✅ Database OK — {db_check.get('stats', {})}")
        else:
            self.issues_found.extend(db_check.get("issues", []))
            for issue in db_check["issues"]:
                self._log(f"❌ DB Issue: {issue}")
        engine_check = self.check_engine_health()
        if engine_check["fixes"]:
            self.fixes_applied.extend(engine_check["fixes"])
        if engine_check["status"] != "ok":
            self.issues_found.extend(engine_check.get("issues", []))
            for issue in engine_check["issues"]:
                self._log(f"⚠️  Engine: {issue}")
        else:
            self._log("✅ Engine health OK")
        ui_check = self.check_ui_health()
        if ui_check["fixes"]:
            self.fixes_applied.extend(ui_check["fixes"])
        if ui_check["status"] != "ok":
            self.issues_found.extend(ui_check.get("issues", []))
            for issue in ui_check["issues"]:
                self._log(f"⚠️  UI: {issue}")
        else:
            self._log("✅ UI health OK")
        now = datetime.now()
        if now.hour == MORNING_BRIEF_HOUR and now.minute == MORNING_BRIEF_MINUTE:
            last_brief = self.memory.get("last_morning_brief")
            if not last_brief or datetime.fromisoformat(last_brief).date() != now.date():
                self._log("📧 Sending morning brief...")
                self.send_morning_brief()
        self.last_check = now.isoformat()
        self._log(f"✅ Health check complete — {len(self.issues_found)} issues, {len(self.fixes_applied)} fixes")

    def _guard_loop(self):
        """Background thread loop."""
        self._log("🛡️ Guard daemon started")
        try:
            self._check_once()
        except Exception as e:
            self._log(f"❌ First check failed: {str(e)}")
            self._log(traceback.format_exc())
        while self.running:
            time.sleep(CHECK_INTERVAL)
            if not self.running:
                break
            try:
                self._check_once()
            except Exception as e:
                self._log(f"❌ Check cycle failed: {str(e)}")

    def start(self):
        """Start the Guard in a background thread."""
        if self.running:
            self._log("Guard already running")
            return
        self.running = True
        self.thread = threading.Thread(target=self._guard_loop, daemon=True, name="RajGuard")
        self.thread.start()
        self._log("🛡️ Raj Guard daemon thread started (parallel to Raj)")

    def stop(self):
        """Stop the Guard."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        self._log("🛡️ Raj Guard stopped")

    def get_status(self) -> Dict:
        """Return current Guard status."""
        return {
            "version": GUARD_VERSION,
            "running": self.running,
            "last_check": self.last_check,
            "issues_found_count": len(self.issues_found),
            "fixes_applied_count": len(self.memory.get("fixes_applied", [])),
            "bugs_learned": len(self.memory.get("bugs_encountered", [])),
            "memory_file": str(self.memory_file)
        }

# ───────────────────────────────────────────────
# STANDALONE MODE
# ───────────────────────────────────────────────

if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    guard = RajGuard(folder)
    guard._check_once()
    print("\n" + "="*50)
    print("STATUS:", json.dumps(guard.get_status(), indent=2))
