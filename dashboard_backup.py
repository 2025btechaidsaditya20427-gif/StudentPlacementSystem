import tkinter as tk
from tkinter import messagebox
import sqlite3
def open_attendance():
    import subprocess
    import sys
    import os

    attendance_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "attendance.py"
    )

    try:
        subprocess.Popen(
            [sys.executable, attendance_file],
            cwd=os.path.dirname(attendance_file)
        )
    except Exception as e:
        messagebox.showerror(
            "Error",
            f"Could not open Attendance:\n{e}"
        )

def open_placements():
    import subprocess
    import sys
    import os

    placement_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "placement.py"
    )

    try:
        subprocess.Popen(
            [sys.executable, placement_file],
            cwd=os.path.dirname(placement_file)
        )
    except Exception as e:
        messagebox.showerror(
            "Error",
            f"Could not open Placement Management:\n{e}"
        )
def get_student_count():
    try:
        conn = sqlite3.connect("college.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM students")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except sqlite3.Error:
        return 0
def get_attendance_stats():
    from datetime import date
    import os

    db_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "college.db"
    )

    present = 0
    absent = 0

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT status
            FROM attendance
            WHERE attendance_date = ?
            """,
            (date.today().isoformat(),)
        )

        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            if row[0].lower() == "present":
                present += 1
            elif row[0].lower() == "absent":
                absent += 1

    except sqlite3.Error as e:
        print("Attendance statistics error:", e)

    return present, absent

def get_latest_students():
    try:
        conn = sqlite3.connect("college.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, email, course FROM students ORDER BY id DESC LIMIT 5"
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
    except sqlite3.Error:
        return []

def show_message(section):
    messagebox.showinfo(
        section,
        f"{section} section will be added in the next steps."
    )


def open_students():
    import subprocess
    import sys
    import os

    main_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")

    try:
        subprocess.Popen([sys.executable, main_file])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open Student Management:\n{e}")


def refresh_dashboard():
    student_count = get_student_count()
    present_count, absent_count = get_attendance_stats()

    values = [student_count, present_count, absent_count]

    for label, value in zip(card_values, values):
        animate_number(label, value)

    messagebox.showinfo(
        "Updated",
        "Dashboard statistics refreshed successfully!"
    )

def make_nav_button(parent, text, command, active=False):
    button = tk.Button(
        parent,
        text=text,
        command=command,
        font=("Arial", 12),
        anchor="w",
        padx=20,
        pady=12,
        bd=0,
        cursor="hand2",
        bg="#2563EB" if active else "#172554",
        fg="white",
        activebackground="#2563EB",
        activeforeground="white"
    )
    button.pack(fill="x", padx=12, pady=4)


def make_action_button(parent, text, command):
    button = tk.Button(
        parent,
        text=text,
        command=command,
        font=("Arial", 11, "bold"),
        padx=18,
        pady=12,
        bd=0,
        cursor="hand2",
        bg="#2563EB",
        fg="white",
        activebackground="#1D4ED8",
        activeforeground="white"
    )
    button.pack(side="left", padx=(0, 12))


# ---------------- Main window ----------------
root = tk.Tk()
root.title("College Management System")
root.geometry("1000x650")
root.configure(bg="#F3F5F9")
root.minsize(850, 550)

# ---------------- Sidebar ----------------
sidebar = tk.Frame(root, bg="#172554", width=220)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

tk.Label(
    sidebar,
    text="COLLEGE\nMANAGER",
    font=("Arial", 19, "bold"),
    bg="#172554",
    fg="white",
    justify="left"
).pack(anchor="w", padx=22, pady=(30, 40))

make_nav_button(sidebar, "Dashboard", lambda: show_message("Dashboard"), True)
make_nav_button(sidebar, "Students", open_students)
make_nav_button(sidebar, "Attendance", open_attendance)
make_nav_button(sidebar, "Placements", open_placements)
make_nav_button(sidebar, "Reports", lambda: show_message("Reports"))

tk.Label(
    sidebar,
    text="Student Placement System",
    font=("Arial", 9),
    bg="#172554",
    fg="#CBD5E1",
    wraplength=180
).pack(side="bottom", anchor="w", padx=18, pady=20)

# ---------------- Main content ----------------
content = tk.Frame(root, bg="#F3F5F9")
content.pack(side="left", fill="both", expand=True, padx=30, pady=25)

tk.Label(
    content,
    text="Dashboard",
    font=("Arial", 25, "bold"),
    bg="#F3F5F9",
    fg="#1E293B"
).pack(anchor="w")

tk.Label(
    content,
    text="Welcome! Here is your college overview.",
    font=("Arial", 11),
    bg="#F3F5F9",
    fg="#64748B"
).pack(anchor="w", pady=(5, 25))

# ---------------- Statistics cards ----------------
# ---------------- Animated Statistics Cards ----------------

cards_frame = tk.Frame(content, bg="#F3F5F9")
cards_frame.pack(fill="x")

student_count = get_student_count()
present_count, absent_count = get_attendance_stats()

card_colors = [
    ("#2563EB", "#1D4ED8"),
    ("#059669", "#047857"),
    ("#EA580C", "#C2410C")
]

card_values = []

card_data = [
    ("Total Students", student_count, "Registered students"),
    ("Present Today", present_count, "Students present today"),
    ("Absent Today", absent_count, "Students absent today")
]

for index, (title, value, description) in enumerate(card_data):

    normal_color, hover_color = card_colors[index]

    card = tk.Frame(
        cards_frame,
        bg=normal_color,
        highlightthickness=0
    )

    card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(0, 12),
        ipady=12
    )

    tk.Label(
        card,
        text=title,
        font=("Arial", 11, "bold"),
        bg=normal_color,
        fg="white"
    ).pack(anchor="w", padx=16, pady=(15, 8))

    value_label = tk.Label(
        card,
        text="0",
        font=("Arial", 25, "bold"),
        bg=normal_color,
        fg="white"
    )

    value_label.pack(anchor="w", padx=16, pady=3)

    tk.Label(
        card,
        text=description,
        font=("Arial", 9),
        bg=normal_color,
        fg="#E0F2FE"
    ).pack(anchor="w", padx=16, pady=(4, 12))

    card_values.append(value_label)

    # Hover animation
    def make_hover(widget, normal, hover):
        def on_enter(event):
            widget.configure(bg=hover)
            for child in widget.winfo_children():
                child.configure(bg=hover)

        def on_leave(event):
            widget.configure(bg=normal)
            for child in widget.winfo_children():
                child.configure(bg=normal)

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

        for child in widget.winfo_children():
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)

    make_hover(card, normal_color, hover_color)


# ---------------- Number Count Animation ----------------

def animate_number(label, target, current=0):
    if current < target:
        step = max(1, target // 20)
        current = min(current + step, target)

        label.configure(text=str(current))
        root.after(35, animate_number, label, target, current)
    else:
        label.configure(text=str(target))


for label, (_, value, _) in zip(card_values, card_data):
    animate_number(label, value)

# ---------------- Attendance Progress Bar ----------------

attendance_frame = tk.Frame(
    content,
    bg="white",
    highlightbackground="#E2E8F0",
    highlightthickness=1
)

attendance_frame.pack(fill="x", pady=(20, 0))

tk.Label(
    attendance_frame,
    text="Today's Attendance Overview",
    font=("Arial", 14, "bold"),
    bg="white",
    fg="#1E293B"
).pack(anchor="w", padx=18, pady=(15, 8))

total_attendance = present_count + absent_count

if total_attendance > 0:
    attendance_percentage = round(
        (present_count / total_attendance) * 100
    )
else:
    attendance_percentage = 0

percentage_label = tk.Label(
    attendance_frame,
    text="0%",
    font=("Arial", 20, "bold"),
    bg="white",
    fg="#2563EB"
)
percentage_label.pack(anchor="w", padx=18)

# Progress bar background
progress_bg = tk.Frame(
    attendance_frame,
    bg="#E2E8F0",
    height=16
)
progress_bg.pack(fill="x", padx=18, pady=(8, 5))
progress_bg.pack_propagate(False)

progress_fill = tk.Frame(
    progress_bg,
    bg="#2563EB",
    width=0,
    height=16
)
progress_fill.place(x=0, y=0)

tk.Label(
    attendance_frame,
    text=f"{present_count} Present  |  {absent_count} Absent",
    font=("Arial", 10),
    bg="white",
    fg="#64748B"
).pack(anchor="w", padx=18, pady=(5, 15))


def animate_attendance(current=0):
    if current <= attendance_percentage:
        percentage_label.config(text=f"{current}%")

        progress_bg.update_idletasks()
        max_width = progress_bg.winfo_width()
        fill_width = int(max_width * current / 100)

        progress_fill.place_configure(width=fill_width)

        if current < attendance_percentage:
            attendance_frame.after(
                20,
                animate_attendance,
                current + 1
            )


attendance_frame.after(300, animate_attendance)
# ---------------- Latest Students ----------------
tk.Label(
    content,
    text="Latest Students",
    font=("Arial", 17, "bold"),
    bg="#F3F5F9",
    fg="#1E293B"
).pack(anchor="w", pady=(30, 12))

students_frame = tk.Frame(
    content,
    bg="white",
    highlightbackground="#E2E8F0",
    highlightthickness=1
)
students_frame.pack(fill="x", pady=(0, 10))

latest_students = get_latest_students()

if latest_students:
    for name, email, course in latest_students:
        student_row = tk.Frame(students_frame, bg="white")
        student_row.pack(fill="x", padx=15, pady=10)

        tk.Label(
            student_row,
            text=name,
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#1E293B",
            width=18,
            anchor="w"
        ).pack(side="left")

        tk.Label(
            student_row,
            text=email,
            font=("Arial", 10),
            bg="white",
            fg="#64748B",
            anchor="w"
        ).pack(side="left", padx=10)

        tk.Label(
            student_row,
            text=course,
            font=("Arial", 10),
            bg="white",
            fg="#2563EB",
            anchor="e"
        ).pack(side="right", padx=10)
else:
    tk.Label(
        students_frame,
        text="No students found. Add a student to see them here.",
        font=("Arial", 11),
        bg="white",
        fg="#64748B"
    ).pack(anchor="w", padx=15, pady=18)
# ---------------- Quick actions ----------------
tk.Label(
    content,
    text="Quick Actions",
    font=("Arial", 17, "bold"),
    bg="#F3F5F9",
    fg="#1E293B"
).pack(anchor="w", pady=(35, 15))

actions_frame = tk.Frame(content, bg="#F3F5F9")
actions_frame.pack(anchor="w", fill="x")

make_action_button(actions_frame, "Manage Students", open_students)
make_action_button(actions_frame, "Refresh Dashboard", refresh_dashboard)

root.mainloop()