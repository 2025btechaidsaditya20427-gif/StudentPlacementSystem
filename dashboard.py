import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import subprocess
import sys
from smart_AI import get_smart_attendance_summary, open_smart_attendance
from pathlib import Path
from datetime import date
from ask_college_data import open_ask_college_data

def open_ask_college_data():
    try:
        script_path = Path(__file__).parent / "ask_college_data.py"

        if not script_path.exists():
            messagebox.showerror(
                "File Not Found",
                "ask_college_data.py file project folder mein nahi mili."
            )
            return

        subprocess.Popen([sys.executable, str(script_path)])

    except Exception as error:
        messagebox.showerror("Error", str(error))
# =====================================================
# CONFIGURATION
# =====================================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "college.db"

BG = "#F4F7FC"
WHITE = "#CDC4C4"
NAVY = "#202E55"
NAVY_LIGHT = "#1B2B50"
BLUE = "#3978F6"
BLUE_HOVER = "#2864DC"
CYAN = "#27C5E8"
GREEN = "#10B981"
ORANGE = "#F59E0B"
RED = "#EF4444"
TEXT = "#17233F"
MUTED = "#7A879E"
BORDER = "#E5EAF3"


# =====================================================
# DATABASE FUNCTIONS
# =====================================================

def get_connection():
    return sqlite3.connect(str(DB_PATH), timeout=5)


def get_student_count():
    try:
        with get_connection() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM students"
            ).fetchone()[0]
    except sqlite3.Error as error:
        print("Student database error:", error)
        return 0


def get_attendance_stats():
    present = 0
    absent = 0

    try:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT LOWER(status), COUNT(*)
                FROM attendance
                WHERE attendance_date = ?
                GROUP BY LOWER(status)
                """,
                (date.today().isoformat(),)
            ).fetchall()

        for status, count in rows:
            if status == "present":
                present = count
            elif status == "absent":
                absent = count

    except sqlite3.Error as error:
        print("Attendance database error:", error)

    return present, absent
def get_attendance_risk(student_id):
    """Calculate attendance percentage and risk status."""

    try:
        with get_connection() as conn:
            result = conn.execute("""
                SELECT
                    COUNT(*),
                    SUM(
                        CASE
                            WHEN LOWER(status) = 'present' THEN 1
                            ELSE 0
                        END
                    )
                FROM attendance
                WHERE student_id = ?
            """, (student_id,)).fetchone()

        total = result[0] or 0
        present = result[1] or 0

        if total == 0:
            return 0.0, "No Records"

        percentage = (present / total) * 100

        if percentage < 75:
            status = "Low Attendance"
        else:
            status = "Safe"

        return round(percentage, 1), status

    except sqlite3.Error:
        return 0.0, "Data Error"


def get_low_attendance_count():
    try:
        with get_connection() as conn:
            students = conn.execute(
                "SELECT id FROM students"
            ).fetchall()

        low_count = 0

        for (student_id,) in students:
            percentage, status = get_attendance_risk(student_id)

            if status == "Low Attendance":
                low_count += 1

        return low_count

    except sqlite3.Error:
        return 0

    try:
        with get_connection() as conn:
            result = conn.execute("""
                SELECT
                    COUNT(*),
                    SUM(
                        CASE
                            WHEN LOWER(status) = 'present' THEN 1
                            ELSE 0
                        END
                    )
                FROM attendance
                WHERE student_id = ?
            """, (student_id,)).fetchone()

        total = result[0] or 0
        present = result[1] or 0

        if total == 0:
            return 0.0, "No Records"

        percentage = (present / total) * 100

        if percentage < 75:
            status = "Low Attendance"
        else:
            status = "Safe"

        return round(percentage, 1), status

    except sqlite3.Error:
        return 0.0, "Data Error"

def get_latest_students():
    try:
        with get_connection() as conn:
            return conn.execute(
                """
                SELECT name, email, course
                FROM students
                ORDER BY id DESC
                LIMIT 5
                """
            ).fetchall()

    except sqlite3.Error as error:
        print("Latest students error:", error)
        return []


# =====================================================
# OPEN OTHER MODULES
# =====================================================

def open_module(filename, module_name):
    module_path = BASE_DIR / filename

    if not module_path.is_file():
        messagebox.showerror(
            "Module Not Found",
            f"{module_name} file was not found:\n{module_path}"
        )
        return

    try:
        subprocess.Popen(
            [sys.executable, str(module_path)],
            cwd=str(BASE_DIR)
        )

        set_status(f"{module_name} opened successfully.")

    except Exception as error:
        messagebox.showerror(
            "Launch Error",
            f"Could not open {module_name}:\n{error}"
        )


def open_students():
    open_module("main.py", "Student Management")


def open_attendance():
    open_module("attendance.py", "Attendance Management")


def open_placements():
    open_module("placement.py", "Placement Management")


# =====================================================
# ROOT WINDOW
# =====================================================

root = tk.Tk()
root.title("College Management System | Dashboard")
root.geometry("1150x780")
root.minsize(950, 680)
root.configure(bg=BG)

root.update_idletasks()

screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()

window_w = min(1150, screen_w - 60)
window_h = min(780, screen_h - 80)

x = max(0, (screen_w - window_w) // 2)
y = max(0, (screen_h - window_h) // 2)

root.geometry(f"{window_w}x{window_h}+{x}+{y}")


# =====================================================
# TTK TABLE STYLE
# =====================================================

style = ttk.Style(root)
style.theme_use("clam")

style.configure(
    "Students.Treeview",
    background=WHITE,
    foreground=TEXT,
    fieldbackground=WHITE,
    rowheight=34,
    borderwidth=0,
    font=("Arial", 10)
)

style.configure(
    "Students.Treeview.Heading",
    background="#EDF2FA",
    foreground=TEXT,
    font=("Arial", 10, "bold"),
    relief="flat",
    padding=9
)

style.map(
    "Students.Treeview",
    background=[("selected", "#DCE9FF")],
    foreground=[("selected", TEXT)]
)


# =====================================================
# MAIN LAYOUT
# =====================================================

sidebar = tk.Frame(root, bg="#111C3A", width=245)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

main_area = tk.Frame(root, bg=BG)
main_area.pack(side="left", fill="both", expand=True)

# Scrollable content area
content_canvas = tk.Canvas(
    main_area,
    bg=BG,
    highlightthickness=0,
    bd=0
)
content_scrollbar = ttk.Scrollbar(
    main_area,
    orient="vertical",
    command=content_canvas.yview
)

content_canvas.pack(side="left", fill="both", expand=True)
content_scrollbar.pack(side="right", fill="y")

content_canvas.configure(
    yscrollcommand=content_scrollbar.set
)

content = tk.Frame(content_canvas, bg=BG)

content_window = content_canvas.create_window(
    (0, 0),
    window=content,
    anchor="nw"
)


def update_scroll_region(event=None):
    content_canvas.configure(
        scrollregion=content_canvas.bbox("all")
    )


def resize_content(event):
    content_canvas.itemconfigure(
        content_window,
        width=event.width
    )


content.bind("<Configure>", update_scroll_region)
content_canvas.bind("<Configure>", resize_content)


# Mouse-wheel scrolling on the content
def on_mousewheel(event):
    if event.delta:
        content_canvas.yview_scroll(
            int(-event.delta / 120),
            "units"
        )


content_canvas.bind("<MouseWheel>", on_mousewheel)


# =====================================================
# STATUS BAR
# =====================================================

status_var = tk.StringVar(
    value="Dashboard ready."
)


def set_status(message):
    status_var.set(message)


# =====================================================
# SIDEBAR HEADER
# =====================================================

logo_frame = tk.Frame(sidebar, bg=NAVY)
logo_frame.pack(fill="x", padx=20, pady=(28, 35))

tk.Label(
    logo_frame,
    text="🎓",
    font=("Arial", 29),
    bg=NAVY,
    fg=CYAN
).pack(anchor="w")

tk.Label(
    logo_frame,
    text="COLLEGE",
    font=("Arial", 19, "bold"),
    bg=NAVY,
    fg=WHITE
).pack(anchor="w", pady=(5, 0))

tk.Label(
    logo_frame,
    text="MANAGEMENT SYSTEM",
    font=("Arial", 8, "bold"),
    bg=NAVY,
    fg="#9DB3DC"
).pack(anchor="w", pady=(2, 0))


# =====================================================
# SIDEBAR NAVIGATION
# =====================================================

tk.Label(
    sidebar,
    text="MAIN MENU",
    font=("Arial", 9, "bold"),
    bg=NAVY,
    fg="#8294B8"
).pack(anchor="w", padx=22, pady=(0, 9))


def make_nav_button(text, command, active=False):
    normal_bg = "#243657" if active else NAVY
    normal_fg = "#FFFFFF"

    button = tk.Button(
        sidebar,
        text=text,
        command=command,
        font=("Arial", 12, "bold"),
        anchor="w",
        padx=18,
        pady=14,
        bd=0,
        relief="flat",
        cursor="hand2",
        bg=normal_bg,
        fg=normal_fg,
        activebackground="#2D4773",
        activeforeground="#FFFFFF",
        highlightthickness=0,
        wraplength=185
    )

    button.pack(
        fill="x",
        padx=12,
        pady=4
    )

    if active:
        button.configure(
            bg="#243657",
            fg="#FFFFFF"
        )
    else:
        button.bind(
            "<Enter>",
            lambda event: button.configure(
                bg="#2D4773",
                fg="#FFFFFF"
            )
        )

        button.bind(
            "<Leave>",
            lambda event: button.configure(
                bg=NAVY,
                fg="#FFFFFF"
            )
        )

    return button

make_nav_button(
    "▦   Dashboard",
    lambda: (
        content_canvas.yview_moveto(0),
        set_status("Dashboard overview.")
    ),
    True
)

make_nav_button(
    "♙   Students",
    open_students
)

make_nav_button(
    "▣   Attendance",
    open_attendance
)

make_nav_button(
    "◆   Placements",
    open_placements
)

make_nav_button(
    "▤   Reports",
    lambda: messagebox.showinfo(
        "Reports",
        "The Reports module can be added in a future update."
    )
)


# Sidebar footer
sidebar_footer = tk.Frame(sidebar, bg=NAVY)
sidebar_footer.pack(side="bottom", fill="x", padx=18, pady=22)

tk.Frame(
    sidebar_footer,
    bg="#304064",
    height=1
).pack(fill="x", pady=(0, 13))

tk.Label(
    sidebar_footer,
    text="COLLEGE MANAGER",
    font=("Arial", 9, "bold"),
    bg=NAVY,
    fg=WHITE
).pack(anchor="w")

tk.Label(
    sidebar_footer,
    text="Student Placement System",
    font=("Arial", 8),
    bg=NAVY,
    fg="#9DB3DC"
).pack(anchor="w", pady=(4, 0))


# =====================================================
# HEADER
# =====================================================

header = tk.Frame(content, bg=BG)
header.pack(fill="x", padx=28, pady=(25, 20))

header_left = tk.Frame(header, bg=BG)
header_left.pack(side="left", fill="x", expand=True)

tk.Label(
    header_left,
    text="Dashboard Overview",
    font=("Arial", 24, "bold"),
    bg=BG,
    fg=TEXT
).pack(anchor="w")

tk.Label(
    header_left,
    text="Monitor your college activity from one place.",
    font=("Arial", 10),
    bg=BG,
    fg=MUTED
).pack(anchor="w", pady=(5, 0))

header_right = tk.Frame(header, bg=BG)
header_right.pack(side="right", anchor="n")

date_label = tk.Label(
    header_right,
    text=date.today().strftime("%d %b %Y"),
    font=("Arial", 10, "bold"),
    bg=BG,
    fg=TEXT
)
date_label.pack(anchor="e")

tk.Label(
    header_right,
    text="TODAY",
    font=("Arial", 8, "bold"),
    bg=BG,
    fg=MUTED
).pack(anchor="e", pady=(4, 0))


# =====================================================
# WELCOME BANNER
# =====================================================

banner = tk.Frame(
    content,
    bg="#1D4ED8",
    highlightthickness=0
)
banner.pack(fill="x", padx=28, pady=(0, 22))

banner_inner = tk.Frame(
    banner,
    bg="#1D4ED8"
)
banner_inner.pack(fill="x", padx=22, pady=19)

banner_left = tk.Frame(
    banner_inner,
    bg="#1D4ED8"
)
banner_left.pack(side="left", fill="x", expand=True)

tk.Label(
    banner_left,
    text="Welcome back! 👋",
    font=("Arial", 19, "bold"),
    bg="#1D4ED8",
    fg=WHITE
).pack(anchor="w")

tk.Label(
    banner_left,
    text="Everything you need to manage your college, in one place.",
    font=("Arial", 10),
    bg="#1D4ED8",
    fg="#E0EAFF",
    wraplength=550,
    justify="left"
).pack(anchor="w", pady=(6, 0))

banner_button = tk.Button(
    banner_inner,
    text="+  Add Student",
    command=open_students,
    font=("Arial", 10, "bold"),
    bg=WHITE,
    fg="#1D4ED8",
    activebackground="#E0EAFF",
    activeforeground="#1D4ED8",
    relief="flat",
    bd=0,
    cursor="hand2",
    padx=14,
    pady=10
)
banner_button.pack(side="right", padx=(12, 0))


# =====================================================
# STATISTICS CARDS
# =====================================================

section_heading = tk.Frame(content, bg=BG)
section_heading.pack(fill="x", padx=28, pady=(0, 12))

tk.Label(
    section_heading,
    text="Key Statistics",
    font=("Arial", 15, "bold"),
    bg=BG,
    fg=TEXT
).pack(side="left")

tk.Label(
    section_heading,
    text="LIVE DATABASE OVERVIEW",
    font=("Arial", 8, "bold"),
    bg=BG,
    fg=MUTED
).pack(side="right")


cards_frame = tk.Frame(content, bg=BG)
cards_frame.pack(fill="x", padx=28)

for column in range(3):
    cards_frame.grid_columnconfigure(
        column,
        weight=1,
        uniform="cards"
    )


def make_stat_card(parent, column, title, description, color):
    card = tk.Frame(
        parent,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    card.grid(
        row=0,
        column=column,
        sticky="nsew",
        padx=(0 if column == 0 else 7, 0 if column == 2 else 7)
    )

    top_line = tk.Frame(
        card,
        bg=color,
        height=4
    )
    top_line.pack(fill="x")

    body = tk.Frame(card, bg=WHITE)
    body.pack(fill="both", expand=True, padx=15, pady=14)

    tk.Label(
        body,
        text=title,
        font=("Arial", 10, "bold"),
        bg=WHITE,
        fg=MUTED
    ).pack(anchor="w")

    value_label = tk.Label(
        body,
        text="0",
        font=("Arial", 27, "bold"),
        bg=WHITE,
        fg=TEXT
    )
    value_label.pack(anchor="w", pady=(8, 3))

    tk.Label(
        body,
        text=description,
        font=("Arial", 9),
        bg=WHITE,
        fg=MUTED
    ).pack(anchor="w")

    def on_enter(event):
        card.configure(highlightbackground=color)
        top_line.configure(height=6)

    def on_leave(event):
        card.configure(highlightbackground=BORDER)
        top_line.configure(height=4)

    for widget in (card, top_line, body, *body.winfo_children()):
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    return value_label


student_value_label = make_stat_card(
    cards_frame,
    0,
    "Total Students",
    "Registered student records",
    BLUE
)

present_value_label = make_stat_card(
    cards_frame,
    1,
    "Present Today",
    "Students marked present",
    GREEN
)

absent_value_label = make_stat_card(
    cards_frame,
    2,
    "Absent Today",
    "Students marked absent",
    ORANGE
)

card_value_labels = [
    student_value_label,
    present_value_label,
    absent_value_label
]


# =====================================================
# ATTENDANCE OVERVIEW
# =====================================================

attendance_card = tk.Frame(
    content,
    bg=WHITE,
    highlightbackground=BORDER,
    highlightthickness=1
)
attendance_card.pack(fill="x", padx=28, pady=(22, 20))

attendance_header = tk.Frame(
    attendance_card,
    bg=WHITE
)
attendance_header.pack(fill="x", padx=19, pady=(17, 5))

tk.Label(
    attendance_header,
    text="Today's Attendance",
    font=("Arial", 14, "bold"),
    bg=WHITE,
    fg=TEXT
).pack(side="left")

attendance_percent_label = tk.Label(
    attendance_header,
    text="0%",
    font=("Arial", 20, "bold"),
    bg=WHITE,
    fg=BLUE
)
attendance_percent_label.pack(side="right")

tk.Label(
    attendance_card,
    text="Percentage of students marked present or absent today",
    font=("Arial", 9),
    bg=WHITE,
    fg=MUTED
).pack(anchor="w", padx=19, pady=(0, 12))

progress_background = tk.Frame(
    attendance_card,
    bg="#E8EDF6",
    height=13
)
progress_background.pack(fill="x", padx=19)
progress_background.pack_propagate(False)

progress_fill = tk.Frame(
    progress_background,
    bg=BLUE,
    height=13,
    width=0
)
progress_fill.place(x=0, y=0)

attendance_detail = tk.Label(
    attendance_card,
    text="Present: 0     Absent: 0     Total marked: 0",
    font=("Arial", 9),
    bg=WHITE,
    fg=MUTED
)
attendance_detail.pack(anchor="w", padx=19, pady=(11, 17))


# =====================================================
# LATEST STUDENTS TABLE
# =====================================================

students_card = tk.Frame(
    content,
    bg=WHITE,
    highlightbackground=BORDER,
    highlightthickness=1
)
students_card.pack(fill="x", padx=28, pady=(0, 20))

students_header = tk.Frame(
    students_card,
    bg=WHITE
)
students_header.pack(fill="x", padx=18, pady=(15, 10))

tk.Label(
    students_header,
    text="Latest Students",
    font=("Arial", 14, "bold"),
    bg=WHITE,
    fg=TEXT
).pack(side="left")

view_all_button = tk.Button(
    students_header,
    text="Manage Students  →",
    command=open_students,
    font=("Arial", 9, "bold"),
    bg=WHITE,
    fg=BLUE,
    activebackground=WHITE,
    activeforeground=BLUE,
    relief="flat",
    bd=0,
    cursor="hand2"
)
view_all_button.pack(side="right")

table_frame = tk.Frame(students_card, bg=WHITE)
table_frame.pack(fill="x", padx=15, pady=(0, 15))

student_table = ttk.Treeview(
    table_frame,
    columns=("name", "email", "course"),
    show="headings",
    height=5,
    style="Students.Treeview"
)

student_table.heading("name", text="STUDENT NAME")
student_table.heading("email", text="EMAIL")
student_table.heading("course", text="COURSE")

student_table.column("name", width=180, minwidth=110, anchor="w")
student_table.column("email", width=260, minwidth=120, anchor="w")
student_table.column("course", width=150, minwidth=90, anchor="w")

student_table.pack(fill="x")


# =====================================================
# QUICK ACTIONS
# =====================================================

quick_heading = tk.Label(
    content,
    text="Quick Actions",
    font=("Arial", 15, "bold"),
    bg=BG,
    fg=TEXT
)
quick_heading.pack(anchor="w", padx=28, pady=(0, 12))

actions_frame = tk.Frame(content, bg=BG)
actions_frame.pack(fill="x", padx=28, pady=(0, 22))


def make_action_button(parent, text, command, color):
    button = tk.Button(
        parent,
        text=text,
        command=command,
        font=("Arial", 10, "bold"),
        bg=color,
        fg=WHITE,
        activebackground=BLUE_HOVER,
        activeforeground=WHITE,
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=14,
        pady=11
    )
    button.pack(side="left", padx=(0, 10), pady=3)

    button.bind(
        "<Enter>",
        lambda event: button.configure(bg=BLUE_HOVER)
    )
    button.bind(
        "<Leave>",
        lambda event, normal=color: button.configure(bg=normal)
    )

    return button


make_action_button(
    actions_frame,
    "+  Manage Students",
    open_students,
    BLUE
)

make_action_button(
    actions_frame,
    "▣  Mark Attendance",
    open_attendance,
    GREEN
)

make_action_button(
    actions_frame,
    "🤖  Smart Attendance AI",
    open_smart_attendance,
    "#228C83"
)
make_action_button(
    actions_frame,
    "🎓 Ask Your College Data",
    open_ask_college_data,
    "#0F766E"
)
# =====================================================
# FOOTER / STATUS BAR
# =====================================================

footer = tk.Frame(
    content,
    bg=BG
)
footer.pack(fill="x", padx=28, pady=(0, 20))

tk.Label(
    footer,
    textvariable=status_var,
    font=("Arial", 9),
    bg=BG,
    fg=MUTED
).pack(side="left")

tk.Label(
    footer,
    text="College Management System",
    font=("Arial", 9),
    bg=BG,
    fg=MUTED
).pack(side="right")


# =====================================================
# NUMBER ANIMATION
# =====================================================

def animate_number(label, target, current=0, generation=0):
    if generation != refresh_generation:
        return

    target = max(0, int(target))

    if current < target:
        step = max(1, (target - current) // 12)
        current = min(current + step, target)

        label.configure(text=str(current))

        root.after(
            25,
            animate_number,
            label,
            target,
            current,
            generation
        )
    else:
        label.configure(text=str(target))

def show_refresh_animation():
    # Temporary welcome overlay
    overlay = tk.Frame(root, bg="#111C3A")
    overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

    tk.Label(
        overlay,
        text="🎓",
        font=("Arial", 48),
        bg="#111C3A",
        fg="#27C5E8"
    ).pack(pady=(150, 15))

    tk.Label(
        overlay,
        text="WELCOME BACK!",
        font=("Arial", 25, "bold"),
        bg="#111C3A",
        fg="white"
    ).pack(pady=8)

    tk.Label(
        overlay,
        text="Refreshing your college dashboard...",
        font=("Arial", 12),
        bg="#111C3A",
        fg="#B8C7E5"
    ).pack(pady=8)

    root.update_idletasks()

    def finish_animation():
        overlay.destroy()
        refresh_dashboard()

    root.after(1800, finish_animation)
# =====================================================
 # DASHBOARD REFRESH
# =====================================================

refresh_generation = 0


def animate_attendance(target, generation, current=0):
    if generation != refresh_generation:
        return

    target = max(0, min(100, int(target)))

    attendance_percent_label.configure(
        text=f"{current}%"
    )

    progress_background.update_idletasks()

    available_width = progress_background.winfo_width()
    fill_width = int(available_width * current / 100)

    progress_fill.place_configure(
        width=fill_width
    )

    if current < target:
        root.after(
            12,
            animate_attendance,
            target,
            generation,
            current + 1
        )


def refresh_dashboard(show_confirmation=False):
    global refresh_generation

    refresh_generation += 1
    generation = refresh_generation

    students_count = get_student_count()
    low_attendance_count = get_low_attendance_count()

    present_count, absent_count = get_attendance_stats()

    animate_number(
        student_value_label,
        students_count,
        generation=generation
    )

    animate_number(
        present_value_label,
        present_count,
        generation=generation
    )

    animate_number(
        absent_value_label,
        absent_count,
        generation=generation
    )

    total_marked = present_count + absent_count

    attendance_percentage = (
        round((present_count / total_marked) * 100)
        if total_marked > 0
        else 0
    )

    attendance_detail.configure(
        text=(
            f"Present: {present_count}     "
            f"Absent: {absent_count}     "
            f"Total marked: {total_marked}"
        )
    )

    animate_attendance(
        attendance_percentage,
        generation
    )

    for item in student_table.get_children():
        student_table.delete(item)

    for student in get_latest_students():
        student_table.insert("", "end", values=student)

    date_label.configure(
        text=date.today().strftime("%d %b %Y")
    )

    set_status("Dashboard refreshed successfully.")

    if show_confirmation:
        messagebox.showinfo(
            "Dashboard",
            "Dashboard refreshed successfully!"
        )


# =====================================================
# REFRESH BUTTON
# =====================================================

refresh_button = tk.Button(
    header_right,
    text="↻ Refresh",
    command=show_refresh_animation,
    font=("Arial", 9, "bold"),
    bg=BLUE,
    fg=WHITE,
    activebackground=BLUE_HOVER,
    activeforeground=WHITE,
    relief="flat",
    bd=0,
    cursor="hand2",
    padx=12,
    pady=7
)
refresh_button.pack(anchor="e", pady=(10, 0))


# =====================================================
# START DASHBOARD
# =====================================================

root.after(150, refresh_dashboard)
root.mainloop()
def open_smart_attendance():
    import tkinter as tk
    from tkinter import ttk, messagebox

    summary = get_smart_attendance_summary()

    if "error" in summary:
        messagebox.showerror("Database Error", summary["error"])
        return

    window = tk.Toplevel()
    window.title("Smart Attendance Intelligence")
    window.geometry("850x550")
    window.configure(bg="#F3F5F9")

    tk.Label(
        window,
        text="Smart Attendance Intelligence",
        font=("Arial", 20, "bold"),
        bg="#F3F5F9",
        fg="#1E293B"
    ).pack(pady=(18, 5))

    tk.Label(
        window,
        text="Attendance analysis and risk detection",
        font=("Arial", 11),
        bg="#F3F5F9",
        fg="#64748B"
    ).pack(pady=(0, 15))

    stats = tk.Frame(window, bg="#F3F5F9")
    stats.pack(fill="x", padx=20, pady=5)

    cards = [
        ("Safe", summary["safe"], "#15803D"),
        ("Low Attendance", summary["low"], "#DC2626"),
        ("No Records", summary["no_records"], "#64748B")
    ]

    for title, count, color in cards:
        card = tk.Frame(
            stats, bg="white",
            highlightbackground="#DCE3ED",
            highlightthickness=1
        )
        card.pack(side="left", fill="x", expand=True, padx=6)

        tk.Label(
            card, text=title, font=("Arial", 11, "bold"),
            bg="white", fg=color
        ).pack(pady=(12, 4))

        tk.Label(
            card, text=str(count), font=("Arial", 24, "bold"),
            bg="white", fg=color
        ).pack(pady=(0, 12))

    columns = ("id", "name", "percentage", "status")
    table = ttk.Treeview(
        window, columns=columns,
        show="headings", height=13
    )

    table.heading("id", text="ID")
    table.heading("name", text="STUDENT NAME")
    table.heading("percentage", text="ATTENDANCE %")
    table.heading("status", text="RISK STATUS")

    table.column("id", width=60, anchor="center")
    table.column("name", width=280, anchor="w")
    table.column("percentage", width=150, anchor="center")
    table.column("status", width=180, anchor="center")

    for student in summary["students"]:
        table.insert(
            "", "end",
            values=(
                student["id"],
                student["name"],
                f'{student["percentage"]:.1f}%',
                student["status"]
            )
        )

    table.pack(fill="both", expand=True, padx=20, pady=15)

    tk.Button(
        window,
        text="Refresh Analysis",
        font=("Arial", 11, "bold"),
        bg="#2563EB",
        fg="white",
        command=lambda: refresh_analysis()
    ).pack(pady=(0, 15))

    def refresh_analysis():
        window.destroy()
        open_smart_attendance()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    open_smart_attendance()
    root.mainloop()