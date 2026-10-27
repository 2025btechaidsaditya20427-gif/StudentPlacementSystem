
import tkinter as tk
from tkinter import ttk
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "college.db"


def get_connection():
    return sqlite3.connect(str(DB_PATH), timeout=5)








def answer_question():
    question = question_entry.get().strip().lower()

    if not question:
        answer_label.config(text="Please type a question first.")
        return

    try:
        with get_connection() as conn:

            # 1. Total registered students
            if (
    "in " not in question
    and any(word in question for word in (
        "total students",
        "how many students",
        "registered students",
        "kitne students"
    ))
            ):
                total = conn.execute(
                    "SELECT COUNT(*) FROM students"
                ).fetchone()[0]

                answer_label.config(
                    text=f"Total registered students: {total}"
                )

            # 2. Course-wise statistics
            elif "course" in question and any(word in question for word in (
                "all", "list", "show", "which", "courses"
            )) and not any(word in question for word in (
                "how many", "count", "most", "highest"
            )):
                rows = conn.execute("""
                    SELECT course, COUNT(*)
                    FROM students
                    GROUP BY course
                    ORDER BY course
                """).fetchall()

                if rows:
                    result = "\n".join(
                        f"{course}: {count} student(s)"
                        for course, count in rows
                    )
                    answer_label.config(
                        text="Course-wise student statistics:\n" + result
                    )
                else:
                    answer_label.config(text="No courses found.")

            # 3. Count students in a particular course
            elif "how many" in question and " in " in question:
                course_name = question.split(" in ", 1)[1].strip(" ?.")

                rows = conn.execute("""
                    SELECT course, COUNT(*)
                    FROM students
                    WHERE LOWER(course) = LOWER(?)
                    GROUP BY course
                """, (course_name,)).fetchall()

                if rows:
                    course, count = rows[0]
                    answer_label.config(
                        text=f"{course}: {count} student(s)"
                    )
                else:
                    answer_label.config(
                        text=f"No students found for course: {course_name}"
                    )

            # 4. Course with the most students
            elif "course" in question and any(word in question for word in (
                "most", "highest", "maximum", "largest"
            )):
                rows = conn.execute("""
                    SELECT course, COUNT(*) AS total
                    FROM students
                    GROUP BY course
                    ORDER BY total DESC, course ASC
                """).fetchall()

                if rows:
                    highest = rows[0][1]
                    winners = [
                        f"{course} ({count} students)"
                        for course, count in rows
                        if count == highest
                    ]
                    answer_label.config(
                        text="Course(s) with the most students:\n"
                        + "\n".join(winners)
                    )
                else:
                    answer_label.config(text="No course data found.")

            # 5. Students above a specified CGPA
            elif "cgpa" in question:
                import re

                match = re.search(
                    r"(?:above|over|greater than|>)\s*(\d+(?:\.\d+)?)",
                    question
                )

                if match:
                    threshold = float(match.group(1))

                    rows = conn.execute("""
                        SELECT name, course, cgpa
                        FROM students
                        WHERE cgpa > ?
                        ORDER BY cgpa DESC, name
                    """, (threshold,)).fetchall()

                    if rows:
                        result = "\n".join(
                            f"{name} ({course}): CGPA {cgpa}"
                            for name, course, cgpa in rows
                        )
                        answer_label.config(
                            text=f"Students with CGPA above {threshold}:\n{result}"
                        )
                    else:
                        answer_label.config(
                            text=f"No students found with CGPA above {threshold}."
                        )
                else:
                    answer_label.config(
                        text="Try: Show students with CGPA above 8"
                    )

            # 6. Students with low attendance (below 75%)
            elif any(word in question for word in (
                "low attendance", "lowest attendance",
                "attendance risk", "kam attendance"
            )):
                rows = conn.execute("""
                    SELECT s.name,
                           COUNT(a.status) AS total,
                           SUM(CASE
                               WHEN LOWER(a.status) = 'present'
                               THEN 1 ELSE 0
                           END) AS present
                    FROM students s
                    LEFT JOIN attendance a ON s.id = a.student_id
                    GROUP BY s.id, s.name
                    ORDER BY s.name
                """).fetchall()

                low_students = []

                for name, total, present in rows:
                    if total > 0:
                        percentage = (present or 0) * 100 / total
                        if percentage < 75:
                            low_students.append(
                                f"{name}: {percentage:.1f}%"
                            )

                answer_label.config(
                    text=(
                        "Low attendance students (<75%):\n"
                        + "\n".join(low_students)
                        if low_students
                        else "No students with recorded attendance below 75%."
                    )
                )

            # 7. Students absent today
            elif "absent" in question:
                from datetime import date
                today = date.today().isoformat()

                rows = conn.execute("""
                    SELECT s.name
                    FROM attendance a
                    JOIN students s ON s.id = a.student_id
                    WHERE a.attendance_date = ?
                      AND LOWER(a.status) = 'absent'
                    ORDER BY s.name
                """, (today,)).fetchall()

                if rows:
                    names = "\n".join(row[0] for row in rows)
                    answer_label.config(
                        text=f"Students absent today ({len(rows)}):\n{names}"
                    )
                else:
                    answer_label.config(
                        text="No students are marked absent today."
                    )

            else:
                answer_label.config(
                    text=(
                        "Try these questions:\n"
                        "• How many students are registered?\n"
                        "• Show all courses\n"
                        "• How many students in BCA?\n"
                        "• Which course has the most students?\n"
                        "• Show students with CGPA above 8\n"
                        "• Show students with low attendance\n"
                        "• How many students are absent today?"
                    )
                )

    except sqlite3.Error as error:
        answer_label.config(text=f"Database error: {error}")  



def open_ask_college_data():
    global root, question_entry, answer_label

    root = tk.Toplevel()
    root.title("Ask Your College Data")
    root.geometry("650x400")
    root.configure(bg="#F4F7FC")

    tk.Label(
        root,
        text="🎓 Ask Your College Data",
        font=("Arial", 21, "bold"),
        bg="#F4F7FC",
        fg="#111C3A"
    ).pack(pady=(30, 10))

    tk.Label(
        root,
        text="Ask a question about your college database.",
        font=("Arial", 11),
        bg="#F4F7FC",
        fg="#64748B"
    ).pack(pady=(0, 20))

    question_entry = ttk.Entry(
        root,
        font=("Arial", 12),
        width=48
    )
    question_entry.pack(pady=8)
    question_entry.bind(
        "<Return>",
        lambda event: answer_question()
    )

    tk.Button(
        root,
        text="Ask Question",
        command=answer_question,
        bg="#3978F6",
        fg="white",
        font=("Arial", 11, "bold"),
        padx=18,
        pady=8
    ).pack(pady=10)

    answer_label = tk.Label(
        root,
        text="Try: How many students are registered?",
        font=("Arial", 11),
        bg="#F4F7FC",
        fg="#17233F",
        wraplength=550,
        justify="center"
    )
    answer_label.pack(pady=20)

    question_entry.focus_set()
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    open_ask_college_data()
    root.mainloop()