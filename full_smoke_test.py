"""Full API smoke test for Raj desktop."""

import requests, sys

BASE = "http://127.0.0.1:5555"

def get(path, expected=200):
    r = requests.get(BASE + path, timeout=10)
    assert r.status_code == expected, f"GET {path}: {r.status_code} {r.text[:200]}"
    try:
        return r.json()
    except Exception:
        return r.text

def post(path, data=None, expected=200):
    r = requests.post(BASE + path, json=data, timeout=10)
    assert r.status_code == expected, f"POST {path}: {r.status_code} {r.text[:200]}"
    return r.json()

def put(path, data=None, expected=200):
    r = requests.put(BASE + path, json=data, timeout=10)
    assert r.status_code == expected, f"PUT {path}: {r.status_code} {r.text[:200]}"
    return r.json()

def check(name, fn):
    try:
        fn()
        print(f"[OK] {name}")
        return True
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        return False

def main():
    ok = []
    ok.append(check("Health", lambda: get("/api/health")))
    ok.append(check("Auth status", lambda: get("/api/auth/status")))
    ok.append(check("Dashboard summary", lambda: get("/api/dashboard/summary")))
    ok.append(check("Dashboard pipeline", lambda: get("/api/dashboard/pipeline")))
    ok.append(check("Dashboard batches", lambda: get("/api/dashboard/batches")))
    ok.append(check("List batches", lambda: get("/api/batches")))
    ok.append(check("List pipelines", lambda: get("/api/batches/pipelines")))
    ok.append(check("List pools", lambda: get("/api/pools?sequence_id=leads")))
    ok.append(check("Pool count", lambda: get("/api/pools/count?sequence_id=leads")))
    ok.append(check("List templates", lambda: get("/api/templates")))
    ok.append(check("Get template school D1", lambda: get("/api/templates/school/1")))
    ok.append(check("List sequences", lambda: get("/api/sequences")))
    ok.append(check("Replies", lambda: get("/api/replies")))
    ok.append(check("Blacklist", lambda: get("/api/blacklist")))
    ok.append(check("Engine status", lambda: get("/api/engine/status")))
    ok.append(check("Audit log", lambda: get("/api/audit-log?limit=5")))
    ok.append(check("Analytics summary", lambda: get("/api/analytics/summary")))
    ok.append(check("Analytics daily", lambda: get("/api/analytics/daily")))
    ok.append(check("Analytics top links", lambda: get("/api/analytics/top-links")))
    ok.append(check("Analytics activity", lambda: get("/api/analytics/activity")))
    ok.append(check("Campaign settings", lambda: get("/api/settings/campaign")))
    ok.append(check("State", lambda: get("/api/state")))

    # mutations that should be safe/no-ops when not authenticated
    ok.append(check("Pause engine (idempotent)", lambda: post("/api/engine/pause")))
    ok.append(check("Resume engine (idempotent)", lambda: post("/api/engine/resume")))
    ok.append(check("Emergency stop all", lambda: post("/api/emergency", {"action": "stop", "target": "all"})))
    ok.append(check("Emergency resume all", lambda: post("/api/emergency", {"action": "resume", "target": "all"})))

    passed = sum(ok)
    total = len(ok)
    print(f"\n{passed}/{total} checks passed")
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
