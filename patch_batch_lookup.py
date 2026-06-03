import os
import sys

raj_folder = os.path.join(os.path.expanduser('~'), 'RP Gmail')
filepath = os.path.join(raj_folder, 'raj_chat.py')

if not os.path.exists(filepath):
    print('File not found:', filepath)
    input('Press Enter...')
    sys.exit(1)

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# The fix: if batch is a string, look it up by name
old = '''            if batch:
                batch_id = batch.get("id")
                status = str(batch.get("status", "")).strip().upper()
                scheduled = batch.get("scheduled_at", "") if batch.get("scheduled_at") else ""
            else:
                batch_id = None
                status = "NONE"
                scheduled = ""'''

new = '''            # Handle both dict and string batch references
            if isinstance(batch, str):
                batch_name = batch
                batch = None
                for b in self.engine.db.get_batches():
                    if b.get("name") == batch_name:
                        batch = b
                        break
            
            if batch:
                batch_id = batch.get("id")
                status = str(batch.get("status", "")).strip().upper()
                scheduled = batch.get("scheduled_at", "") if batch.get("scheduled_at") else ""
            else:
                batch_id = None
                status = "NONE"
                scheduled = ""'''

if old in content:
    content = content.replace(old, new)
    print('✅ Patch applied')
else:
    print('⚠️ Pattern not found - may need manual fix')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Done. Restart Raj.')
input('Press Enter...')