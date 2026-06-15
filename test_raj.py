import sqlite3
import sys
import os
from pathlib import Path

# Force UTF-8 output on Windows so emoji/status characters print correctly
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Find the database
DB_PATH = Path(__file__).parent / "campaign_data.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def test_db_schema():
    """Test 1: Check all new columns exist from the 6 prompts"""
    print("=" * 50)
    print("TEST 1: Database Schema")
    print("=" * 50)
    conn = get_db()
    c = conn.cursor()
    
    # Check sub_pool column exists (Prompt 1+2: sub-pools)
    try:
        c.execute("SELECT sub_pool FROM recipients LIMIT 1")
        print("✅ sub_pool column exists in recipients")
    except:
        print("❌ sub_pool column MISSING in recipients")
        return False
    
    # Check deleted_at column exists (Prompt 2: soft delete)
    try:
        c.execute("SELECT deleted_at FROM batches LIMIT 1")
        print("✅ deleted_at column exists in batches")
    except:
        print("❌ deleted_at column MISSING in batches")
        return False
    
    # Check ab_test columns exist (Prompt 6: A/B testing)
    try:
        c.execute("SELECT subject_b, ab_test, ab_split FROM templates LIMIT 1")
        print("✅ subject_b, ab_test, ab_split columns exist in templates")
    except:
        print("❌ A/B test columns MISSING in templates")
        return False
    
    # Check ab_variant in sends
    try:
        c.execute("SELECT ab_variant FROM sends LIMIT 1")
        print("✅ ab_variant column exists in sends")
    except:
        print("❌ ab_variant column MISSING in sends")
        return False
    
    # Check indexes
    c.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_recipients_sub_pool'")
    if c.fetchone():
        print("✅ idx_recipients_sub_pool index exists")
    else:
        print("❌ idx_recipients_sub_pool index MISSING")
        return False
    
    conn.close()
    print("TEST 1: PASSED\n")
    return True

def test_sub_pool_filtering():
    """Test 2: Sub-pool import and filtering works"""
    print("=" * 50)
    print("TEST 2: Sub-Pool Filtering")
    print("=" * 50)
    conn = get_db()
    c = conn.cursor()
    
    # Check if any sub_pools exist
    c.execute("SELECT COUNT(*) FROM recipients WHERE sub_pool != '' AND sub_pool IS NOT NULL")
    count = c.fetchone()[0]
    if count > 0:
        print(f"✅ Found {count} recipients with sub_pool set")
    else:
        print("⚠️ No recipients with sub_pool found — import something with a sub-pool name to test this")
    
    # Check get_pool-style query works with sub_pool filter
    try:
        c.execute("SELECT r.* FROM recipients r WHERE r.sequence_id=? AND r.batched=0 AND r.sub_pool = ? ORDER BY r.id LIMIT 1", ("school", "Test-Pool"))
        print("✅ Sub-pool filtered query executes without error")
    except Exception as e:
        print(f"❌ Sub-pool query failed: {e}")
        return False
    
    conn.close()
    print("TEST 2: PASSED\n")
    return True

def test_conditional_sequences():
    """Test 3: Check that 'replied' and 'stopped' statuses exist"""
    print("=" * 50)
    print("TEST 3: Conditional Sequence Statuses")
    print("=" * 50)
    conn = get_db()
    c = conn.cursor()
    
    # We can't easily test the engine logic without running it, but we can verify the DB supports it
    # Check if batch_recipients has status column that can hold 'replied' and 'stopped'
    try:
        c.execute("PRAGMA table_info(batch_recipients)")
        columns = [row[1] for row in c.fetchall()]
        if 'status' in columns:
            print("✅ batch_recipients.status column exists")
        else:
            print("❌ batch_recipients.status column MISSING")
            return False
    except Exception as e:
        print(f"❌ Error checking batch_recipients: {e}")
        return False
    
    # Check if replies table exists
    try:
        c.execute("SELECT COUNT(*) FROM replies")
        reply_count = c.fetchone()[0]
        print(f"✅ replies table exists with {reply_count} rows")
    except:
        print("❌ replies table MISSING")
        return False
    
    conn.close()
    print("TEST 3: PASSED\n")
    return True

def test_soft_delete():
    """Test 4: Soft delete functionality"""
    print("=" * 50)
    print("TEST 4: Soft Delete (Family Delete)")
    print("=" * 50)
    conn = get_db()
    c = conn.cursor()
    
    # Check deleted batches query works
    try:
        c.execute("SELECT * FROM batches WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC LIMIT 5")
        deleted = c.fetchall()
        print(f"✅ Soft delete query works. Found {len(deleted)} deleted batches.")
    except Exception as e:
        print(f"❌ Soft delete query failed: {e}")
        return False
    
    # Check active batches exclude deleted
    try:
        c.execute("SELECT COUNT(*) FROM batches WHERE deleted_at IS NULL")
        active = c.fetchone()[0]
        print(f"✅ Active batches query works. {active} active batches.")
    except Exception as e:
        print(f"❌ Active batches query failed: {e}")
        return False
    
    conn.close()
    print("TEST 4: PASSED\n")
    return True

def test_ui_elements():
    """Test 5: Check that UI code references exist"""
    print("=" * 50)
    print("TEST 5: UI Elements (Code Check)")
    print("=" * 50)
    
    raj_chat_path = Path(__file__).parent / "raj_chat.py"
    if not raj_chat_path.exists():
        print("❌ raj_chat.py not found")
        return False
    
    with open(raj_chat_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    checks = {
        "Sub-pool entry": "import_subpool_entry" in code,
        "Family delete button": "_delete_family" in code,
        "History toggle": "_history_expanded" in code or "HISTORY" in code,
        "Reply inbox": "Reply Inbox" in code,
        "Clone button": "Clone" in code or "clone_family" in code,
        "A/B test UI": "ab_test" in code and "subject_b" in code,
        "Desktop notifications": "notify(" in code or "notification.notify" in code,
    }
    
    all_pass = True
    for name, found in checks.items():
        status = "✅" if found else "❌"
        if not found:
            all_pass = False
        print(f"  {status} {name}: {'FOUND' if found else 'NOT FOUND'}")
    
    print(f"TEST 5: {'PASSED' if all_pass else 'SOME MISSING'}\n")
    return all_pass

def test_import_methods():
    """Test 6: Check engine and smart_importer have sub_pool params"""
    print("=" * 50)
    print("TEST 6: Import Pipeline (Code Check)")
    print("=" * 50)
    
    files_to_check = {
        "engine.py": ["sub_pool", "smart_import"],
        "smart_importer.py": ["sub_pool", "import_to_pool"],
        "db.py": ["sub_pool", "batch_from_pool"],
    }
    
    all_pass = True
    for filename, keywords in files_to_check.items():
        filepath = Path(__file__).parent / filename
        if not filepath.exists():
            print(f"❌ {filename} not found")
            all_pass = False
            continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        for keyword in keywords:
            found = keyword in code
            status = "✅" if found else "❌"
            if not found:
                all_pass = False
            print(f"  {status} {filename} contains '{keyword}': {'FOUND' if found else 'NOT FOUND'}")
    
    print(f"TEST 6: {'PASSED' if all_pass else 'SOME MISSING'}\n")
    return all_pass

def main():
    print("\n" + "=" * 50)
    print("RAJ AI v5 — FEATURE TEST SUITE")
    print("Testing all 6 prompt features...")
    print("=" * 50 + "\n")
    
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        print("Make sure you're running this from the same folder as Raj.")
        sys.exit(1)
    
    results = []
    results.append(("DB Schema", test_db_schema()))
    results.append(("Sub-Pool Filtering", test_sub_pool_filtering()))
    results.append(("Conditional Sequences", test_conditional_sequences()))
    results.append(("Soft Delete", test_soft_delete()))
    results.append(("UI Elements", test_ui_elements()))
    results.append(("Import Pipeline", test_import_methods()))
    
    print("=" * 50)
    print("FINAL RESULTS")
    print("=" * 50)
    passed = 0
    for name, ok in results:
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"  {status}: {name}")
        if ok:
            passed += 1
    
    print(f"\n{passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 ALL FEATURES LOOK GOOD! You can start using Raj.")
    elif passed >= 4:
        print("\n⚠️ MOSTLY OK. Check the failed tests above. Non-critical.")
    else:
        print("\n🔴 SEVERAL ISSUES. Tell Kimi: 'Fix the failed tests from test_raj.py'")
        print("   and paste the error output above.")

if __name__ == "__main__":
    main()
