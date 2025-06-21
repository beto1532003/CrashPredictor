import sqlite3
import time
import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, session

auth_bp = Blueprint('auth', __name__)

DB_PATH = "users.db"
AUTH_VERSION = "v1"
ACCESS_DURATION = 3600  # ثانية (1 ساعة)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, password, role FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row if row else None

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = get_user(username)

        if user and user[1] == hash_password(password):
            session["logged_in"] = True
            session["login_time"] = int(time.time())
            session["auth_version"] = AUTH_VERSION
            session["username"] = username
            session["role"] = user[2]

            if user[2] == "admin":
                return redirect(url_for("manage_users"))
            else:
                return redirect(url_for("index"))
        else:
            return render_template("login.html", error="❌ اسم المستخدم أو كلمة المرور خطأ")

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

def is_logged_in():
    if session.get("logged_in"):
        login_time = session.get("login_time", 0)
        if int(time.time()) - login_time <= ACCESS_DURATION:
            if session.get("auth_version") == AUTH_VERSION:
                return True
    return False

def is_admin():
    return session.get("role") == "admin"
