import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox


# Database connection
def connect_db():
    return sqlite3.connect("college.db")


# Main window
root = tk.Tk()
root.title("Student Management System")
root.geometry("800x600")


# Heading
title = tk.Label(
    root,
    text="Student Management System",
    font=("Arial", 22, "bold")
)
title.pack(pady=15)


# Input fields
form = tk.Frame(root)
form.pack(pady=10)

tk.Label(form, text="Student ID:").grid(
    row=0, column=0, padx=5, pady=5, sticky="w"
)
id_entry = tk.Entry(form)
id_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(form, text="Name:").grid(
    row=1, column=0, padx=5, pady=5, sticky="w"
)
name_entry = tk.Entry(form)
name_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(form, text="Email:").grid(
    row=2, column=0, padx=5, pady=5, sticky="w"
)
email_entry = tk.Entry(form)
email_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(form, text="Course:").grid(
    row=3, column=0, padx=5, pady=5, sticky="w"
)
course_entry = tk.Entry(form)
course_entry.grid(row=3, column=1, padx=5, pady=5)

tk.Label(form, text="CGPA:").grid(
    row=4, column=0, padx=5, pady=5, sticky="w"
)
cgpa_entry = tk.Entry(form)
cgpa_entry.grid(row=4, column=1, padx=5, pady=5)


# Table to display students
columns = ("ID", "Name", "Email", "Course", "CGPA")

table = ttk.Treeview(
    root,
    columns=columns,
    show="headings",
    height=10
)

for col in columns:
    table.heading(col, text=col)
    table.column(col, width=140)

table.pack(padx=15, pady=15, fill="both", expand=True)


# Clear input fields
def clear_fields():
    for entry in (
        id_entry,
        name_entry,
        email_entry,
        course_entry,
        cgpa_entry
    ):
        entry.delete(0, tk.END)


# Display all students
def view_students():
    for item in table.get_children():
        table.delete(item)

    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, email, course, cgpa "
                "FROM students ORDER BY id"
            )
            students = cursor.fetchall()

        for student in students:
            table.insert("", tk.END, values=student)

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


# Add student
def add_student():
    name = name_entry.get().strip()
    email = email_entry.get().strip()
    course = course_entry.get().strip()
    cgpa_text = cgpa_entry.get().strip()

    if not all((name, email, course, cgpa_text)):
        messagebox.showwarning(
            "Missing Information",
            "Please fill in Name, Email, Course and CGPA."
        )
        return

    try:
        cgpa = float(cgpa_text)

        if not 0 <= cgpa <= 10:
            messagebox.showwarning(
                "Invalid CGPA",
                "CGPA must be between 0 and 10."
            )
            return

        with connect_db() as conn:
            conn.execute(
                """
                INSERT INTO students (name, email, course, cgpa)
                VALUES (?, ?, ?, ?)
                """,
                (name, email, course, cgpa)
            )

        messagebox.showinfo(
            "Success", "Student added successfully!"
        )
        clear_fields()
        view_students()

    except ValueError:
        messagebox.showerror(
            "Invalid CGPA", "Please enter a valid number."
        )
    except sqlite3.IntegrityError:
        messagebox.showerror(
            "Error", "This email already exists."
        )
    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


# Search student by ID
def search_student():
    student_id = id_entry.get().strip()

    if not student_id.isdigit():
        messagebox.showwarning(
            "Invalid ID", "Please enter a valid Student ID."
        )
        return

    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, email, course, cgpa "
                "FROM students WHERE id = ?",
                (int(student_id),)
            )
            student = cursor.fetchone()

        if student:
            clear_fields()
            id_entry.insert(0, str(student[0]))
            name_entry.insert(0, student[1])
            email_entry.insert(0, student[2])
            course_entry.insert(0, student[3])
            cgpa_entry.insert(0, str(student[4]))
        else:
            messagebox.showinfo(
                "Not Found", "Student not found."
            )

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


# Update student's CGPA
def update_student():
    student_id = id_entry.get().strip()
    cgpa_text = cgpa_entry.get().strip()

    if not student_id.isdigit():
        messagebox.showwarning(
            "Invalid ID", "Enter a valid Student ID."
        )
        return

    try:
        cgpa = float(cgpa_text)

        if not 0 <= cgpa <= 10:
            messagebox.showwarning(
                "Invalid CGPA",
                "CGPA must be between 0 and 10."
            )
            return

        with connect_db() as conn:
            cursor = conn.execute(
                "UPDATE students SET cgpa = ? WHERE id = ?",
                (cgpa, int(student_id))
            )

            if cursor.rowcount == 0:
                messagebox.showinfo(
                    "Not Found", "Student ID not found."
                )
                return

        messagebox.showinfo(
            "Success", "CGPA updated successfully!"
        )
        view_students()

    except ValueError:
        messagebox.showerror(
            "Invalid CGPA", "Enter a valid CGPA."
        )
    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


# Delete student
def delete_student():
    student_id = id_entry.get().strip()

    if not student_id.isdigit():
        messagebox.showwarning(
            "Invalid ID", "Enter a valid Student ID."
        )
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this student?"
    )

    if not confirm:
        return

    try:
        with connect_db() as conn:
            cursor = conn.execute(
                "DELETE FROM students WHERE id = ?",
                (int(student_id),)
            )

            if cursor.rowcount == 0:
                messagebox.showinfo(
                    "Not Found", "Student ID not found."
                )
                return

        messagebox.showinfo(
            "Success", "Student deleted successfully!"
        )
        clear_fields()
        view_students()

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


# Buttons
buttons = tk.Frame(root)
buttons.pack(pady=10)

tk.Button(
    buttons, text="Add Student",
    command=add_student, width=14
).grid(row=0, column=0, padx=5, pady=5)

tk.Button(
    buttons, text="View Students",
    command=view_students, width=14
).grid(row=0, column=1, padx=5, pady=5)

tk.Button(
    buttons, text="Search Student",
    command=search_student, width=14
).grid(row=0, column=2, padx=5, pady=5)

tk.Button(
    buttons, text="Update CGPA",
    command=update_student, width=14
).grid(row=1, column=0, padx=5, pady=5)

tk.Button(
    buttons, text="Delete Student",
    command=delete_student, width=14
).grid(row=1, column=1, padx=5, pady=5)

tk.Button(
    buttons, text="Clear Fields",
    command=clear_fields, width=14
).grid(row=1, column=2, padx=5, pady=5)


# Load existing records and start application
view_students()
root.mainloop()