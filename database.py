import sqlite3

Database se connection

conn = sqlite3.connect("college.db")
cursor = conn.cursor()

Students table

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
email TEXT UNIQUE NOT NULL,
course TEXT NOT NULL,
cgpa REAL
)
""")

Attendance table

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
id INTEGER PRIMARY KEY AUTOINCREMENT,
student_id INTEGER NOT NULL,
attendance_date TEXT NOT NULL,
status TEXT NOT NULL CHECK(status IN ('Present', 'Absent')),
UNIQUE(student_id, attendance_date),
FOREIGN KEY (student_id) REFERENCES students(id)
)
""")

Changes save karna

conn.commit()

Connection close karna

conn.close()

print("Database, students table, and attendance table created successfully!")