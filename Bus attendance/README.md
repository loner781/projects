# Bus Attendance Management System

A modern Flask-based web application for managing student bus attendance with a beautiful, responsive UI.

## Features

- **User Authentication**: Secure login/signup system with password hashing
- **Student Management**: Add and manage student records
- **Attendance Tracking**: Mark daily attendance for students
- **Record Viewing**: View attendance history and reports
- **Responsive Design**: Modern, mobile-friendly interface
- **SQLite Database**: Lightweight, file-based database

## Installation

1. **Install Python** (if not already installed)
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```bash
   python app.py
   ```
4. **Open your browser** and go to `http://localhost:5000`

## Default Login

- **Username**: `admin`
- **Password**: `admin123`

## Usage

### 1. First Time Setup
- Visit the application in your browser
- Click "Sign up" to create a new account, or use the default admin account

### 2. Adding Students
- Login to the dashboard
- Fill in student details (Name, Roll Number, Bus Number)
- Click "Add Student"

### 3. Marking Attendance
- Go to "Mark Attendance" from the dashboard
- Select Present/Absent for each student
- Click "Save Attendance"

### 4. Viewing Records
- Click "View Records" to see all attendance history
- Records are sorted by date (newest first)

## Database Schema

The application uses SQLite with three main tables:

- **users**: Stores user accounts (id, username, email, password)
- **students**: Stores student information (id, name, roll, bus_no)
- **attendance**: Stores attendance records (id, student_id, date, status)

## Security Features

- Password hashing using SHA-256
- Session management
- Input validation
- SQL injection protection
- Login required for protected routes

## File Structure

```
Bus attendance/
├── app.py                 # Main Flask application
├── bus.db                # SQLite database file
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── static/
│   └── style.css        # CSS styles
└── templates/
    ├── base.html        # Base template
    ├── index.html       # Home page
    ├── login.html       # Login page
    ├── signup.html      # Signup page
    ├── dashboard.html   # Main dashboard
    ├── mark_attendance.html  # Attendance marking
    └── view_attendance.html  # Attendance records
```

## Troubleshooting

- **Database errors**: Make sure the application has write permissions in the directory
- **Port already in use**: Change the port in `app.py` (line 200)
- **Python not found**: Install Python and ensure it's in your PATH

## Customization

- **Styling**: Edit `static/style.css` to change the appearance
- **Database**: The SQLite file `bus.db` can be backed up or moved
- **Port**: Change the port in the last line of `app.py`

## Support

For issues or questions, check the console output for error messages and ensure all dependencies are properly installed.
