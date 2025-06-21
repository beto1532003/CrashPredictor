import sqlite3

# الاتصال بقاعدة البيانات أو إنشاؤها
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# إنشاء جدول المستخدمين لو مش موجود
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

# إضافة مستخدم admin مبدأي (beto)
cursor.execute("""
INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)
""", ("beto", "15382002", "admin"))

# حفظ التغييرات
conn.commit()
conn.close()

print("✅ قاعدة البيانات اتعملت والمستخدم admin اتسجل")
