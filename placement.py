import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from pathlib import Path
import random

# ---------------- DATABASE ----------------

DB_PATH = Path(__file__).resolve().parent / "college.db"


def connect_db():
    return sqlite3.connect(DB_PATH)


def setup_database():
    with connect_db() as conn:
        cursor = conn.cursor()

        # Separate table names protect any existing placement tables.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS placement_companies_ui (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                role TEXT NOT NULL,
                package TEXT,
                location TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS placement_applications_ui (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                student_email TEXT,
                company_name TEXT NOT NULL,
                status TEXT DEFAULT 'Applied'
            )
        """)


# ---------------- STUDENT DATA ----------------

def load_student_records():
    """Read student names/emails from the existing students table."""
    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
            """)

            tables = [row[0] for row in cursor.fetchall()]

            if "students" not in tables:
                return []

            cursor.execute("PRAGMA table_info(students)")
            columns = [row[1] for row in cursor.fetchall()]
            lower_columns = {column.lower(): column for column in columns}

            name_column = next(
                (
                    lower_columns[key]
                    for key in ("name", "student_name", "fullname", "full_name")
                    if key in lower_columns
                ),
                None
            )

            email_column = next(
                (
                    lower_columns[key]
                    for key in ("email", "student_email", "email_id")
                    if key in lower_columns
                ),
                None
            )

            if not name_column:
                return []

            if email_column:
                query = (
                    f'SELECT "{name_column}", "{email_column}" '
                    f'FROM students ORDER BY "{name_column}"'
                )
            else:
                query = (
                    f'SELECT "{name_column}", NULL '
                    f'FROM students ORDER BY "{name_column}"'
                )

            cursor.execute(query)

            return [
                (str(row[0]), str(row[1] or ""))
                for row in cursor.fetchall()
                if row[0]
            ]

    except sqlite3.Error as error:
        print("Student database error:", error)
        return []


# ---------------- MAIN WINDOW ----------------

setup_database()

root = tk.Tk()
root.title("Placement Pro | College Management")
root.geometry("1180x760")
root.minsize(950, 650)
root.configure(bg="#F2F5FC")


# ---------------- COLORS ----------------

BG = "#F2F5FC"
NAVY = "#172554"
BLUE = "#2563EB"
PURPLE = "#7C3AED"
GREEN = "#059669"
WHITE = "#FFFFFF"
TEXT = "#1E293B"
MUTED = "#64748B"


# ---------------- STYLE ----------------

style = ttk.Style()

try:
    style.theme_use("clam")
except tk.TclError:
    pass

style.configure(
    "Treeview",
    background=WHITE,
    foreground=TEXT,
    rowheight=34,
    fieldbackground=WHITE,
    font=("Arial", 10)
)

style.configure(
    "Treeview.Heading",
    background="#E8EEFC",
    foreground=NAVY,
    font=("Arial", 10, "bold"),
    padding=9
)

style.map(
    "Treeview",
    background=[("selected", "#DBEAFE")],
    foreground=[("selected", NAVY)]
)

style.configure(
    "TNotebook",
    background=BG,
    borderwidth=0
)

style.configure(
    "TNotebook.Tab",
    padding=(18, 11),
    font=("Arial", 10, "bold")
)

style.map(
    "TNotebook.Tab",
    background=[("selected", WHITE)],
    foreground=[("selected", BLUE)]
)


# ---------------- HELPER FUNCTIONS ----------------

def create_button(parent, text, command, color=BLUE):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=color,
        fg="white",
        activebackground=color,
        activeforeground="white",
        font=("Arial", 10, "bold"),
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=16,
        pady=10
    )


def create_label(parent, text, size=10, color=TEXT, bold=False):
    return tk.Label(
        parent,
        text=text,
        bg=parent.cget("bg"),
        fg=color,
        font=("Arial", size, "bold" if bold else "normal")
    )


# ---------------- HEADER ----------------

header = tk.Frame(root, bg=NAVY, height=115)
header.pack(fill="x")
header.pack_propagate(False)

header_left = tk.Frame(header, bg=NAVY)
header_left.pack(side="left", padx=28, pady=20)

tk.Label(
    header_left,
    text="PLACEMENT PRO",
    bg=NAVY,
    fg="white",
    font=("Arial", 23, "bold")
).pack(anchor="w")

tk.Label(
    header_left,
    text="College Placement Management System",
    bg=NAVY,
    fg="#CBD5E1",
    font=("Arial", 11)
).pack(anchor="w", pady=(5, 0))

clock_label = tk.Label(
    header,
    text="",
    bg=NAVY,
    fg="#BFDBFE",
    font=("Arial", 11, "bold")
)
clock_label.pack(side="right", padx=28)


def update_clock():
    from datetime import datetime

    clock_label.config(
        text=datetime.now().strftime("%d %b %Y  |  %I:%M:%S %p")
    )

    root.after(1000, update_clock)


update_clock()


# ---------------- WELCOME BANNER ----------------

welcome = tk.Frame(root, bg=WHITE, padx=22, pady=16)
welcome.pack(fill="x", padx=22, pady=(18, 12))

tk.Label(
    welcome,
    text="Welcome to your Placement Dashboard!",
    bg=WHITE,
    fg=NAVY,
    font=("Arial", 16, "bold")
).pack(anchor="w")

tk.Label(
    welcome,
    text="Manage companies, student applications and placement progress.",
    bg=WHITE,
    fg=MUTED,
    font=("Arial", 10)
).pack(anchor="w", pady=(5, 0))


# ---------------- STATISTICS CARDS ----------------

stats_frame = tk.Frame(root, bg=BG)
stats_frame.pack(fill="x", padx=22, pady=5)

stats_data = [
    ("Companies", "0", BLUE),
    ("Applications", "0", PURPLE),
    ("Selected Students", "0", GREEN)
]

stats_labels = {}

for title, value, color in stats_data:
    card = tk.Frame(
        stats_frame,
        bg=WHITE,
        padx=18,
        pady=15,
        highlightthickness=1,
        highlightbackground="#E2E8F0"
    )

    card.pack(side="left", fill="both", expand=True, padx=6)

    tk.Label(
        card,
        text=title.upper(),
        bg=WHITE,
        fg=MUTED,
        font=("Arial", 9, "bold")
    ).pack(anchor="w")

    number = tk.Label(
        card,
        text=value,
        bg=WHITE,
        fg=color,
        font=("Arial", 25, "bold")
    )

    number.pack(anchor="w", pady=(7, 0))
    stats_labels[title] = number


# ---------------- PROGRESS BAR ----------------

progress_frame = tk.Frame(root, bg=WHITE, padx=20, pady=13)
progress_frame.pack(fill="x", padx=28, pady=(12, 14))

progress_heading = tk.Frame(progress_frame, bg=WHITE)
progress_heading.pack(fill="x")

tk.Label(
    progress_heading,
    text="Placement Progress",
    bg=WHITE,
    fg=NAVY,
    font=("Arial", 11, "bold")
).pack(side="left")

progress_text = tk.Label(
    progress_heading,
    text="0% selection rate",
    bg=WHITE,
    fg=GREEN,
    font=("Arial", 10, "bold")
)
progress_text.pack(side="right")

progress_bar = ttk.Progressbar(
    progress_frame,
    maximum=100,
    mode="determinate"
)
progress_bar.pack(fill="x", pady=(10, 0))


# ---------------- NOTEBOOK ----------------

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=22, pady=(0, 18))

company_tab = tk.Frame(notebook, bg=WHITE)
application_tab = tk.Frame(notebook, bg=WHITE)

notebook.add(company_tab, text="  Company Management  ")
notebook.add(application_tab, text="  Student Applications  ")


# ---------------- COMPANY TAB ----------------

company_heading = tk.Frame(company_tab, bg=WHITE)
company_heading.pack(fill="x", padx=20, pady=(18, 8))

tk.Label(
    company_heading,
    text="Company Management",
    bg=WHITE,
    fg=NAVY,
    font=("Arial", 16, "bold")
).pack(anchor="w")

tk.Label(
    company_heading,
    text="Add and manage companies visiting your college.",
    bg=WHITE,
    fg=MUTED,
    font=("Arial", 10)
).pack(anchor="w", pady=(4, 0))


company_form = tk.Frame(company_tab, bg="#F8FAFC", padx=15, pady=14)
company_form.pack(fill="x", padx=20, pady=8)

company_entries = {}

company_fields = [
    ("Company Name", "company_name"),
    ("Job Role", "role"),
    ("Package (e.g. 6 LPA)", "package"),
    ("Location", "location")
]

for index, (label_text, key) in enumerate(company_fields):
    column = index % 2
    row = index // 2

    field = tk.Frame(company_form, bg="#F8FAFC")
    field.grid(
        row=row,
        column=column,
        sticky="ew",
        padx=8,
        pady=7
    )

    tk.Label(
        field,
        text=label_text,
        bg="#F8FAFC",
        fg=TEXT,
        font=("Arial", 10, "bold")
    ).pack(anchor="w", pady=(0, 5))

    entry = tk.Entry(
        field,
        font=("Arial", 11),
        relief="solid",
        bd=1
    )
    entry.pack(fill="x", ipady=6)

    company_entries[key] = entry

company_form.columnconfigure(0, weight=1)
company_form.columnconfigure(1, weight=1)


def refresh_companies():
    for item in company_tree.get_children():
        company_tree.delete(item)

    with connect_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, company_name, role, package, location
            FROM placement_companies_ui
            ORDER BY id DESC
        """)

        for row in cursor.fetchall():
            company_tree.insert("", "end", values=row)

        cursor.execute("""
            SELECT company_name
            FROM placement_companies_ui
            ORDER BY company_name
        """)

        company_names = [row[0] for row in cursor.fetchall()]

    company_combo["values"] = company_names

    if company_combo.get() not in company_names:
        company_combo.set("")

    refresh_statistics()


def add_company():
    name = company_entries["company_name"].get().strip()
    role = company_entries["role"].get().strip()
    package = company_entries["package"].get().strip()
    location = company_entries["location"].get().strip()

    if not name or not role:
        messagebox.showwarning(
            "Missing Information",
            "Please enter both Company Name and Job Role."
        )
        return

    try:
        with connect_db() as conn:
            conn.execute("""
                INSERT INTO placement_companies_ui
                (company_name, role, package, location)
                VALUES (?, ?, ?, ?)
            """, (name, role, package, location))

        for entry in company_entries.values():
            entry.delete(0, "end")

        refresh_companies()

        messagebox.showinfo(
            "Success",
            "Company added successfully!"
        )

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


company_buttons = tk.Frame(company_tab, bg=WHITE)
company_buttons.pack(fill="x", padx=28, pady=5)

create_button(
    company_buttons,
    "+ Add Company",
    add_company,
    GREEN
).pack(side="left")


# ---------------- COMPANY TABLE ----------------

company_table_frame = tk.Frame(company_tab, bg=WHITE)
company_table_frame.pack(
    fill="both",
    expand=True,
    padx=25,
    pady=(10, 20)
)

company_columns = (
    "ID",
    "Company",
    "Job Role",
    "Package",
    "Location"
)

company_tree = ttk.Treeview(
    company_table_frame,
    columns=company_columns,
    show="headings"
)

for column in company_columns:
    company_tree.heading(column, text=column)
    company_tree.column(column, width=150, anchor="center")

company_tree.column("ID", width=55)
company_tree.column("Company", width=190)

company_scroll = ttk.Scrollbar(
    company_table_frame,
    orient="vertical",
    command=company_tree.yview
)

company_tree.configure(yscrollcommand=company_scroll.set)

company_tree.pack(side="left", fill="both", expand=True)
company_scroll.pack(side="right", fill="y")


# ---------------- APPLICATION TAB ----------------

app_heading = tk.Frame(application_tab, bg=WHITE)
app_heading.pack(fill="x", padx=20, pady=(18, 8))

tk.Label(
    app_heading,
    text="Student Application Tracker",
    bg=WHITE,
    fg=NAVY,
    font=("Arial", 16, "bold")
).pack(anchor="w")

tk.Label(
    app_heading,
    text="Select a student, choose a company and track application status.",
    bg=WHITE,
    fg=MUTED,
    font=("Arial", 10)
).pack(anchor="w", pady=(4, 0))


app_form = tk.Frame(application_tab, bg="#F8FAFC", padx=15, pady=14)
app_form.pack(fill="x", padx=20, pady=8)


# Student dropdown

tk.Label(
    app_form,
    text="Student Name",
    bg="#F8FAFC",
    fg=TEXT,
    font=("Arial", 10, "bold")
).grid(row=0, column=0, sticky="w", padx=8, pady=(4, 5))

student_combo = ttk.Combobox(
    app_form,
    state="readonly",
    font=("Arial", 10)
)
student_combo.grid(
    row=1,
    column=0,
    sticky="ew",
    padx=8,
    pady=(0, 12),
    ipady=5
)


# Email field

tk.Label(
    app_form,
    text="Student Email",
    bg="#F8FAFC",
    fg=TEXT,
    font=("Arial", 10, "bold")
).grid(row=0, column=1, sticky="w", padx=8, pady=(4, 5))

email_var = tk.StringVar()

email_entry = tk.Entry(
    app_form,
    textvariable=email_var,
    state="readonly",
    readonlybackground="#E2E8F0",
    font=("Arial", 10),
    relief="solid",
    bd=1
)

email_entry.grid(
    row=1,
    column=1,
    sticky="ew",
    padx=8,
    pady=(0, 12),
    ipady=7
)


# Company dropdown

tk.Label(
    app_form,
    text="Company",
    bg="#F8FAFC",
    fg=TEXT,
    font=("Arial", 10, "bold")
).grid(row=2, column=0, sticky="w", padx=8, pady=(4, 5))

company_combo = ttk.Combobox(
    app_form,
    state="readonly",
    font=("Arial", 10)
)
company_combo.grid(
    row=3,
    column=0,
    sticky="ew",
    padx=8,
    pady=(0, 12),
    ipady=5
)


# Status dropdown

tk.Label(
    app_form,
    text="Application Status",
    bg="#F8FAFC",
    fg=TEXT,
    font=("Arial", 10, "bold")
).grid(row=2, column=1, sticky="w", padx=8, pady=(4, 5))

status_combo = ttk.Combobox(
    app_form,
    state="readonly",
    values=[
        "Applied",
        "Shortlisted",
        "Interview",
        "Selected",
        "Rejected"
    ],
    font=("Arial", 10)
)

status_combo.set("Applied")

status_combo.grid(
    row=3,
    column=1,
    sticky="ew",
    padx=8,
    pady=(0, 12),
    ipady=5
)

app_form.columnconfigure(0, weight=1)
app_form.columnconfigure(1, weight=1)


# ---------------- STUDENT DROPDOWN LOGIC ----------------

student_email_map = {}


def load_students():
    global student_email_map

    records = load_student_records()

    student_email_map = {
        name: email for name, email in records
    }

    student_combo["values"] = list(student_email_map.keys())

    if student_combo.get() not in student_email_map:
        student_combo.set("")

    email_var.set("")


def on_student_selected(event=None):
    selected_name = student_combo.get()
    email_var.set(student_email_map.get(selected_name, ""))


student_combo.bind("<<ComboboxSelected>>", on_student_selected)


# ---------------- ADD APPLICATION ----------------

def add_application():
    student = student_combo.get().strip()
    email = email_var.get().strip()
    company = company_combo.get().strip()
    status = status_combo.get().strip()

    if not student:
        messagebox.showwarning(
            "Select Student",
            "Please select a student from the dropdown."
        )
        return

    if not company:
        messagebox.showwarning(
            "Select Company",
            "Please add and select a company first."
        )
        return

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id
                FROM placement_applications_ui
                WHERE student_name = ? AND company_name = ?
            """, (student, company))

            if cursor.fetchone():
                messagebox.showwarning(
                    "Already Exists",
                    "This student already has an application for this company."
                )
                return

            cursor.execute("""
                INSERT INTO placement_applications_ui
                (student_name, student_email, company_name, status)
                VALUES (?, ?, ?, ?)
            """, (student, email, company, status))

        refresh_applications()

        messagebox.showinfo(
            "Success",
            "Student application added successfully!"
        )

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


create_button(
    app_form,
    "+ Add Application",
    add_application,
    BLUE
).grid(
    row=4,
    column=0,
    columnspan=2,
    sticky="ew",
    padx=8,
    pady=(3, 5)
)


# ---------------- APPLICATION TABLE ----------------

app_table_frame = tk.Frame(application_tab, bg=WHITE)
app_table_frame.pack(
    fill="both",
    expand=True,
    padx=25,
    pady=(10, 20)
)

app_columns = (
    "ID",
    "Student",
    "Email",
    "Company",
    "Status"
)

app_tree = ttk.Treeview(
    app_table_frame,
    columns=app_columns,
    show="headings"
)

for column in app_columns:
    app_tree.heading(column, text=column)
    app_tree.column(column, width=150, anchor="center")

app_tree.column("ID", width=50)
app_tree.column("Student", width=160)
app_tree.column("Email", width=200)
app_tree.column("Company", width=170)
app_tree.column("Status", width=115)

app_scroll = ttk.Scrollbar(
    app_table_frame,
    orient="vertical",
    command=app_tree.yview
)

app_tree.configure(yscrollcommand=app_scroll.set)

app_tree.pack(side="left", fill="both", expand=True)
app_scroll.pack(side="right", fill="y")


# ---------------- REFRESH APPLICATIONS ----------------

def refresh_applications():
    for item in app_tree.get_children():
        app_tree.delete(item)

    with connect_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, student_name, student_email, company_name, status
            FROM placement_applications_ui
            ORDER BY id DESC
        """)

        for row in cursor.fetchall():
            app_tree.insert("", "end", values=row)

    refresh_statistics()


# ---------------- UPDATE APPLICATION STATUS ----------------

def update_application_status():
    selected = app_tree.selection()

    if not selected:
        messagebox.showwarning(
            "Select Application",
            "Please select an application from the table."
        )
        return

    new_status = status_combo.get().strip()

    if not new_status:
        messagebox.showwarning(
            "Select Status",
            "Please select a status first."
        )
        return

    item = app_tree.item(selected[0])
    application_id = item["values"][0]

    try:
        with connect_db() as conn:
            conn.execute("""
                UPDATE placement_applications_ui
                SET status = ?
                WHERE id = ?
            """, (new_status, application_id))

        refresh_applications()

        messagebox.showinfo(
            "Updated",
            "Application status updated successfully!"
        )

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


create_button(
    application_tab,
    "Update Selected Application Status",
    update_application_status,
    PURPLE
).pack(anchor="w", padx=25, pady=(0, 15))


# ---------------- STATISTICS ----------------

def refresh_statistics():
    with connect_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM placement_companies_ui
        """)
        companies = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM placement_applications_ui
        """)
        applications = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM placement_applications_ui
            WHERE status = 'Selected'
        """)
        selected = cursor.fetchone()[0]

    stats_labels["Companies"].config(text=str(companies))
    stats_labels["Applications"].config(text=str(applications))
    stats_labels["Selected Students"].config(text=str(selected))

    rate = (selected / applications * 100) if applications else 0

    progress_bar["value"] = rate
    progress_text.config(text=f"{rate:.1f}% selection rate")


# ---------------- ANIMATED HEADER ----------------

animation_colors = ["#BFDBFE", "#DDD6FE", "#A7F3D0", "#FDE68A"]
color_index = 0


def animate_header():
    global color_index

    header_left.winfo_children()[0].config(
        fg=animation_colors[color_index]
    )

    color_index = (color_index + 1) % len(animation_colors)

    root.after(900, animate_header)


# ---------------- REFRESH ALL ----------------

def refresh_all():
    refresh_companies()
    refresh_applications()
    load_students()


# ---------------- FOOTER ----------------

footer = tk.Label(
    root,
    text="PLACEMENT PRO  |  Student Career & Placement Management",
    bg=BG,
    fg=MUTED,
    font=("Arial", 9)
)
footer.pack(side="bottom", pady=(0, 8))


# ---------------- START APPLICATION ----------------

refresh_all()
animate_header()

root.mainloop()