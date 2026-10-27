import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from datetime import date

# Use the same project database without replacing existing tables
DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "college.db"
)


# ---------------- DATABASE ----------------

def connect_db():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS placement_companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            job_role TEXT NOT NULL,
            package_lpa REAL NOT NULL,
            min_cgpa REAL NOT NULL,
            eligible_branch TEXT NOT NULL,
            deadline TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS placement_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            student_email TEXT NOT NULL,
            company_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Applied',
            applied_on TEXT NOT NULL,
            FOREIGN KEY (company_id)
                REFERENCES placement_companies(id)
        )
    """)

    conn.commit()
    conn.close()


# ---------------- MAIN WINDOW ----------------

initialize_database()

root = tk.Tk()
root.title("College Placement Management")
root.geometry("1100x720")
root.minsize(900, 600)
root.configure(bg="#F1F5F9")

style = ttk.Style()
style.configure(
    "Treeview",
    rowheight=28,
    font=("Arial", 10)
)
style.configure(
    "Treeview.Heading",
    font=("Arial", 10, "bold")
)

# ---------------- HEADER ----------------

header = tk.Frame(root, bg="#172554", height=90)
header.pack(fill="x")
header.pack_propagate(False)

tk.Label(
    header,
    text="PLACEMENT MANAGEMENT",
    font=("Arial", 22, "bold"),
    bg="#172554",
    fg="white"
).pack(anchor="w", padx=25, pady=(15, 2))

tk.Label(
    header,
    text="Company Recruitment • Student Applications • Selection Tracking",
    font=("Arial", 10),
    bg="#172554",
    fg="#BFDBFE"
).pack(anchor="w", padx=27)


# ---------------- STATISTICS ----------------

stats_frame = tk.Frame(root, bg="#F1F5F9")
stats_frame.pack(fill="x", padx=20, pady=15)

stats_labels = {}

for title in ["Companies", "Applications", "Selected"]:
    card = tk.Frame(
        stats_frame,
        bg="white",
        highlightbackground="#CBD5E1",
        highlightthickness=1
    )
    card.pack(side="left", fill="x", expand=True, padx=6)

    tk.Label(
        card,
        text=title,
        font=("Arial", 11, "bold"),
        bg="white",
        fg="#64748B"
    ).pack(pady=(12, 3))

    value_label = tk.Label(
        card,
        text="0",
        font=("Arial", 23, "bold"),
        bg="white",
        fg="#2563EB"
    )
    value_label.pack(pady=(0, 12))

    stats_labels[title] = value_label


# ---------------- NOTEBOOK / TABS ----------------

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))

company_tab = tk.Frame(notebook, bg="#F8FAFC")
application_tab = tk.Frame(notebook, bg="#F8FAFC")

notebook.add(company_tab, text="  Company Management  ")
notebook.add(application_tab, text="  Student Applications  ")


# ---------------- COMPANY FORM ----------------

tk.Label(
    company_tab,
    text="Add Company & Job Details",
    font=("Arial", 16, "bold"),
    bg="#F8FAFC",
    fg="#172554"
).pack(anchor="w", padx=15, pady=(15, 10))

company_form = tk.Frame(company_tab, bg="#F8FAFC")
company_form.pack(fill="x", padx=15)

company_fields = [
    ("Company Name", "name"),
    ("Job Role", "role"),
    ("Package (LPA)", "package"),
    ("Minimum CGPA", "cgpa"),
    ("Eligible Branch", "branch"),
    ("Deadline (YYYY-MM-DD)", "deadline")
]

company_entries = {}

for index, (label_text, key) in enumerate(company_fields):
    row = index // 2
    column = (index % 2) * 2

    tk.Label(
        company_form,
        text=label_text,
        font=("Arial", 10, "bold"),
        bg="#F8FAFC"
    ).grid(row=row, column=column, sticky="w", padx=5, pady=7)

    entry = tk.Entry(company_form, font=("Arial", 10), width=25)
    entry.grid(
        row=row,
        column=column + 1,
        sticky="ew",
        padx=5,
        pady=7,
        ipady=4
    )

    company_entries[key] = entry

company_form.columnconfigure(1, weight=1)
company_form.columnconfigure(3, weight=1)


# ---------------- COMPANY TABLE ----------------

tk.Label(
    company_tab,
    text="Available Companies",
    font=("Arial", 13, "bold"),
    bg="#F8FAFC",
    fg="#172554"
).pack(anchor="w", padx=15, pady=(15, 8))

company_columns = (
    "id", "company", "role", "package",
    "cgpa", "branch", "deadline"
)

company_tree = ttk.Treeview(
    company_tab,
    columns=company_columns,
    show="headings",
    height=8
)

company_headings = {
    "id": "ID",
    "company": "Company",
    "role": "Job Role",
    "package": "LPA",
    "cgpa": "Min CGPA",
    "branch": "Branch",
    "deadline": "Deadline"
}

company_widths = {
    "id": 45,
    "company": 145,
    "role": 145,
    "package": 65,
    "cgpa": 75,
    "branch": 100,
    "deadline": 110
}

for col in company_columns:
    company_tree.heading(col, text=company_headings[col])
    company_tree.column(col, width=company_widths[col], anchor="center")

company_tree.pack(fill="both", expand=True, padx=15, pady=5)


# ---------------- APPLICATION FORM ----------------

tk.Label(
    application_tab,
    text="Register Student Application",
    font=("Arial", 16, "bold"),
    bg="#F8FAFC",
    fg="#172554"
).pack(anchor="w", padx=15, pady=(15, 10))

application_form = tk.Frame(application_tab, bg="#F8FAFC")
application_form.pack(fill="x", padx=15)

# ---------------- STUDENT INTEGRATION ----------------

tk.Label(
    application_form,
    text="Select Student",
    font=("Arial", 10, "bold"),
    bg="#F8FAFC"
).grid(row=0, column=0, sticky="w", padx=5, pady=7)

student_combo = ttk.Combobox(
    application_form,
    state="readonly",
    width=28
)
student_combo.grid(
    row=0, column=1, sticky="ew",
    padx=5, pady=7, ipady=4
)

tk.Label(
    application_form,
    text="Student Email",
    font=("Arial", 10, "bold"),
    bg="#F8FAFC"
).grid(row=1, column=0, sticky="w", padx=5, pady=7)

student_email_var = tk.StringVar()

student_email_entry = tk.Entry(
    application_form,
    textvariable=student_email_var,
    font=("Arial", 10),
    width=30,
    state="readonly"
)
student_email_entry.grid(
    row=1, column=1, sticky="ew",
    padx=5, pady=7, ipady=4
)

student_map = {}


def load_students():
    global student_map

    student_map = {}

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, email, course
            FROM students
            ORDER BY name
        """)

        rows = cursor.fetchall()
        conn.close()

        student_values = []

        for student_id, name, email, course in rows:
            display_name = f"{name} (ID: {student_id})"
            student_map[display_name] = {
                "id": student_id,
                "name": name,
                "email": email,
                "course": course
            }
            student_values.append(display_name)

        student_combo["values"] = student_values

        if student_values:
            student_combo.current(0)
            fill_student_email()
        else:
            student_email_var.set("")

    except sqlite3.Error as error:
        messagebox.showerror(
            "Student Database Error",
            str(error)
        )


def fill_student_email(event=None):
    selected_student = student_combo.get()
    student = student_map.get(selected_student)

    if student:
        student_email_var.set(student["email"] or "")
    else:
        student_email_var.set("")


student_combo.bind(
    "<<ComboboxSelected>>",
    fill_student_email
)

tk.Label(
    application_form,
    text="Company",
    font=("Arial", 10, "bold"),
    bg="#F8FAFC"
).grid(row=0, column=2, sticky="w", padx=5, pady=7)

company_combo = ttk.Combobox(
    application_form,
    state="readonly",
    width=28
)
company_combo.grid(row=0, column=3, padx=5, pady=7)

tk.Label(
    application_form,
    text="Initial Status",
    font=("Arial", 10, "bold"),
    bg="#F8FAFC"
).grid(row=1, column=2, sticky="w", padx=5, pady=7)

status_combo = ttk.Combobox(
    application_form,
    values=["Applied", "Shortlisted", "Selected", "Rejected"],
    state="readonly",
    width=26
)
status_combo.grid(row=1, column=3, padx=5, pady=7)
status_combo.set("Applied")

application_form.columnconfigure(1, weight=1)
application_form.columnconfigure(3, weight=1)


# ---------------- APPLICATION TABLE ----------------

tk.Label(
    application_tab,
    text="Student Placement Tracker",
    font=("Arial", 13, "bold"),
    bg="#F8FAFC",
    fg="#172554"
).pack(anchor="w", padx=15, pady=(15, 8))

application_columns = (
    "id", "student", "email", "company",
    "role", "package", "status", "date"
)

application_tree = ttk.Treeview(
    application_tab,
    columns=application_columns,
    show="headings",
    height=8
)

application_headings = {
    "id": "ID",
    "student": "Student",
    "email": "Email",
    "company": "Company",
    "role": "Role",
    "package": "LPA",
    "status": "Status",
    "date": "Applied On"
}

for col in application_columns:
    application_tree.heading(col, text=application_headings[col])
    application_tree.column(col, width=115, anchor="center")

application_tree.column("id", width=45)
application_tree.pack(fill="both", expand=True, padx=15, pady=5)


# ---------------- REFRESH DATA ----------------

company_map = {}


def refresh_companies():
    global company_map

    company_tree.delete(*company_tree.get_children())
    company_map = {}

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, company_name, job_role, package_lpa,
               min_cgpa, eligible_branch, deadline
        FROM placement_companies
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        company_tree.insert("", "end", values=row)
        company_map[row[1]] = row[0]

    company_combo["values"] = list(company_map.keys())

    if company_map and company_combo.get() not in company_map:
        company_combo.current(0)


def refresh_applications():
    application_tree.delete(*application_tree.get_children())

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.id, a.student_name, a.student_email,
               c.company_name, c.job_role, c.package_lpa,
               a.status, a.applied_on
        FROM placement_applications a
        JOIN placement_companies c ON a.company_id = c.id
        ORDER BY a.id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        application_tree.insert("", "end", values=row)


def refresh_statistics():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM placement_companies")
    companies = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM placement_applications")
    applications = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM placement_applications
        WHERE status = 'Selected'
    """)
    selected = cursor.fetchone()[0]

    conn.close()

    stats_labels["Companies"].config(text=str(companies))
    stats_labels["Applications"].config(text=str(applications))
    stats_labels["Selected"].config(text=str(selected))


def refresh_all():
    refresh_companies()
    refresh_applications()
    refresh_statistics()


# ---------------- ADD COMPANY ----------------

def add_company():
    name = company_entries["name"].get().strip()
    role = company_entries["role"].get().strip()
    package = company_entries["package"].get().strip()
    cgpa = company_entries["cgpa"].get().strip()
    branch = company_entries["branch"].get().strip()
    deadline = company_entries["deadline"].get().strip()

    if not all([name, role, package, cgpa, branch, deadline]):
        messagebox.showwarning(
            "Missing Details",
            "Please fill in all company fields."
        )
        return

    try:
        package_value = float(package)
        cgpa_value = float(cgpa)

        if package_value < 0:
            raise ValueError("Package cannot be negative.")

        if not 0 <= cgpa_value <= 10:
            raise ValueError("CGPA must be between 0 and 10.")

        # Validate deadline format
        date.fromisoformat(deadline)

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO placement_companies
            (company_name, job_role, package_lpa,
             min_cgpa, eligible_branch, deadline)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name, role, package_value,
            cgpa_value, branch, deadline
        ))

        conn.commit()
        conn.close()

        for entry in company_entries.values():
            entry.delete(0, tk.END)

        refresh_all()

        messagebox.showinfo(
            "Success",
            f"{name} has been added successfully!"
        )

    except ValueError as error:
        messagebox.showerror(
            "Invalid Input",
            f"Check package, CGPA or deadline.\n{error}"
        )
    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


# ---------------- ADD APPLICATION ----------------

def add_application():
    selected_student = student_combo.get()
    student_data = student_map.get(selected_student)

    if not student_data:
        messagebox.showwarning(
            "Select Student",
            "Please select a registered student."
        )
        return

    student = student_data["name"]
    email = student_data["email"] or ""

    company_name = company_combo.get().strip()
    status = status_combo.get().strip()

    if not student or not email or not company_name:
        messagebox.showwarning(
            "Missing Details",
            "Enter student name, email and select a company."
        )
        return

    if "@" not in email or "." not in email.split("@")[-1]:
        messagebox.showwarning(
            "Invalid Email",
            "Please enter a valid email address."
        )
        return

    if status not in ["Applied", "Shortlisted", "Selected", "Rejected"]:
        messagebox.showwarning("Invalid Status", "Choose a valid status.")
        return

    company_id = company_map.get(company_name)

    if company_id is None:
        messagebox.showwarning(
            "No Company",
            "Please add a company before registering applications."
        )
        return

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO placement_applications
            (student_name, student_email, company_id, status, applied_on)
            VALUES (?, ?, ?, ?, ?)
        """, (
            student,
            email,
            company_id,
            status,
            date.today().isoformat()
        ))

        conn.commit()
        conn.close()

        application_entries["student"].delete(0, tk.END)
        application_entries["email"].delete(0, tk.END)
        status_combo.set("Applied")

        refresh_all()

        messagebox.showinfo(
            "Success",
            f"Application registered for {student}!"
        )

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


# ---------------- UPDATE APPLICATION STATUS ----------------

def update_application_status():
    selected_item = application_tree.selection()

    if not selected_item:
        messagebox.showwarning(
            "Select Application",
            "Select an application from the table first."
        )
        return

    selected_status = status_combo.get()

    if selected_status not in [
        "Applied", "Shortlisted", "Selected", "Rejected"
    ]:
        messagebox.showwarning(
            "Choose Status",
            "Please choose a valid status."
        )
        return

    application_id = application_tree.item(
        selected_item[0], "values"
    )[0]

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE placement_applications
            SET status = ?
            WHERE id = ?
        """, (selected_status, application_id))

        conn.commit()
        conn.close()

        refresh_all()

        messagebox.showinfo(
            "Updated",
            f"Application status changed to {selected_status}."
        )

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


def select_application(event=None):
    selected_item = application_tree.selection()

    if not selected_item:
        return

    values = application_tree.item(
        selected_item[0], "values"
    )

    status_combo.set(values[6])


application_tree.bind("<<TreeviewSelect>>", select_application)


# ---------------- BUTTONS ----------------

button_frame = tk.Frame(root, bg="#F1F5F9")
button_frame.pack(fill="x", padx=20, pady=(0, 12))

tk.Button(
    company_tab,
    text="Add Company",
    command=add_company,
    bg="#2563EB",
    fg="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    cursor="hand2",
    padx=18,
    pady=8
).pack(anchor="e", padx=15, pady=10)

application_buttons = tk.Frame(
    application_tab,
    bg="#F8FAFC"
)
application_buttons.pack(anchor="e", padx=15, pady=10)

tk.Button(
    application_buttons,
    text="Register Application",
    command=add_application,
    bg="#2563EB",
    fg="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    cursor="hand2",
    padx=12,
    pady=8
).pack(side="left", padx=5)

tk.Button(
    application_buttons,
    text="Update Selected Status",
    command=update_application_status,
    bg="#059669",
    fg="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    cursor="hand2",
    padx=12,
    pady=8
).pack(side="left", padx=5)

tk.Button(
    button_frame,
    text="Refresh All Data",
    command=refresh_all,
    bg="#172554",
    fg="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    cursor="hand2",
    padx=18,
    pady=9
).pack(side="right")

# Load initial data
refresh_all()
load_students()
root.mainloop()