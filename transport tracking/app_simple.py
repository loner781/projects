from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import sqlite3
import time

app = Flask(__name__)
app.secret_key = "secret123"

DB_NAME = "transport.db"

# ---------- Database Setup ----------
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        # Users
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT, password TEXT)''')
        # Buses
        c.execute('''CREATE TABLE IF NOT EXISTS buses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        bus_number TEXT, route TEXT)''')
        # Locations
        c.execute('''CREATE TABLE IF NOT EXISTS locations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        bus_id INTEGER, latitude REAL, longitude REAL, timestamp TEXT)''')
        
        # Create default user if none exists
        c.execute("SELECT COUNT(*) FROM users")
        user_count = c.fetchone()[0]
        if user_count == 0:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin123"))
            print("Created default user: admin / admin123")
        
        conn.commit()

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()
        if user:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        
        # Validate input
        if not username or not password:
            return render_template("signup.html", error="Username and password are required")
        
        if password != confirm_password:
            return render_template("signup.html", error="Passwords do not match")
        
        if len(password) < 6:
            return render_template("signup.html", error="Password must be at least 6 characters long")
        
        # Check if user already exists
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=?", (username,))
            existing_user = c.fetchone()
            
            if existing_user:
                return render_template("signup.html", error="Username already exists")
            
            # Create new user
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        
        # Auto-login after successful signup
        session["user"] = username
        return redirect(url_for("dashboard"))
    
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM buses")
        buses = c.fetchall()
    return render_template("dashboard.html", buses=buses)

@app.route("/add_bus", methods=["GET", "POST"])
def add_bus():
    if request.method == "POST":
        bus_number = request.form["bus_number"]
        route = request.form["route"]
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO buses (bus_number, route) VALUES (?,?)", (bus_number, route))
            conn.commit()
        return redirect(url_for("dashboard"))
    return render_template("add_bus.html")

@app.route("/api/update_location", methods=["POST"])
def update_location():
    data = request.get_json()
    bus_id = data["bus_id"]
    lat = data["latitude"]
    lon = data["longitude"]
    timestamp = str(int(time.time()))
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO locations (bus_id, latitude, longitude, timestamp) VALUES (?,?,?,?)",
                  (bus_id, lat, lon, timestamp))
        conn.commit()
    return jsonify({"status": "success"})

@app.route("/track_bus")
def track_bus():
    return render_template("track_bus.html")

@app.route("/api/get_locations")
def get_locations():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT bus_id, latitude, longitude, timestamp FROM locations ORDER BY id DESC LIMIT 10")
        data = c.fetchall()
    return jsonify(data)

# ---------- Run ----------
if __name__ == "__main__":
    init_db()
    print("Starting Flask server on http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
