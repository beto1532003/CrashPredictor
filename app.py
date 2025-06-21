from flask import Flask, render_template, request, session, redirect, url_for
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, base64, os, joblib, sqlite3, hashlib
from tensorflow.keras.models import load_model
from train_model import train_model
from auth import auth_bp, is_logged_in, is_admin
from functools import wraps
import traceback

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.register_blueprint(auth_bp)

SCALER_PATH = "models/scaler.pkl"
DATA_PATH = "game_data.csv"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            session.clear()
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/admin/users", methods=["GET", "POST"])
@login_required
def manage_users():
    if not is_admin():
        return redirect(url_for("index"))

    message = None
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    if request.method == "POST":
        if "add_user" in request.form:
            new_username = request.form["new_username"]
            new_password = request.form["new_password"]
            role = request.form["role"]

            # 🔐 تشفير كلمة السر
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

            try:
                c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                          (new_username, hashed_password, role))
                conn.commit()
                message = f"✅ تم إضافة المستخدم {new_username}"
            except sqlite3.IntegrityError:
                message = "❌ اسم المستخدم موجود بالفعل"

        elif "delete_user" in request.form:
            username_to_delete = request.form["username_to_delete"]
            if username_to_delete != session["username"]:
                c.execute("DELETE FROM users WHERE username=?", (username_to_delete,))
                conn.commit()
                message = f"🗑️ تم حذف المستخدم {username_to_delete}"
            else:
                message = "❌ لا يمكنك حذف حسابك الشخصي"

    c.execute("SELECT username, role FROM users")
    users = c.fetchall()
    conn.close()

    return render_template("admin_users.html", users=users, message=message)

def generate_chart(values):
    plt.figure(figsize=(8, 3))
    plt.plot(values, marker='o')
    plt.title("Crash Values")
    plt.xlabel("Round")
    plt.ylabel("Value")
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def predict_next_values(values, scaler, model):
    last_sequence = np.array(values[-10:]).reshape(-1, 1)
    scaled_sequence = scaler.transform(last_sequence)
    sequence = scaled_sequence.reshape(1, 10, 1)
    predictions = []
    for _ in range(5):
        pred_scaled = model.predict(sequence, verbose=0)[0][0]
        pred = scaler.inverse_transform([[pred_scaled]])[0][0]
        pred = float(np.clip(pred, 1.0, 35.0))
        predictions.append(round(pred, 2))
        next_input = np.concatenate((sequence[0][1:], np.array([[pred_scaled]])), axis=0)
        sequence = next_input.reshape(1, 10, 1)
    return predictions

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if "values" not in session:
        session["values"] = []

    prediction = None
    chart_base64 = None
    message = None

    if request.method == "POST":
        if "add" in request.form:
            try:
                val = float(request.form["value"])
                if 1 <= val <= 35:
                    session["values"].append(val)
                    session.modified = True
                    os.makedirs("models", exist_ok=True)
                    with open(DATA_PATH, "a") as f:
                        f.write(f"{val}\n")
                    if len(session["values"]) >= 11:
                        pattern = train_model(session["values"])
                        session["last_pattern"] = pattern
                        message = f"✅ تم حفظ القيمة وتدريب النموذج على النمط: {pattern}"
                    else:
                        message = "✅ تم حفظ القيمة، أدخل 11 قيمة على الأقل للتدريب"
                else:
                    message = "❗ القيمة يجب أن تكون بين 1 و 35"
            except ValueError:
                message = "❗ أدخل رقما صالحا"

        elif "reset" in request.form:
            session["values"] = []
            open(DATA_PATH, "w").close()
            message = "✅ تم إعادة ضبط البيانات"

        elif "download" in request.form:
            with open(DATA_PATH, "w") as f:
                for val in session["values"]:
                    f.write(f"{val}\n")
            message = "✅ تم حفظ البيانات"

        elif "train" in request.form:
            try:
                pattern = train_model(session["values"])
                session["last_pattern"] = pattern
                message = f"✅ تم تدريب النموذج باستخدام نمط: {pattern}"
            except Exception as e:
                message = f"❌ خطأ أثناء التدريب: {str(e)}"

        elif "predict" in request.form:
            if len(session["values"]) < 10:
                message = "❗ أدخل على الأقل 10 قيم للتوقع"
            else:
                try:
                    pattern = session.get("last_pattern", "transformer")
                    model_file_map = {
                        "LCG": "model_lcg.keras",
                        "PRNG": "model_prng.keras",
                        "HASH": "model_transformer.keras"
                    }
                    model_path = f"models/{model_file_map.get(pattern, 'model_transformer.keras')}"
                    model = load_model(model_path)
                    scaler = joblib.load(SCALER_PATH)
                    prediction = predict_next_values(session["values"], scaler, model)
                    chart_base64 = generate_chart(session["values"])
                except Exception as e:
                    print("[Prediction Error]:", traceback.format_exc())
                    message = f"❌ حدث خطأ أثناء التوقع: {str(e)}"

    return render_template("form.html", prediction=prediction, chart=chart_base64,
                           values=session["values"], message=message)

if __name__ == "__main__":
    app.run(debug=True)
ش