"""
web/app.py — Flask backend for the new Raj web UI.
Wraps existing engine.py / db.py / gmail.py methods in REST endpoints.
"""

import csv
import io
import os
import sys
import tempfile
import threading
import uuid
import webbrowser
from datetime import datetime
from html import escape
from pathlib import Path

# Make project root importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from db import Database
from engine import CampaignEngine, SEQUENCES

try:
    from email_validator import validate_email
    EMAIL_VALIDATOR_AVAILABLE = True
except Exception:
    validate_email = None
    EMAIL_VALIDATOR_AVAILABLE = False

# Static/template folders relative to this file
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
STATIC_DIR = Path(__file__).resolve().parent / "static"

app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(STATIC_DIR))
CORS(app)

# ── Engine initialization ───────────────────────────────────────────────────
# We instantiate engine once at startup. Gmail auth may fail (token expired),
# but we catch it so the web UI can show a "Connect Gmail" button.
_db = Database()
_gmail = None
_engine = None
_last_connect_error = {}  # service -> {"success": bool, "error": str | None}


def _init_engine():
    global _gmail, _engine
    try:
        from gmail import GmailClient
        _gmail = GmailClient()
    except Exception as e:
        print(f"[WebApp] Gmail not connected at startup: {e}")
        _gmail = None

    try:
        _engine = CampaignEngine(_db, _gmail) if _gmail else CampaignEngine(_db, None)
    except Exception as e:
        print(f"[WebApp] Engine init warning: {e}")
        _engine = CampaignEngine.__new__(CampaignEngine)
        _engine.db = _db
        _engine.gmail = _gmail
        _engine.calendar = None
        _engine.drive = None
        _engine._running = False
        _engine._paused = True


_init_engine()


# ── Helpers ───────────────────────────────────────────────────────────────────
def _ok(data=None):
    return jsonify({"success": True, "data": data, "error": None})


def _err(message, code=400):
    return jsonify({"success": False, "data": None, "error": message}), code


def _engine_or_500():
    if _engine is None:
        return None, _err("Engine not initialized", 500)
    return _engine, None


# ── Frontend ──────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(str(TEMPLATE_DIR), "index.html")


@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory(str(STATIC_DIR), path)


# ── Health ────────────────────────────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    return _ok({
        "status": "ok",
        "version": getattr(_engine, "VERSION", "5.0.0") if _engine else "5.0.0",
        "engine_initialized": _engine is not None,
        "gmail_connected": _gmail.is_connected() if _gmail else False,
        "last_error": _last_connect_error,
    })


# ── Dashboard ─────────────────────────────────────────────────────────────────
@app.route("/api/dashboard/summary", methods=["GET"])
def dashboard_summary():
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        summary = engine.get_summary()
        return _ok(summary)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/dashboard/pipeline", methods=["GET"])
def dashboard_pipeline():
    try:
        pipeline = _db.get_pipeline()
        day_wise = {}
        for seq in ["school", "csr", "csr-wsl-5"]:
            try:
                day_wise[seq] = _db.get_day_wise_pipeline(seq)
            except Exception:
                day_wise[seq] = []
        return _ok({"pipeline": pipeline, "day_wise": day_wise})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/dashboard/batches", methods=["GET"])
def dashboard_batches():
    try:
        active = _db.get_running_batches()
        scheduled = _db.get_scheduled_batches()
        return _ok({"running": active, "scheduled": scheduled})
    except Exception as e:
        return _err(str(e), 500)


# ── Batches ───────────────────────────────────────────────────────────────────
@app.route("/api/batches", methods=["GET"])
def list_batches():
    try:
        sequence_id = request.args.get("sequence_id")
        batches = _db.batch_get_all(sequence_id=sequence_id)
        return _ok(batches)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/batches/<int:batch_id>", methods=["GET"])
def get_batch(batch_id):
    try:
        batch = _db.batch_get(batch_id)
        if not batch:
            return _err("Batch not found", 404)
        counts = _db.batch_count_by_status(batch_id)
        recipients = _db.batch_get_recipients(batch_id)
        return _ok({"batch": batch, "counts": counts, "recipients": recipients})
    except Exception as e:
        return _err(str(e), 500)


# ── Engine control ────────────────────────────────────────────────────────────
@app.route("/api/engine/status", methods=["GET"])
def engine_status():
    engine, error = _engine_or_500()
    if error:
        return error
    return _ok({
        "running": getattr(engine, "is_running", lambda: False)(),
        "paused": getattr(engine, "is_paused", lambda: True)(),
    })


@app.route("/api/engine/pause", methods=["POST"])
def engine_pause():
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        engine.pause()
        return _ok({"paused": True})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/engine/resume", methods=["POST"])
def engine_resume():
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        engine.resume()
        return _ok({"paused": False})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/engine/start", methods=["POST"])
def engine_start():
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        if not engine.is_running():
            engine.start()
        return _ok({"running": engine.is_running()})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/engine/stop", methods=["POST"])
def engine_stop():
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        engine.stop()
        return _ok({"running": False})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/brief", methods=["POST"])
def trigger_brief():
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        text = engine.morning_brief()
        brief_email = _db.get_meta("brief_email") or ""
        sent = False
        if brief_email and getattr(engine, "gmail", None) and engine.gmail.is_connected():
            try:
                engine.gmail.send_email(brief_email, "Raj Morning Brief", f"<pre>{escape(text)}</pre>")
                sent = True
            except Exception as e:
                print(f"[Brief] Send failed: {e}")
        return _ok({"brief": text, "sent": sent, "to": brief_email if sent else None})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/emergency", methods=["POST"])
def emergency_command():
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        data = request.get_json() or {}
        action = data.get("action", "")
        target = data.get("target", "all")
        if action not in ("stop", "resume"):
            return _err("Invalid action", 400)

        if action == "stop":
            if target == "all":
                engine.pause()
            elif target in SEQUENCES:
                _db.set_meta(f"pause_{target}", "true")
            else:
                return _err("Invalid target", 400)
        else:  # resume
            if target == "all":
                engine.resume()
                _db.execute("DELETE FROM meta WHERE key LIKE 'pause_%'")
                _db.commit()
            elif target in SEQUENCES:
                _db.set_meta(f"pause_{target}", "false")
            else:
                return _err("Invalid target", 400)

        return _ok({"action": action, "target": target})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/audit-log", methods=["GET"])
def audit_log():
    try:
        limit = request.args.get("limit", 50, type=int)
        rows = _db.get_audit_log(limit=limit)
        return _ok(rows)
    except Exception as e:
        return _err(str(e), 500)


# ── Analytics ─────────────────────────────────────────────────────────────────
@app.route("/api/analytics/summary", methods=["GET"])
def analytics_summary():
    try:
        days = request.args.get("days", 30, type=int)
        seq = request.args.get("sequence_id") or None
        stats = _db.get_engagement_stats(sequence_id=seq, days_back=days)
        return _ok(stats)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/analytics/daily", methods=["GET"])
def analytics_daily():
    try:
        days = request.args.get("days", 14, type=int)
        seq = request.args.get("sequence_id") or None
        data = _db.get_engagement_by_day(sequence_id=seq, days_back=days)
        return _ok(data)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/analytics/top-links", methods=["GET"])
def analytics_top_links():
    try:
        limit = request.args.get("limit", 8, type=int)
        links = _db.get_top_clicked_links(limit=limit)
        return _ok(links)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/analytics/activity", methods=["GET"])
def analytics_activity():
    try:
        limit = request.args.get("limit", 10, type=int)
        rows = _db.get_recent_activity(limit=limit)
        return _ok(rows)
    except Exception as e:
        return _err(str(e), 500)


# ── Calendar ──────────────────────────────────────────────────────────────────
@app.route("/api/calendar/events", methods=["GET"])
def list_calendar_events():
    engine, error = _engine_or_500()
    if error:
        return error
    if not getattr(engine, "calendar", None) or not engine.calendar.is_connected():
        return _err("Calendar not connected", 400)
    try:
        max_results = request.args.get("max", 10, type=int)
        events = engine.calendar.list_upcoming(max_results=max_results)
        return _ok(events)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/calendar/events", methods=["POST"])
def create_calendar_event():
    engine, error = _engine_or_500()
    if error:
        return error
    if not getattr(engine, "calendar", None) or not engine.calendar.is_connected():
        return _err("Calendar not connected", 400)
    try:
        data = request.get_json() or {}
        result, err = engine.calendar.create_meeting(
            recipient_email=data.get("email", ""),
            recipient_name=data.get("name", ""),
            subject=data.get("subject", ""),
            duration_minutes=int(data.get("duration", 30)),
            days_from_now=int(data.get("days_from_now", 2)),
            time_hour=int(data.get("hour", 10)),
            time_minute=int(data.get("minute", 0)),
            description=data.get("description", "")
        )
        if err:
            return _err(err, 400)
        return _ok(result)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/calendar/events/<event_id>", methods=["DELETE"])
def cancel_calendar_event(event_id):
    engine, error = _engine_or_500()
    if error:
        return error
    if not getattr(engine, "calendar", None) or not engine.calendar.is_connected():
        return _err("Calendar not connected", 400)
    try:
        ok = engine.calendar.cancel_event(event_id)
        return _ok({"cancelled": ok})
    except Exception as e:
        return _err(str(e), 500)


# ── Drive ─────────────────────────────────────────────────────────────────────
@app.route("/api/drive/files", methods=["GET"])
def list_drive_files():
    engine, error = _engine_or_500()
    if error:
        return error
    if not getattr(engine, "drive", None) or not engine.drive.is_connected():
        return _err("Drive not connected", 400)
    try:
        folder_id = request.args.get("folder_id") or None
        query = request.args.get("query") or None
        files = engine.drive.list_files(folder_id=folder_id, query=query, page_size=100)
        return _ok(files)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/drive/files/<file_id>", methods=["GET"])
def get_drive_file(file_id):
    engine, error = _engine_or_500()
    if error:
        return error
    if not getattr(engine, "drive", None) or not engine.drive.is_connected():
        return _err("Drive not connected", 400)
    try:
        info = engine.drive.get_file_url(file_id)
        if not info:
            return _err("File not found", 404)
        return _ok(info)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/drive/files/<file_id>/validate", methods=["GET"])
def validate_drive_file(file_id):
    engine, error = _engine_or_500()
    if error:
        return error
    if not getattr(engine, "drive", None) or not engine.drive.is_connected():
        return _err("Drive not connected", 400)
    try:
        ok = engine.drive.validate_link(file_id)
        return _ok({"valid": ok})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/drive/upload", methods=["POST"])
def upload_drive_file():
    engine, error = _engine_or_500()
    if error:
        return error
    if not getattr(engine, "drive", None) or not engine.drive.is_connected():
        return _err("Drive not connected", 400)
    try:
        if "file" not in request.files:
            return _err("No file provided", 400)
        file = request.files["file"]
        if file.filename == "":
            return _err("Empty filename", 400)
        folder_id = request.form.get("folder_id") or None
        tmp_dir = tempfile.mkdtemp()
        tmp_path = os.path.join(tmp_dir, file.filename)
        file.save(tmp_path)
        result = engine.drive.upload_file(tmp_path, filename=file.filename, folder_id=folder_id)
        if not result:
            return _err("Upload failed", 500)
        return _ok(result)
    except Exception as e:
        return _err(str(e), 500)


# ── Auth / Connections ────────────────────────────────────────────────────────
@app.route("/api/auth/status", methods=["GET"])
def auth_status():
    try:
        return _ok({
            "gmail": _gmail.is_connected() if _gmail else False,
            "calendar": _engine.calendar.is_connected() if _engine and getattr(_engine, "calendar", None) else False,
            "drive": _engine.drive.is_connected() if _engine and getattr(_engine, "drive", None) else False,
            "last_error": _last_connect_error,
        })
    except Exception as e:
        return _err(str(e), 500)


# ── Templates (read-only for Phase 1) ─────────────────────────────────────────
@app.route("/api/templates", methods=["GET"])
def list_templates():
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        templates = engine.get_templates()
        status = engine.get_template_status()
        return _ok({"templates": templates, "status": status})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/templates/<seq>/<int:day>", methods=["GET"])
def get_template(seq, day):
    try:
        tmpl = _db.template_get(seq, day)
        if not tmpl:
            return _err("Template not found", 404)
        return _ok(tmpl)
    except Exception as e:
        return _err(str(e), 500)


# ── Pools ─────────────────────────────────────────────────────────────────────
@app.route("/api/pools", methods=["GET"])
def list_pools():
    """Return all sub-pool tags and lead counts from the unified pool."""
    try:
        rows = _db.execute(
            """
            SELECT sub_pool, COUNT(*) as cnt FROM recipients r
            WHERE r.sequence_id='leads' AND r.batched=0
            AND NOT EXISTS (SELECT 1 FROM blacklist b WHERE b.email=r.email)
            GROUP BY sub_pool
            """
        ).fetchall()
        pools = [{"name": r["sub_pool"] or "(no sub-pool)", "count": r["cnt"]} for r in rows]
        total = sum(p["count"] for p in pools)
        return _ok({"pools": pools, "total": total})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/pools/count", methods=["GET"])
def pool_count():
    sub_pool = request.args.get("sub_pool") or None
    try:
        count = _engine.get_pool_count(sub_pool) if _engine else _db.get_pool_count(sub_pool)
        return _ok({"count": count})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/pools/stats", methods=["GET"])
def pool_stats():
    sub_pool = request.args.get("sub_pool") or None
    try:
        if sub_pool:
            return _ok({sub_pool: _db.pool_stats(sub_pool)})
        out = {"all": _db.pool_stats("leads")}
        # Also return per-tag stats
        tags = _db.execute("SELECT DISTINCT sub_pool FROM recipients WHERE sequence_id='leads'").fetchall()
        for r in tags:
            tag = r[0] or "(no sub-pool)"
            out[tag] = _db.pool_stats(tag)
        return _ok(out)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/pools/<sub_pool>/reset-recampaign", methods=["POST"])
def reset_pool_recampaign(sub_pool):
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        result = engine.reset_pool(sub_pool)
        return _ok(result)
    except Exception as e:
        return _err(str(e), 500)


# ── Batches (mutations) ───────────────────────────────────────────────────────
@app.route("/api/batches", methods=["POST"])
def create_batch():
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        data = request.get_json() or {}
        pull_from = data.get("pull_from") or None
        sequence_id = data.get("sequence_id") or None
        result = engine.create_batch_from_pool(
            name=data.get("name", "New Campaign"),
            sequence_id=sequence_id,
            source_sequence=pull_from,
            batch_size=int(data.get("batch_size", 10) or 10),
            day_offset=int(data.get("day_offset", 1) or 1),
            scheduled_at=data.get("scheduled_at") or None,
            timezone=data.get("timezone", "Asia/Kolkata"),
        )
        if not result.get("success"):
            return _err(result.get("error", "Batch creation failed"), 400)

        return _ok(result)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/batches/<int:batch_id>/start", methods=["POST"])
def start_batch(batch_id):
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        batch = _db.batch_get(batch_id)
        if not batch:
            return _err("Batch not found", 404)
        if batch.get("sequence_id") in (None, "", "unassigned"):
            return _err("Assign a sequence before starting the batch", 400)
        data = request.get_json() or {}
        sequence_id = data.get("sequence_id")
        if sequence_id and sequence_id not in ("leads", "unassigned") and sequence_id in SEQUENCES:
            assign = engine.assign_sequence_to_batch(batch_id, sequence_id)
            if not assign.get("success"):
                return _err(assign.get("error", "Sequence assignment failed"), 400)
        # Force-start: clear scheduled time so it takes the send path, not draft path
        _db.execute("UPDATE batches SET scheduled_at=NULL WHERE id=?", (batch_id,))
        _db.batch_update_status(batch_id, "running")
        return _ok({"batch_id": batch_id, "status": "running"})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/batches/<int:batch_id>/pause", methods=["POST"])
def pause_batch(batch_id):
    try:
        batch = _db.batch_get(batch_id)
        if not batch:
            return _err("Batch not found", 404)
        _db.batch_update_status(batch_id, "paused")
        return _ok({"batch_id": batch_id, "status": "paused"})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/batches/<int:batch_id>/clone", methods=["POST"])
def clone_batch(batch_id):
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        data = request.get_json() or {}
        batch = _db.batch_get(batch_id)
        if not batch:
            return _err("Batch not found", 404)
        source_name = batch.get("name") or str(batch_id)
        # Strip day suffix to get family name
        if source_name.endswith("-D1"):
            source_name = source_name[:-3]
        new_name = data.get("new_name") or f"Clone-{source_name}"
        result = engine.clone_family(source_name, new_name, sub_pool=data.get("sub_pool"))
        if not result.get("success"):
            return _err(result.get("error", "Clone failed"), 400)
        return _ok(result)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/batches/<int:batch_id>", methods=["DELETE"])
def delete_batch(batch_id):
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        result = engine.delete_batch(batch_id)
        if not result.get("success"):
            return _err(result.get("error", "Delete failed"), 400)
        return _ok(result)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/batches/<int:batch_id>/report", methods=["GET"])
def batch_report(batch_id):
    try:
        batch = _db.batch_get(batch_id)
        if not batch:
            return _err("Batch not found", 404)
        counts = _db.batch_count_by_status(batch_id)
        recipients = _db.batch_get_recipients(batch_id)
        return _ok({"batch": batch, "counts": counts, "recipients": recipients})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/batches/pipelines", methods=["GET"])
def list_pipelines():
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        sequence_id = request.args.get("sequence_id") or None
        pipelines = engine.get_all_batch_pipelines(sequence_id)
        return _ok(pipelines)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/batches/<int:batch_id>/pipeline", methods=["GET"])
def get_batch_pipeline(batch_id):
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        pipeline = engine.get_batch_pipeline(batch_id)
        return _ok(pipeline)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/batches/<int:batch_id>/family", methods=["DELETE"])
def delete_family(batch_id):
    """Soft-delete a whole campaign family (root + day batches)."""
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        pipeline = engine.get_batch_pipeline(batch_id)
        root_id = pipeline.get("root_batch_id", batch_id)
        rows = _db.execute("SELECT id, status FROM batches WHERE parent_batch_id=? OR id=?", (root_id, root_id)).fetchall()
        returned = 0
        deleted = 0
        for row in rows:
            if row["status"] == "running":
                continue
            res = engine.delete_batch(row["id"])
            if res.get("success"):
                returned += res.get("returned", 0)
                deleted += 1
        return _ok({"deleted": deleted, "returned": returned})
    except Exception as e:
        return _err(str(e), 500)


# ── Leads / Import ────────────────────────────────────────────────────────────
def _preview_rows_from_path(path, ext):
    rows = []
    columns = []
    if ext == ".csv":
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            raw = list(reader)
    else:
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb.active
        raw = [[str(c.value) if c.value is not None else "" for c in row] for row in ws.iter_rows()]

    if not raw:
        return [], []

    # Detect header row
    first = [c.strip().lower() for c in raw[0]]
    has_header = "email" in first or "e-mail" in first
    if has_header:
        columns = [c.strip() for c in raw[0]]
        data_rows = raw[1:]
    else:
        columns = [f"col{i+1}" for i in range(len(raw[0]))]
        data_rows = raw

    for r in data_rows:
        if not any(c.strip() for c in r):
            continue
        row_dict = {}
        for i, col in enumerate(columns):
            row_dict[col] = r[i].strip() if i < len(r) else ""
        rows.append(row_dict)
    return rows, columns


@app.route("/api/leads/import/file", methods=["POST"])
def import_file():
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        if "file" not in request.files:
            return _err("No file provided", 400)
        file = request.files["file"]
        if file.filename == "":
            return _err("Empty filename", 400)

        sequence_id = request.form.get("sequence_id", "leads")
        sub_pool = request.form.get("sub_pool") or None
        preview = request.form.get("preview", "false").lower() in ("1", "true", "yes")

        ext = Path(file.filename).suffix.lower()
        if ext not in [".csv", ".xlsx", ".xls"]:
            return _err("Only CSV or Excel files allowed", 400)

        tmp_dir = tempfile.mkdtemp()
        tmp_path = os.path.join(tmp_dir, f"{uuid.uuid4()}{ext}")
        file.save(tmp_path)

        if preview:
            rows, columns = _preview_rows_from_path(tmp_path, ext)
            result = {"success": True, "rows": rows, "columns": columns, "imported": 0}
        else:
            if ext == ".csv":
                result = engine.smart_import(tmp_path, sequence_id=sequence_id, sub_pool=sub_pool)
            else:
                added, updated = engine.import_recipients(tmp_path, sequence_id=sequence_id, sub_pool=sub_pool)
                result = {"success": True, "imported": added, "updated": updated}

        try:
            os.remove(tmp_path)
            os.rmdir(tmp_dir)
        except Exception:
            pass

        return _ok(result)
    except Exception as e:
        return _err(str(e), 500)


def _normalize_lead_row(row, sequence_id="leads", sub_pool=None):
    out = {
        "email": "",
        "name": "",
        "org": "",
        "sequence_id": sequence_id,
        "sub_pool": sub_pool,
    }
    for k, v in row.items():
        kl = k.lower().strip()
        if kl in ("email", "e-mail"):
            out["email"] = str(v).lower().strip()
        elif kl == "name":
            out["name"] = str(v).strip()
        elif kl in ("org", "company", "organization"):
            out["org"] = str(v).strip()
        else:
            out[k] = v

    # Syntax + MX validation. On validator outage, treat email as valid so imports
    # are never blocked by a DNS failure.
    if out["email"]:
        try:
            if validate_email is not None:
                ok, reason = validate_email(out["email"])
                if not ok:
                    out["status"] = reason
        except Exception:
            pass

    return out


@app.route("/api/leads/import/paste", methods=["POST"])
def import_paste_preview():
    try:
        data = request.get_json() or {}
        raw = data.get("text") or data.get("emails", "")
        sequence_id = data.get("sequence_id", "leads")
        sub_pool = data.get("sub_pool") or None

        reader = csv.reader(io.StringIO(raw.strip()))
        raw_rows = [r for r in reader if any(c.strip() for c in r)]
        if not raw_rows:
            return _ok({"rows": [], "columns": []})

        first = [c.strip().lower() for c in raw_rows[0]]
        has_header = "email" in first or "e-mail" in first
        if has_header:
            columns = [c.strip() for c in raw_rows[0]]
            data_rows = raw_rows[1:]
        else:
            columns = [f"col{i+1}" for i in range(len(raw_rows[0]))]
            data_rows = raw_rows

        rows = []
        for r in data_rows:
            row_dict = {columns[i]: (r[i].strip() if i < len(r) else "") for i in range(len(columns))}
            lead = _normalize_lead_row(row_dict, sequence_id, sub_pool)
            if lead["email"]:
                # Validation reasons (bad-syntax / no-mx) are set by the normalizer.
                # Do not overwrite them; otherwise mark ready / blacklisted / duplicate.
                if lead.get("status") not in ("bad-syntax", "no-mx"):
                    lead["status"] = "ready"
                    if _db.blacklist_has(lead["email"]):
                        lead["status"] = "blacklisted"
                    elif _db.recipient_exists(lead["email"]):
                        lead["status"] = "duplicate"
                rows.append(lead)

        return _ok({"rows": rows, "columns": list(rows[0].keys()) if rows else columns})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/leads/import/confirm", methods=["POST"])
def import_paste_confirm():
    try:
        data = request.get_json() or {}
        rows = data.get("rows") or data.get("leads", [])
        sequence_id = data.get("sequence_id", "leads")
        sub_pool = data.get("sub_pool") or None
        imported = 0
        skipped = 0
        for row in rows:
            lead = _normalize_lead_row(row, sequence_id, sub_pool)
            email = lead["email"]
            if not email or "@" not in email or lead.get("status") in ("bad-syntax", "no-mx"):
                skipped += 1
                continue
            if _db.blacklist_has(email) or _db.recipient_exists(email):
                skipped += 1
                continue
            _db.recipient_add(
                sequence_id=lead["sequence_id"],
                email=email,
                name=lead["name"],
                org=lead["org"],
                sub_pool=lead["sub_pool"],
            )
            imported += 1
        return _ok({"imported": imported, "skipped": skipped})
    except Exception as e:
        return _err(str(e), 500)


# ── Templates (mutations) ─────────────────────────────────────────────────────
@app.route("/api/sequences", methods=["GET"])
def list_sequences():
    try:
        sequences = {
            sid: {"days": cfg["days"], "label": sid.upper()}
            for sid, cfg in SEQUENCES.items()
        }
        return _ok(sequences)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/templates/<seq>/<int:day>", methods=["PUT"])
def update_template(seq, day):
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        data = request.get_json() or {}
        existing = _db.template_get(seq, day) or {}
        if engine.is_template_locked(seq, day) and not data.get("force"):
            return _err("Template is locked", 409)
        subject = data.get("subject", existing.get("subject", ""))
        html_body = data.get("html_body", existing.get("html_body", ""))
        text_body = data.get("text_body", existing.get("text_body", ""))
        subject_b = data.get("subject_b", existing.get("subject_b", ""))
        ab_test = data.get("ab_test", existing.get("ab_test", 0))
        ab_split = data.get("ab_split", existing.get("ab_split", 0.5))
        fmt = data.get("format", existing.get("format", "html"))
        source = data.get("source") or existing.get("source") or "web_ui"
        _db.template_put(
            seq, day, subject, html_body, source,
            text_body=text_body,
            subject_b=subject_b,
            ab_test=ab_test,
            ab_split=ab_split,
            format=fmt
        )
        return _ok({"sequence_id": seq, "day": day, "saved": True})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/templates/<seq>/<int:day>/test", methods=["POST"])
def test_send_template(seq, day):
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        data = request.get_json() or {}
        email = data.get("email")
        if not email:
            return _err("Email required", 400)
        ok = engine.test_send(
            email, seq, day,
            format=data.get("format"),
            subject=data.get("subject"),
            body=data.get("body"),
        )
        return _ok({"sent": ok})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/templates/<seq>/trial", methods=["POST"])
def trial_send_sequence(seq):
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        data = request.get_json() or {}
        email = data.get("email")
        if not email:
            return _err("Email required", 400)
        result = engine.trial_send(email, seq, name=data.get("name", ""), org=data.get("org", ""), format=data.get("format"))
        return _ok(result)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/templates/<seq>/<int:day>/generate", methods=["POST"])
def generate_template(seq, day):
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        data = request.get_json() or {}
        create_draft = data.get("create_draft", True)
        if engine.is_template_locked(seq, day) and not data.get("force"):
            return _err("Template is locked", 409)
        ok = engine.save_generated_template(seq, day, create_draft=create_draft)
        if not ok:
            return _err("Template generation failed", 400)
        tmpl = _db.template_get(seq, day)
        return _ok({"generated": True, "template": tmpl})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/templates/generate-missing", methods=["POST"])
def generate_missing_templates():
    engine, error = _engine_or_500()
    if error:
        return error
    if not getattr(engine, "gmail", None) or not engine.gmail.is_connected():
        return _err("Gmail not connected", 400)
    try:
        data = request.get_json() or {}
        result = engine.create_missing_drafts()
        return _ok(result)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/templates/<seq>/<int:day>/lock", methods=["POST"])
def lock_template(seq, day):
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        engine.lock_template(seq, day)
        return _ok({"locked": True})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/templates/<seq>/<int:day>/lock", methods=["DELETE"])
def unlock_template(seq, day):
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        engine.unlock_template(seq, day)
        return _ok({"locked": False})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/templates/lock-all", methods=["POST"])
def lock_all_templates():
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        result = engine.lock_templates()
        return _ok(result)
    except Exception as e:
        return _err(str(e), 500)


# ── Desktop integration ───────────────────────────────────────────────────────
_shutdown_callback = None


@app.route("/api/shutdown", methods=["POST"])
def shutdown():
    """Shutdown request from the desktop wrapper.

    Werkzeug no longer exposes request.environ['werkzeug.server.shutdown'],
    so we rely on the desktop wrapper's callback to terminate the process.
    """
    if _shutdown_callback:
        try:
            _shutdown_callback()
        except Exception:
            pass
        return _ok({"shutdown": True})
    return _err("No shutdown callback registered", 501)


@app.route("/api/state", methods=["GET", "POST"])
def app_state():
    from state import load_state, update_state
    if request.method == "POST":
        data = request.get_json() or {}
        update_state(data)
    return _ok(load_state())


@app.route("/api/settings/autostart", methods=["POST"])
def toggle_autostart():
    from autostart import add_to_startup, is_autostart_enabled, remove_from_startup
    data = request.get_json() or {}
    enabled = bool(data.get("enabled"))
    target = PROJECT_ROOT / "desktop.py"
    if enabled:
        add_to_startup(target)
    else:
        remove_from_startup()
    return _ok({"enabled": is_autostart_enabled()})


@app.route("/api/export", methods=["POST"])
def export_campaign():
    """Export campaign state to Markdown."""
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        engine.export_campaign_state()
        return _ok({"exported": True, "file": "campaign_state.md"})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/settings/campaign", methods=["GET", "POST"])
def campaign_settings():
    """Get or update campaign-level settings stored in meta."""
    keys = ["brief_email", "default_sender", "pause_school", "pause_csr", "pause_csr_wsl_5",
            "send_gap_seconds", "daily_send_cap"]
    if request.method == "POST":
        data = request.get_json() or {}
        for key in keys:
            if key in data:
                _db.set_meta(key, data[key])
        return _ok({"saved": True})

    try:
        values = {key: _db.get_meta(key) for key in keys}
        # Convert pause flags to booleans
        for key in keys:
            if key.startswith("pause_"):
                values[key] = str(values.get(key)).lower() in ("1", "true", "yes")
        return _ok(values)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/dashboard/send-stats", methods=["GET"])
def send_stats():
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        return _ok(engine.get_send_stats())
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/settings/deliverability", methods=["GET"])
def deliverability_check():
    """Live DNS check for SPF / DKIM / DMARC on the sending domain."""
    import subprocess, re
    domain = (_db.get_meta("sender_domain") or "robopirate.in").strip()

    def txt_records(name):
        try:
            out = subprocess.run(
                ["nslookup", "-type=TXT", name], capture_output=True, text=True, timeout=10
            )
            return out.stdout or ""
        except Exception:
            return ""

    try:
        root_txt = txt_records(domain)
        spf_found = "v=spf1" in root_txt and "_spf.google.com" in root_txt
        dkim_txt = txt_records(f"google._domainkey.{domain}")
        dkim_found = "v=DKIM1" in dkim_txt or "k=rsa" in dkim_txt
        dmarc_txt = txt_records(f"_dmarc.{domain}")
        dmarc_found = "v=DMARC1" in dmarc_txt
        checks = [
            {
                "name": "SPF",
                "ok": spf_found,
                "fix": f"Add TXT record @{domain} → v=spf1 include:_spf.google.com ~all",
            },
            {
                "name": "DKIM",
                "ok": dkim_found,
                "fix": "Google Workspace Admin → Apps → Gmail → Authenticate email → generate DKIM record and add it to DNS",
            },
            {
                "name": "DMARC",
                "ok": dmarc_found,
                "fix": f"Add TXT record _dmarc.{domain} → v=DMARC1; p=quarantine; rua=mailto:dmarc@{domain}; pct=100",
            },
        ]
        return _ok({"domain": domain, "checks": checks, "all_ok": all(c["ok"] for c in checks)})
    except Exception as e:
        return _err(str(e), 500)


# ── Replies ───────────────────────────────────────────────────────────────────
@app.route("/api/replies", methods=["GET"])
def get_replies():
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        refresh = request.args.get("refresh", "false").lower() in ("1", "true", "yes")
        if refresh and getattr(engine, "gmail", None) and engine.gmail.is_connected():
            try:
                engine.scan_replies(days_back=3)
            except Exception as e:
                print(f"[Replies] Scan warning: {e}")

        status = request.args.get("status") or None
        sentiment = request.args.get("sentiment") or None
        search = request.args.get("search") or None
        replies = _db.get_replies_with_drafts(filter_status=status, filter_sentiment=sentiment, search=search)
        for r in replies:
            r["date"] = r.get("received_at", "")
            r["snippet"] = (r.get("body") or "")[:160]
        return _ok(replies)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/replies/count", methods=["GET"])
def get_replies_count():
    try:
        total = _db.execute("SELECT COUNT(*) FROM replies").fetchone()[0]
        pending = _db.execute("SELECT COUNT(*) FROM replies WHERE status='pending'").fetchone()[0]
        drafted = _db.execute("SELECT COUNT(*) FROM replies WHERE status='drafted'").fetchone()[0]
        handled = _db.execute("SELECT COUNT(*) FROM replies WHERE status='handled'").fetchone()[0]
        by_sentiment = {}
        for row in _db.execute("SELECT sentiment, COUNT(*) FROM replies WHERE sentiment IS NOT NULL GROUP BY sentiment").fetchall():
            by_sentiment[row[0]] = row[1]
        return _ok({"total": total, "pending": pending, "drafted": drafted, "handled": handled, "by_sentiment": by_sentiment})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/replies/<int:reply_id>/handled", methods=["POST"])
def mark_reply_handled(reply_id):
    try:
        _db.mark_reply_handled(reply_id)
        return _ok({"handled": True})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/replies/<int:reply_id>/draft", methods=["POST"])
def draft_reply(reply_id):
    """Generate an AI draft for a received reply."""
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        result = engine.generate_reply_draft(reply_id)
        if not result.get("success"):
            return _err(result.get("error", "Draft generation failed"), 400)
        _db.execute("UPDATE replies SET status='drafted' WHERE id=?", (reply_id,))
        _db.commit()
        return _ok(result)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/replies/<int:reply_id>/send-draft", methods=["POST"])
def send_draft_reply(reply_id):
    """Send a previously drafted reply."""
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        result = engine.send_reply_draft(reply_id)
        if not result.get("success"):
            return _err(result.get("error", "Send failed"), 400)
        return _ok(result)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/replies/<int:reply_id>/update-draft", methods=["POST"])
def update_draft_reply(reply_id):
    """Update the body of a drafted reply."""
    try:
        data = request.get_json() or {}
        new_body = data.get("body", "")

        reply = _db.execute("SELECT * FROM replies WHERE id=?", (reply_id,)).fetchone()
        if not reply:
            return _err("Reply not found", 404)

        _db.execute("UPDATE replies SET draft_html=? WHERE id=?", (new_body, reply_id))
        _db.commit()
        return _ok({"updated": True})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/replies/<int:reply_id>/blacklist", methods=["POST"])
def blacklist_from_reply(reply_id):
    """Blacklist the sender of a reply."""
    engine, error = _engine_or_500()
    if error:
        return error
    try:
        result = engine.blacklist_from_reply(reply_id)
        if not result.get("success"):
            return _err(result.get("error", "Blacklist failed"), 400)
        return _ok(result)
    except Exception as e:
        return _err(str(e), 500)


# ── Blacklist ─────────────────────────────────────────────────────────────────
@app.route("/api/blacklist", methods=["GET"])
def get_blacklist():
    try:
        return _ok(_db.blacklist_get_all())
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/blacklist", methods=["POST"])
def add_to_blacklist():
    try:
        data = request.get_json() or {}
        emails = data.get("emails", [])
        reason = data.get("reason", "manual")
        added = 0
        skipped = 0
        for email in emails:
            email = (email or "").lower().strip()
            if not email or "@" not in email:
                skipped += 1
                continue
            _db.blacklist_add(email, reason)
            added += 1
        return _ok({"added": added, "skipped": skipped, "total": _db.execute("SELECT COUNT(*) FROM blacklist").fetchone()[0]})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/blacklist/<path:email>", methods=["DELETE"])
def remove_from_blacklist(email):
    try:
        _db.blacklist_remove(email)
        return _ok({"removed": True})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/blacklist/import", methods=["POST"])
def import_blacklist():
    try:
        if "file" not in request.files:
            return _err("No file provided", 400)
        file = request.files["file"]
        if file.filename == "" or not file.filename.lower().endswith(".csv"):
            return _err("Only CSV files allowed", 400)

        import io
        stream = io.TextIOWrapper(file.stream, encoding="utf-8-sig")
        reader = csv.reader(stream)
        added = 0
        skipped = 0
        for row in reader:
            if not row:
                continue
            email = (row[0] or "").lower().strip()
            if not email or "@" not in email or email.lower() == "email":
                skipped += 1
                continue
            _db.blacklist_add(email, "csv_import")
            added += 1
        return _ok({"added": added, "skipped": skipped, "total": _db.execute("SELECT COUNT(*) FROM blacklist").fetchone()[0]})
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/blacklist/scan", methods=["POST"])
def scan_bounces():
    """Run a deep bounce scan and return results."""
    engine, error = _engine_or_500()
    if error:
        return error
    if not getattr(engine, "gmail", None) or not engine.gmail.is_connected():
        return _err("Gmail not connected", 400)
    try:
        data = request.get_json() or {}
        days = int(data.get("days", 15))
        result = engine.deep_bounce_scan(days=days)
        return _ok(result)
    except Exception as e:
        return _err(str(e), 500)


# ── External preview ──────────────────────────────────────────────────────────
@app.route("/api/preview", methods=["POST"])
def open_preview():
    """Write the current email content to a temp HTML file and open it in the system browser."""
    try:
        data = request.get_json() or {}
        subject = (data.get("subject") or "No subject")[:500]
        body = (data.get("body") or "")[:100000]
        fmt = data.get("format", "html")

        if fmt == "html":
            body_html = body
        else:
            body_html = f"<pre style='white-space:pre-wrap;font-family:Segoe UI,Arial,sans-serif;font-size:14px;color:#0F172A;background:#F8FAFC;padding:20px;margin:0;'>{escape(body)}</pre>"

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Preview: {escape(subject)}</title>
    <style>
        body {{ font-family: Segoe UI, Arial, sans-serif; background: #F8FAFC; color: #0F172A; padding: 20px; margin: 0; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #FFFFFF; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); padding: 30px; }}
        .subject {{ font-size: 18px; font-weight: 600; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #E2E8F0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="subject">{escape(subject)}</div>
        <div>{body_html}</div>
    </div>
</body>
</html>"""

        tmp_dir = Path(tempfile.gettempdir()) / "raj_previews"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        tmp_path = tmp_dir / f"preview_{uuid.uuid4().hex}.html"
        tmp_path.write_text(html, encoding="utf-8")

        def open_browser():
            try:
                webbrowser.open(f"file:///{tmp_path}")
            except Exception as e:
                print(f"[Preview] webbrowser.open failed: {e}")

        threading.Thread(target=open_browser, daemon=True).start()
        return _ok({"opened": True, "path": str(tmp_path)})
    except Exception as e:
        return _err(str(e), 500)


# ── Google OAuth connect triggers ─────────────────────────────────────────────
@app.route("/api/connect/<service>", methods=["POST"])
def connect_google(service):
    engine, error = _engine_or_500()
    if error:
        return error
    valid = {"gmail", "calendar", "drive"}
    if service not in valid:
        return _err(f"Invalid service: {service}", 400)

    def cb(success, error):
        global _last_connect_error
        _last_connect_error[service] = {"success": success, "error": error}
        print(f"[Connect] {service}: success={success} error={error}")

    try:
        method = getattr(engine, f"connect_{service}")
        method(callback=cb)
        return _ok({"started": True, "service": service})
    except Exception as e:
        _last_connect_error[service] = {"success": False, "error": str(e)}
        return _err(str(e), 500)


# ── Main entry for Flask dev server ───────────────────────────────────────────
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="127.0.0.1", port=5555, threads=4)
