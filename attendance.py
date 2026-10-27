import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date

DB_NAME = "college.db"

def create_attendance_table():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                student_id INTEGER NOT NULL,
                attendance_date TEXT NOT NULL,
                status TEXT NOT NULL,
                UNIQUE(student_id, attendance_date)
            )
        """)


def get_students():
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute(
            "SELECT id, name, course FROM students ORDER BY name"
        ).fetchall()
def get_attendance_percentage(student_id):
    with sqlite3.connect(DB_NAME) as conn:
        result = conn.execute("""
            SELECT
                COUNT(*),
                SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END)
            FROM attendance
            WHERE student_id = ?
        """, (student_id,)).fetchone()

    total = result[0] or 0
    present = result[1] or 0

    if total == 0:
        return "0.0%"

    percentage = (present / total) * 100
    return f"{percentage:.1f}%"

def load_students():
    for item in table.get_children():
        table.delete(item)

    try:
        students = get_students()

        for student_id, name, course in students:
            percentage = get_attendance_percentage(student_id)

            table.insert(
                "",
                "end",
                iid=str(student_id),
                values=(
                    student_id,
                    name,
                    course,
                    "Not Marked",
                    percentage
                )
            )

        load_saved_attendance()

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))
     

        


def load_saved_attendance():
    selected_date = date_entry.get().strip()

    try:
        with sqlite3.connect(DB_NAME) as conn:
            records = conn.execute(
                """
                SELECT student_id, status
                FROM attendance
                WHERE attendance_date = ?
                """,
                (selected_date,)
            ).fetchall()

        for student_id, status in records:
            item_id = str(student_id)

            if table.exists(item_id):
                values = list(table.item(item_id, "values"))
                values[3] = status
                table.item(item_id, values=values)

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


def mark_attendance(status):
    selected = table.selection()

    if not selected:
        messagebox.showwarning(
            "Select Student",
            "Please select a student from the table first."
        )
        return

    selected_date = date_entry.get().strip()

    try:
        date.fromisoformat(selected_date)
    except ValueError:
        messagebox.showerror(
            "Invalid Date",
            "Date format must be YYYY-MM-DD."
        )
        return

    student_id = int(selected[0])

    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                """
                INSERT INTO attendance
                    (student_id, attendance_date, status)
                VALUES (?, ?, ?)
                ON CONFLICT(student_id, attendance_date)
                DO UPDATE SET status = excluded.status
                """,
                (student_id, selected_date, status)
            )

        load_students()
        table.selection_set(str(student_id))

        messagebox.showinfo(
            "Success",
            f"Attendance marked {status} and saved!"
        )

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


root = tk.Tk()
root.title("Student Attendance Management")
root.geometry("850x550")
root.configure(bg="#F3F5F9")

heading = tk.Label(
    root,
    text="Attendance Management",
    font=("Arial", 22, "bold"),
    bg="#F3F5F9",
    fg="#1E293B"
)
heading.pack(pady=(20, 5))

tk.Label(
    root,
    text="Select a student, choose a date, and mark attendance.",
    font=("Arial", 11),
    bg="#F3F5F9",
    fg="#64748B"
).pack(pady=(0, 15))

date_frame = tk.Frame(root, bg="#F3F5F9")
date_frame.pack(pady=5)

tk.Label(
    date_frame,
    text="Attendance Date (YYYY-MM-DD):",
    font=("Arial", 11),
    bg="#F3F5F9"
).pack(side="left", padx=5)

date_entry = tk.Entry(date_frame, width=14, font=("Arial", 11))
date_entry.pack(side="left", padx=5)
date_entry.insert(0, date.today().isoformat())

tk.Button(
    date_frame,
    text="Load Date",
    command=load_students,
    bg="#2563EB",
    fg="white",
    padx=10
).pack(side="left", padx=5)

columns = ("ID", "Name", "Course", "Status", "Attendance %")

table = ttk.Treeview(
    root,
    columns=columns,
    show="headings",
    height=13,
    selectmode="browse"
)

column_widths = {
    "ID": 60,
    "Name": 150,
    "Course": 140,
    "Status": 120,
    "Attendance %": 130
}

for column in columns:
    table.heading(column, text=column)
    table.column(
        column,
        width=column_widths[column],
        anchor="center"
    )

table.pack(fill="both", expand=True, padx=20, pady=15)

buttons = tk.Frame(root, bg="#F3F5F9")
buttons.pack(pady=(0, 20))

tk.Button(
    buttons,
    text="Mark Present",
    command=lambda: mark_attendance("Present"),
    bg="#15803D",
    fg="white",
    font=("Arial", 11, "bold"),
    padx=15,
    pady=8
).pack(side="left", padx=8)

tk.Button(
    buttons,
    text="Mark Absent",
    command=lambda: mark_attendance("Absent"),
    bg="#DC2626",
    fg="white",
    font=("Arial", 11, "bold"),
    padx=15,
    pady=8
).pack(side="left", padx=8)

tk.Button(
    buttons,
    text="Refresh",
    command=load_students,
    font=("Arial", 11),
    padx=15,
    pady=8
).pack(side="left", padx=8)

create_attendance_table()
load_students()
root.mainloop()