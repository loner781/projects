import os
import sqlite3
import hashlib
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import date
from functools import wraps

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- Database Path ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "bus.db")

# ---------- Helper Functions ----------
def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    """Get database connection with error handling"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------- Database Setup ----------
def init_db():
    """Initialize database with proper error handling and migration"""
    try:
        conn = get_db_connection()
        if not conn:
            raise Exception("Could not connect to database")
            
        cur = conn.cursor()
        
        # Check if users table exists and get its structure
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        users_table_exists = cur.fetchone()
        
        if users_table_exists:
            # Check if email column exists
            cur.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cur.fetchall()]
            
            if 'email' not in columns:
                print("Migrating database: Adding email column to users table...")
                cur.execute("ALTER TABLE users ADD COLUMN email TEXT")
                cur.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                # Update existing admin user with email
                cur.execute("UPDATE users SET email = 'admin@example.com' WHERE username = 'admin'")
                conn.commit()
                print("Database migration completed!")
        else:
            # Create users table from scratch
            cur.execute("""CREATE TABLE users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            email TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

        # Create students table
        cur.execute("""CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        roll TEXT UNIQUE NOT NULL,
                        bus_no TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

        # Create attendance table
        cur.execute("""CREATE TABLE IF NOT EXISTS attendance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER NOT NULL,
                        date TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(student_id) REFERENCES students(id),
                        UNIQUE(student_id, date))""")
        
        # Insert default admin user if not exists
        admin_password = hash_password("admin123")
        cur.execute("""INSERT OR IGNORE INTO users(username, email, password) 
                       VALUES(?, ?, ?)""", ("admin", "admin@example.com", admin_password))
        
        conn.commit()
        conn.close()
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"FATAL ERROR: Could not initialize database. {e}")
        raise

# Initialize database
init_db()

# ---------- Routes ----------
@app.route("/")
def index():
    """Home page"""
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page"""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if not username or not password:
            flash("Please fill in all fields.", "danger")
            return render_template("login.html")
        
        conn = get_db_connection()
        if not conn:
            flash("Database connection error. Please try again.", "danger")
            return render_template("login.html")
            
        try:
            cur = conn.cursor()
            hashed_password = hash_password(password)
            cur.execute("SELECT id, username, email FROM users WHERE username=? AND password=?", 
                       (username, hashed_password))
            user = cur.fetchone()
            conn.close()
            
            if user:
                session['user'] = {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email']
                }
                flash(f"Welcome back, {user['username']}!", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid username or password.", "danger")
        except Exception as e:
            flash("Login error. Please try again.", "danger")
            print(f"Login error: {e}")
        finally:
            if conn:
                conn.close()
    
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Signup page"""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        
        if not all([username, email, password]):
            flash("Please fill in all fields.", "danger")
            return render_template("signup.html")
        
        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("signup.html")
        
        conn = get_db_connection()
        if not conn:
            flash("Database connection error. Please try again.", "danger")
            return render_template("signup.html")
            
        try:
            cur = conn.cursor()
            hashed_password = hash_password(password)
            cur.execute("INSERT INTO users(username, email, password) VALUES(?, ?, ?)", 
                       (username, email, hashed_password))
            conn.commit()
            conn.close()
            
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("login"))
            
        except sqlite3.IntegrityError:
            flash("Username or email already exists.", "danger")
        except Exception as e:
            flash("Registration error. Please try again.", "danger")
            print(f"Signup error: {e}")
        finally:
            if conn:
                conn.close()
    
    return render_template("signup.html")

@app.route("/dashboard")
@login_required
def dashboard():
    """Dashboard page"""
    return render_template("dashboard.html")

@app.route("/add_student", methods=["POST"])
@login_required
def add_student():
    """Add new student"""
    name = request.form.get("name", "").strip()
    roll = request.form.get("roll", "").strip()
    bus_no = request.form.get("bus_no", "").strip()
    
    if not all([name, roll, bus_no]):
        flash("Please fill in all fields.", "danger")
        return redirect(url_for("dashboard"))
    
    conn = get_db_connection()
    if not conn:
        flash("Database connection error. Please try again.", "danger")
        return redirect(url_for("dashboard"))
    
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO students(name, roll, bus_no) VALUES(?, ?, ?)", 
                   (name, roll, bus_no))
        conn.commit()
        conn.close()
        flash("Student added successfully!", "success")
    except sqlite3.IntegrityError:
        flash("Student with this roll number already exists.", "danger")
    except Exception as e:
        flash("Error adding student. Please try again.", "danger")
        print(f"Add student error: {e}")
    finally:
        if conn:
            conn.close()
    
    return redirect(url_for("dashboard"))

@app.route("/mark_attendance", methods=["GET", "POST"])
@login_required
def mark_attendance():
    """Mark attendance page"""
    conn = get_db_connection()
    if not conn:
        flash("Database connection error. Please try again.", "danger")
        return redirect(url_for("dashboard"))
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM students ORDER BY name")
        students = cur.fetchall()
        conn.close()
        
        if request.method == "POST":
            today = str(date.today())
            conn = get_db_connection()
            if not conn:
                flash("Database connection error. Please try again.", "danger")
                return redirect(url_for("dashboard"))
            
            try:
                cur = conn.cursor()
                
                # Check if attendance already marked for today
                cur.execute("SELECT COUNT(*) FROM attendance WHERE date=?", (today,))
                if cur.fetchone()[0] > 0:
                    flash("Attendance already marked for today!", "warning")
                    return redirect(url_for("dashboard"))
                
                # Insert attendance records
                for student in students:
                    status = request.form.get(f"status_{student['id']}", "Absent")
                    cur.execute("INSERT INTO attendance(student_id, date, status) VALUES(?, ?, ?)",
                               (student['id'], today, status))
                
                conn.commit()
                conn.close()
                flash("Attendance marked successfully!", "success")
                return redirect(url_for("dashboard"))
                
            except Exception as e:
                flash("Error marking attendance. Please try again.", "danger")
                print(f"Mark attendance error: {e}")
            finally:
                if conn:
                    conn.close()
        
        return render_template("mark_attendance.html", students=students)
        
    except Exception as e:
        flash("Error loading students. Please try again.", "danger")
        print(f"Load students error: {e}")
        return redirect(url_for("dashboard"))

@app.route("/view_attendance")
@login_required
def view_attendance():
    """View attendance records"""
    conn = get_db_connection()
    if not conn:
        flash("Database connection error. Please try again.", "danger")
        return redirect(url_for("dashboard"))
    
    try:
        cur = conn.cursor()
        cur.execute("""SELECT students.name, students.roll, students.bus_no, 
                              attendance.date, attendance.status
                       FROM attendance
                       JOIN students ON students.id = attendance.student_id
                       ORDER BY attendance.date DESC, students.name""")
        records = cur.fetchall()
        conn.close()
        return render_template("view_attendance.html", records=records)
    except Exception as e:
        flash("Error loading attendance records. Please try again.", "danger")
        print(f"View attendance error: {e}")
        return redirect(url_for("dashboard"))
    finally:
        if conn:
            conn.close()

@app.route("/logout")
def logout():
    """Logout user"""
    session.pop("user", None)
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)