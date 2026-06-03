import os

FOLDER = r"C:\Users\itsom\OneDrive\Documents\GitHub\raj-desktop"

# Fix engine.py
engine_path = os.path.join(FOLDER, "engine.py")
with open(engine_path, "r", encoding="utf-8") as file:
    engine = file.read()

old = "scheduled = (datetime.now() + timedelta(days=2)).replace(hour=10, minute=0, second=0, microsecond=0)"
new = """completed_at = completed_batch.get("completed_at")
    if completed_at:
        try:
            base_dt = datetime.fromisoformat(completed_at)
        except:
            base_dt = datetime.now()
    else:
        base_dt = datetime.now()
    scheduled = (base_dt + timedelta(days=2)).replace(hour=10, minute=0, second=0, microsecond=0)"""

if old in engine:
    engine = engine.replace(old, new)
    with open(engine_path, "w", encoding="utf-8") as file:
        file.write(engine)
    print("Fixed engine.py")

# Fix raj_chat.py
chat_path = os.path.join(FOLDER, "raj_chat.py")
with open(chat_path, "r", encoding="utf-8") as file:
    chat = file.read()

chat = chat.replace("if status != 'COMPLETED':", "if status not in ['COMPLETED', 'NOT_CREATED']:")
chat = chat.replace("if scheduled and status in ['SCHEDULED', 'DRAFT']:", "if scheduled:")

with open(chat_path, "w", encoding="utf-8") as file:
    file.write(chat)
print("Fixed raj_chat.py")

print("Done! Commit and push via GitHub Desktop.")
input("Press Enter...")