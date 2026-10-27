import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "college.db"


def get_smart_attendance_summary():
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            students = conn.execute("""
                SELECT
                    s.id,
                    s.name,
                    COUNT(a.student_id) AS total,
                    SUM(
                        CASE
                            WHEN LOWER(a.status) = 'present'
                            THEN 1 ELSE 0
                        END
                    ) AS present
                FROM students s
                LEFT JOIN attendance a
                    ON s.id = a.student_id
                GROUP BY s.id, s.name
                ORDER BY s.name
            """).fetchall()

        summary = {
            "safe": 0,
            "low": 0,
            "no_records": 0,
            "students": []
        }

        for student_id, name, total, present in students:
            total = total or 0
            present = present or 0

            if total == 0:
                percentage = 0.0
                status = "No Records"
                summary["no_records"] += 1
            else:
                percentage = round((present / total) * 100, 1)

                if percentage < 75:
                    status = "Low Attendance"
                    summary["low"] += 1
                else:
                    status = "Safe"
                    summary["safe"] += 1

            summary["students"].append({
                "id": student_id,
                "name": name,
                "percentage": percentage,
                "status": status
            })

        return summary

    except sqlite3.Error as error:
        return {"error": str(error)}

if __name__ == "__main__":
    result = get_smart_attendance_summary()
    print(result)
def open_smart_attendance():
    import tkinter as tk
    from tkinter import ttk, messagebox

    summary = get_smart_attendance_summary()

    if "error" in summary:
        messagebox.showerror("Database Error", summary["error"])
        return

    window = tk.Toplevel()
    window.title("Smart Attendance AI")
    window.geometry("800x500")
    window.configure(bg="#F3F5F9")

    tk.Label(
        window,
        text="Smart Attendance Intelligence",
        font=("Arial", 20, "bold"),
        bg="#F3F5F9",
        fg="#1E293B"
    ).pack(pady=15)

    stats = tk.Frame(window, bg="#F3F5F9")
    stats.pack(fill="x", padx=15)

    for title, key, color in [
        ("Safe", "safe", "#15803D"),
        ("Low Attendance", "low", "#DC2626"),
        ("No Records", "no_records", "#64748B")
    ]:
        card = tk.Frame(stats, bg="white", padx=20, pady=12)
        card.pack(side="left", fill="x", expand=True, padx=5)

        tk.Label(
            card, text=title, bg="white", fg=color,
            font=("Arial", 11, "bold")
        ).pack()

        tk.Label(
            card, text=str(summary[key]), bg="white", fg=color,
            font=("Arial", 22, "bold")
        ).pack()

    columns = ("id", "name", "percentage", "status")
    table = ttk.Treeview(
        window, columns=columns, show="headings", height=12
    )

    for col, heading in [
        ("id", "ID"),
        ("name", "STUDENT NAME"),
        ("percentage", "ATTENDANCE %"),
        ("status", "RISK STATUS")
    ]:
        table.heading(col, text=heading)

    table.column("id", width=60, anchor="center")
    table.column("name", width=260)
    table.column("percentage", width=140, anchor="center")
    table.column("status", width=180, anchor="center")

    for student in summary["students"]:
        table.insert(
            "",
            "end",
            values=(
                student["id"],
                student["name"],
                f'{student["percentage"]:.1f}%',
                student["status"]
            )
        )

    table.pack(fill="both", expand=True, padx=15, pady=15)    