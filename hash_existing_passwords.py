import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

DB_PATH = "users.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# نجيب كل اليوزرز والباسوردات
c.execute("SELECT id, password FROM users")
users = c.fetchall()

updated = 0
for user_id, password in users:
    # لو الباسورد مش طوله 64 (يعني غالبًا مش هاش)، شفره
    if len(password) != 64:
        hashed = hash_password(password)
        c.execute("UPDATE users SET password=? WHERE id=?", (hashed, user_id))
        updated += 1

conn.commit()
conn.close()

print(f"✅ تم تحديث {updated} كلمة مرور.")
