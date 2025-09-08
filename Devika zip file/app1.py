import os
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv

# ----------------------------
# Paths
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent

# Templates and static files
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "devi" / "devi"   # ✅ static files inside devi/devi

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")

# ----------------------------
# Flask App
# ----------------------------
app = Flask(__name__, template_folder=str(TEMPLATES_DIR), static_folder=str(STATIC_DIR))
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change_me")

# ----------------------------
# Database
# ----------------------------
dbconfig = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),  # ✅ password comes from .env
    "database": os.getenv("DB_NAME", "devi"),
}
pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **dbconfig)

def get_db():
    return pool.get_connection()

def query(sql, params=None, commit=False, dictcur=True):
    """Helper for running queries safely"""
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=dictcur)
        cur.execute(sql, params or ())
        if commit:
            conn.commit()
            return cur.rowcount
        if sql.strip().lower().startswith("select"):
            return cur.fetchall()
        return None
    finally:
        try:
            cur.close()
        except Exception:
            pass
        conn.close()

# ----------------------------
# Routes
# ----------------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/teams")
def teams():
    return render_template("teams.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("fullname") or request.form.get("name")
        gender = request.form.get("gender")
        sport = request.form.get("sport")
        department = request.form.get("department")
        contact = request.form.get("contact")
        email = request.form.get("email")

        if not name:
            flash("Name is required", "danger")
            return redirect(url_for("register"))

        sql = """INSERT INTO student_registrations (name, gender, sport, department, contact, email)
                 VALUES (%s,%s,%s,%s,%s,%s)"""
        query(sql, (name, gender, sport, department, contact, email), commit=True, dictcur=False)
        flash("Registration saved!", "success")
        return redirect(url_for("admin"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Demo: plain text check (⚠️ not safe in production)
        rows = query("SELECT * FROM admins WHERE username=%s AND password=%s", (username, password))
        if rows:
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("index"))

def require_admin():
    return session.get("admin_logged_in", False)

@app.route("/admin")
def admin():
    if not require_admin():   # ✅ now protected
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))
    students = query("SELECT * FROM student_registrations ORDER BY id DESC") or []
    return render_template("admin.html", students=students)


@app.route("/delete/<int:student_id>", methods=["POST"])  # ✅ only POST
def delete(student_id):
    query("DELETE FROM student_registrations WHERE id=%s", (student_id,), commit=True, dictcur=False)
    flash("Deleted.", "info")
    return redirect(url_for("admin"))

@app.route("/Addplayer", methods=["GET", "POST"])
def addplayer():
    if request.method == "POST":
        name = request.form.get("name")
        team = request.form.get("team")
        position = request.form.get("position")
        matches = request.form.get("matches", type=int)
        goals = request.form.get("goals", type=int)
        assists = request.form.get("assists", type=int)

        try:
            # Insert into players table
            query("""INSERT INTO players (name, team, position, matches, goals, assists)
                     VALUES (%s, %s, %s, %s, %s, %s)""",
                  (name, team, position, matches, goals, assists),
                  commit=True, dictcur=False)

            flash("✅ Player added successfully!", "success")
        except Exception as e:
            print("❌ Error inserting player:", e)
            flash("Something went wrong while saving the player.", "danger")

        return redirect(url_for("performance"))

    return render_template("Addplayer.html")

@app.route("/Performance")
def performance():
    players = query("SELECT * FROM players ORDER BY goals DESC, assists DESC") or []
    # Calculate energy dynamically
    for p in players:
      matches = p.get("matches", 0) or 0
      goals = p.get("goals", 0) or 0
      assists = p.get("assists", 0) or 0
      # Always integer value
      p["energy"] = int(max(0, 100 - (matches * 2) + (goals * 1) + (assists * 0.5)))

    return render_template("Performance.html", players=players)


@app.route("/contact", methods=["GET","POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        query("INSERT INTO contacts (name,email,message) VALUES (%s,%s,%s)",
              (name, email, message), commit=True, dictcur=False)
        flash("Thanks for contacting us!", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")

# ----------------------------
# Run App
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)
