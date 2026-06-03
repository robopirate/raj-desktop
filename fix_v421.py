import os, re

FOLDER = r"C:\Users\itsom\OneDrive\Documents\GitHub\raj-desktop"

# Fix 1: engine.py - HTML_TEMPLATE
engine_path = os.path.join(FOLDER, "engine.py")
with open(engine_path, "r", encoding="utf-8") as f:
    engine = f.read()

# Replace empty HTML_TEMPLATE
old_pattern = r'HTML_TEMPLATE\s*=\s*"""\s*"""'
new_template = 'HTML_TEMPLATE = """<!DOCTYPE html>\n<html>\n<head>\n<meta charset="UTF-8">\n<style>\nbody{font-family:Segoe UI,Arial,sans-serif;background:#0A1628;color:#E6EDF3;padding:20px;margin:0}\n.container{max-width:600px;margin:0 auto;background:#111D2E;border-radius:12px;padding:30px;border:1px solid #2a2a4e}\n.header{text-align:center;border-bottom:2px solid #59ced9;padding-bottom:15px;margin-bottom:20px}\n.logo{font-size:28px;font-weight:bold;color:#59ced9}\n.sub{color:#8B949E;font-size:12px}\n.content{line-height:1.6;font-size:14px}\n.footer{margin-top:30px;padding-top:15px;border-top:1px solid #2a2a4e;text-align:center;color:#8B949E;font-size:11px}\n.cta{display:inline-block;background:#59ced9;color:#0A1628;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:bold;margin:15px 0}\n</style>\n</head>\n<body>\n<div class="container">\n<div class="header">\n<div class="logo">🤖 RAJ by RoboPirate</div>\n<div class="sub">Smart Labs for Smart Schools</div>\n</div>\n<div class="content">\n{body}\n</div>\n<div class="footer">\n© 2026 RoboPirate · robopirate.in · Unsubscribe: reply STOP\n</div>\n</div>\n</body>\n</html>"""'

engine_new = re.sub(old_pattern, new_template, engine)
if engine_new != engine:
    with open(engine_path, "w", encoding="utf-8") as f:
        f.write(engine_new)
    print("✅ engine.py: HTML_TEMPLATE fixed")
else:
    old2 = 'HTML_TEMPLATE = """\n\n"""'
    if old2 in engine:
        engine = engine.replace(old2, new_template)
        with open(engine_path, "w", encoding="utf-8") as f:
            f.write(engine)
        print("✅ engine.py: HTML_TEMPLATE fixed (alt)")
    else:
        print("❌ engine.py: Could not find empty HTML_TEMPLATE")

# Fix 2: raj_chat.py - Dashboard refresh
chat_path = os.path.join(FOLDER, "raj_chat.py")
with open(chat_path, "r", encoding="utf-8") as f:
    chat = f.read()

old_refresh = '                if hasattr(self, \'views\') and "dashboard" in self.views:\n                    # Only refresh if dashboard is visible\n                    pass'
new_refresh = '                if hasattr(self, \'views\') and "dashboard" in self.views:\n                    # Only refresh if dashboard is visible\n                    self._refresh_dashboard()'

if old_refresh in chat:
    chat = chat.replace(old_refresh, new_refresh)
    with open(chat_path, "w", encoding="utf-8") as f:
        f.write(chat)
    print("✅ raj_chat.py: Dashboard auto-refresh fixed")
else:
    print("⚠️ raj_chat.py: Refresh pattern not found")

print("\n🎉 Done! Commit and push via GitHub Desktop.")
input("Press Enter to exit...")
