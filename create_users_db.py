import sqlite3

# إنشاء اتصال بقاعدة البيانات (أو إنشاؤها لو مش موجودة)
conn = sqlite3.connect('users.db')
c = conn.cursor()

# إنشاء جدول المستخدمين
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'user'))
    )
''')

# إضافة أول مستخدم (أنت كأدمن)
c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", 
          ("beto", "15382002", "admin"))

conn.commit()
conn.close()

print("✅ قاعدة البيانات وإنشاء الأدمن تم بنجاح.")
