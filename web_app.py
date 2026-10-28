import streamlit as st
import sqlite3
from pathlib import Path
from datetime import date

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="College Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "college.db"


# =========================
# DATABASE
# =========================
def get_connection():
    return sqlite3.connect(str(DB_PATH))


def setup_demo_database():
    """Create safe demo data if college.db is not available."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            course TEXT,
            cgpa REAL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            status TEXT,
            attendance_date TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS placement_companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            package REAL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS placement_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            company_id INTEGER,
            status TEXT
        )
    """)

    # Add demo students only if table is empty
    cur.execute("SELECT COUNT(*) FROM students")
    if cur.fetchone()[0] == 0:
        demo_students = [
            (1, "Aarav Sharma", "aarav@example.com", "BCA", 8.4),
            (2, "Riya Verma", "riya@example.com", "BCA", 8.9),
            (3, "Aditya Singh", "aditya@example.com", "BCA", 7.8),
            (4, "Priya Gupta", "priya@example.com", "BBA", 8.1),
            (5, "Rahul Meena", "rahul@example.com", "BCA", 7.2),
            (6, "Ananya Jain", "ananya@example.com", "BBA", 9.0),
            (7, "Kunal Sharma", "kunal@example.com", "BCA", 6.9),
            (8, "Sneha Agarwal", "sneha@example.com", "BCA", 8.7),
        ]

        cur.executemany("""
            INSERT INTO students
            (id, name, email, course, cgpa)
            VALUES (?, ?, ?, ?, ?)
        """, demo_students)

    cur.execute("SELECT COUNT(*) FROM placement_companies")
    if cur.fetchone()[0] == 0:
        companies = [
            ("Tech Solutions", 6.5),
            ("Global Systems", 8.0),
            ("Innovate Pvt Ltd", 7.2)
        ]

        cur.executemany("""
            INSERT INTO placement_companies
            (company_name, package)
            VALUES (?, ?)
        """, companies)

    # Demo attendance
    cur.execute("SELECT COUNT(*) FROM attendance")

    if cur.fetchone()[0] == 0:
        today = str(date.today())

        attendance_data = [
            (1, "Present", today),
            (2, "Present", today),
            (3, "Present", today),
            (4, "Absent", today),
            (5, "Present", today),
            (6, "Present", today),
            (7, "Absent", today),
            (8, "Present", today),
        ]

        cur.executemany("""
            INSERT INTO attendance
            (student_id, status, attendance_date)
            VALUES (?, ?, ?)
        """, attendance_data)

    conn.commit()
    conn.close()


setup_demo_database()


# =========================
# CSS
# =========================
st.markdown("""
<style>

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background-color: #202E55;
}

[data-testid="stSidebar"] * {
    color: white;
}

.dashboard-title {
    font-size: 32px;
    font-weight: 800;
    color: #17233F;
    margin-bottom: 5px;
}

.dashboard-subtitle {
    color: #7A879E;
    font-size: 15px;
}

.welcome-box {
    background: linear-gradient(135deg, #202E55, #3978F6);
    padding: 28px;
    border-radius: 16px;
    color: white;
    margin-top: 20px;
    margin-bottom: 25px;
}

.welcome-title {
    font-size: 25px;
    font-weight: 700;
}

.welcome-text {
    font-size: 15px;
    opacity: 0.9;
}

.stat-card {
    background: white;
    padding: 22px;
    border-radius: 15px;
    border: 1px solid #E5EAF3;
    box-shadow: 0 4px 15px rgba(0,0,0,0.04);
}

.stat-title {
    color: #7A879E;
    font-size: 14px;
}

.stat-value {
    color: #17233F;
    font-size: 30px;
    font-weight: 800;
}

.section-title {
    font-size: 22px;
    font-weight: 700;
    color: #17233F;
    margin-top: 25px;
}

.attendance-box {
    background: white;
    border: 1px solid #E5EAF3;
    padding: 25px;
    border-radius: 15px;
}

.big-percent {
    font-size: 40px;
    font-weight: 800;
    color: #3978F6;
}

.small-muted {
    color: #7A879E;
}

</style>
""", unsafe_allow_html=True)


# =========================
# DATABASE HELPERS
# =========================
def query_one(sql, params=()):
    conn = get_connection()
    result = conn.execute(sql, params).fetchone()
    conn.close()
    return result


def query_all(sql, params=()):
    conn = get_connection()
    result = conn.execute(sql, params).fetchall()
    conn.close()
    return result


# =========================
# SIDEBAR
# =========================
with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center;padding:15px 5px 25px;">
            <div style="font-size:42px;">🎓</div>
            <div style="font-size:18px;font-weight:800;">
                COLLEGE
            </div>
            <div style="font-size:18px;font-weight:800;">
                MANAGEMENT SYSTEM
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### MAIN MENU")

    page = st.radio(
        "",
        [
            "Dashboard",
            "Students",
            "Attendance",
            "Placements",
            "Reports",
            "Smart Attendance AI",
            "Ask Your College Data"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.caption("Student Placement System")
    st.caption("Web Version")


# =========================
# DASHBOARD
# =========================
if page == "Dashboard":

    st.markdown(
        '<div class="dashboard-title">Dashboard Overview</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        'Monitor your college activity from one place.'
        '</div>',
        unsafe_allow_html=True
    )

    st.write("📅 " + date.today().strftime("%d %B %Y"))

    # Welcome
    st.markdown(
        """
        <div class="welcome-box">
            <div class="welcome-title">
                Welcome back! 👋
            </div>
            <div class="welcome-text">
                Everything you need to manage your college, in one place.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Stats
    total_students = query_one(
        "SELECT COUNT(*) FROM students"
    )[0]

    total_companies = query_one(
        "SELECT COUNT(*) FROM placement_companies"
    )[0]

    total_applications = query_one(
        "SELECT COUNT(*) FROM placement_applications"
    )[0]

    today = str(date.today())

    present_today = query_one(
        """
        SELECT COUNT(*)
        FROM attendance
        WHERE attendance_date = ?
        AND LOWER(status) = 'present'
        """,
        (today,)
    )[0]

    absent_today = query_one(
        """
        SELECT COUNT(*)
        FROM attendance
        WHERE attendance_date = ?
        AND LOWER(status) = 'absent'
        """,
        (today,)
    )[0]

    st.markdown(
        '<div class="section-title">Key Statistics</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-title">👨‍🎓 Total Students</div>
                <div class="stat-value">{total_students}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-title">🟢 Present Today</div>
                <div class="stat-value">{present_today}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-title">🔴 Absent Today</div>
                <div class="stat-value">{absent_today}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-title">🏢 Companies</div>
                <div class="stat-value">{total_companies}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Attendance
    st.markdown(
        '<div class="section-title">Today\'s Attendance</div>',
        unsafe_allow_html=True
    )

    total_marked = present_today + absent_today

    if total_marked > 0:
        attendance_percentage = round(
            present_today / total_marked * 100
        )
    else:
        attendance_percentage = 0

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown(
            f"""
            <div class="attendance-box">
                <div class="small-muted">Attendance Percentage</div>
                <div class="big-percent">
                    {attendance_percentage}%
                </div>
                <div class="small-muted">
                    Present: {present_today}
                    &nbsp;&nbsp;|&nbsp;&nbsp;
                    Absent: {absent_today}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.progress(
            attendance_percentage / 100,
            text=f"{attendance_percentage}% Attendance"
        )

        st.write(
            f"Present: **{present_today}** | "
            f"Absent: **{absent_today}** | "
            f"Total Marked: **{total_marked}**"
        )

    # Latest Students
    st.markdown(
        '<div class="section-title">Latest Students</div>',
        unsafe_allow_html=True
    )

    students = query_all("""
        SELECT id, name, email, course, cgpa
        FROM students
        ORDER BY id DESC
        LIMIT 5
    """)

    if students:
        st.dataframe(
            students,
            column_config={
                "id": "ID",
                "name": "Student Name",
                "email": "Email",
                "course": "Course",
                "cgpa": st.column_config.NumberColumn(
                    "CGPA",
                    format="%.2f"
                )
            },
            hide_index=True,
            use_container_width=True
        )

    # Quick Actions
    st.markdown(
        '<div class="section-title">Quick Actions</div>',
        unsafe_allow_html=True
    )

    q1, q2, q3, q4 = st.columns(4)

    with q1:
        if st.button(
            "👨‍🎓 Manage Students",
            use_container_width=True
        ):
            st.session_state["page"] = "Students"
            st.rerun()

    with q2:
        if st.button(
            "▣ Mark Attendance",
            use_container_width=True
        ):
            st.session_state["page"] = "Attendance"
            st.rerun()

    with q3:
        if st.button(
            "🤖 Smart Attendance AI",
            use_container_width=True
        ):
            st.session_state["page"] = "Smart Attendance AI"
            st.rerun()

    with q4:
        if st.button(
            "🎓 Ask College Data",
            use_container_width=True
        ):
            st.session_state["page"] = "Ask Your College Data"
            st.rerun()


# =========================
# STUDENTS
# =========================
elif page == "Students":

    st.title("👨‍🎓 Students")

    students = query_all("""
        SELECT id, name, email, course, cgpa
        FROM students
        ORDER BY id
    """)

    st.dataframe(
        students,
        column_config={
            "id": "ID",
            "name": "Student Name",
            "email": "Email",
            "course": "Course",
            "cgpa": st.column_config.NumberColumn(
                "CGPA",
                format="%.2f"
            )
        },
        hide_index=True,
        use_container_width=True
    )


# =========================
# ATTENDANCE
# =========================
elif page == "Attendance":

    st.title("▣ Attendance")

    today = str(date.today())

    attendance = query_all("""
        SELECT
            s.id,
            s.name,
            s.course,
            COALESCE(a.status, 'Not Marked') AS status
        FROM students s
        LEFT JOIN attendance a
        ON s.id = a.student_id
        AND a.attendance_date = ?
        ORDER BY s.id
    """, (today,))

    st.dataframe(
        attendance,
        column_config={
            "id": "ID",
            "name": "Student Name",
            "course": "Course",
            "status": "Today's Status"
        },
        hide_index=True,
        use_container_width=True
    )

    st.info(
        "Attendance management is connected to the database."
    )


# =========================
# PLACEMENTS
# =========================
elif page == "Placements":

    st.title("🎓 Placements")

    companies = query_all("""
        SELECT *
        FROM placement_companies
        ORDER BY id
    """)

    if companies:
        st.subheader("Placement Companies")

        st.dataframe(
            companies,
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No placement companies found.")

    st.subheader("Placement Applications")

    applications = query_all("""
        SELECT *
        FROM placement_applications
        ORDER BY id
    """)

    if applications:
        st.dataframe(
            applications,
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No placement applications found.")


# =========================
# REPORTS
# =========================
elif page == "Reports":

    st.title("📊 Reports")

    total_students = query_one(
        "SELECT COUNT(*) FROM students"
    )[0]

    total_companies = query_one(
        "SELECT COUNT(*) FROM placement_companies"
    )[0]

    st.metric("Total Students", total_students)
    st.metric("Placement Companies", total_companies)

    st.info(
        "Reports section is ready for further analytics."
    )


# =========================
# SMART ATTENDANCE AI
# =========================
elif page == "Smart Attendance AI":

    st.title("🤖 Smart Attendance Intelligence")

    students = query_all("""
        SELECT id, name, course
        FROM students
        ORDER BY id
    """)

    for student_id, name, course in students:

        total = query_one("""
            SELECT COUNT(*)
            FROM attendance
            WHERE student_id = ?
        """, (student_id,))[0]

        present = query_one("""
            SELECT COUNT(*)
            FROM attendance
            WHERE student_id = ?
            AND LOWER(status) = 'present'
        """, (student_id,))[0]

        if total == 0:
            percentage = 0
            risk = "No Records"
        else:
            percentage = round(
                present / total * 100
            )

            if percentage < 75:
                risk = "Low Attendance"
            else:
                risk = "Safe"

        if risk == "Safe":
            icon = "🟢"
        elif risk == "Low Attendance":
            icon = "🔴"
        else:
            icon = "⚪"

        st.write(
            f"{icon} **{name}** — "
            f"{percentage}% — {risk}"
        )


# =========================
# ASK YOUR COLLEGE DATA
# =========================
elif page == "Ask Your College Data":

    st.title("🎓 Ask Your College Data")

    st.write(
        "Ask questions about students, courses, attendance "
        "and placements."
    )

    question = st.text_input(
        "Enter your question"
    )

    if st.button(
        "🔍 Ask",
        use_container_width=False
    ):

        q = question.lower().strip()

        if "total" in q and "student" in q:
            result = query_one(
                "SELECT COUNT(*) FROM students"
            )[0]

            st.success(
                f"Total registered students: {result}"
            )

        elif "course" in q and (
            "most" in q or
            "highest" in q
        ):
            result = query_one("""
                SELECT course, COUNT(*) AS total
                FROM students
                GROUP BY course
                ORDER BY total DESC
                LIMIT 1
            """)

            if result:
                st.success(
                    f"Course with most students: "
                    f"{result[0]} ({result[1]} students)"
                )

        elif "bca" in q:
            result = query_one("""
                SELECT COUNT(*)
                FROM students
                WHERE UPPER(course) = 'BCA'
            """)[0]

            st.success(
                f"BCA students: {result}"
            )

        elif "bba" in q:
            result = query_one("""
                SELECT COUNT(*)
                FROM students
                WHERE UPPER(course) = 'BBA'
            """)[0]

            st.success(
                f"BBA students: {result}"
            )

        elif "cgpa" in q and (
            "above" in q or
            "greater" in q
        ):

            result = query_all("""
                SELECT name, cgpa
                FROM students
                WHERE cgpa >= 8.0
                ORDER BY cgpa DESC
            """)

            if result:
                st.write(
                    "Students with CGPA 8.0 or above:"
                )
                st.dataframe(
                    result,
                    column_config={
                        "name": "Student Name",
                        "cgpa": st.column_config.NumberColumn(
                            "CGPA",
                            format="%.2f"
                        )
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info(
                    "No students found."
                )

        elif "attendance" in q and (
            "low" in q or
            "below" in q
        ):

            st.subheader(
                "Students with Low Attendance"
            )

            students = query_all("""
                SELECT id, name
                FROM students
                ORDER BY id
            """)

            low_students = []

            for student_id, name in students:

                total = query_one("""
                    SELECT COUNT(*)
                    FROM attendance
                    WHERE student_id = ?
                """, (student_id,))[0]

                present = query_one("""
                    SELECT COUNT(*)
                    FROM attendance
                    WHERE student_id = ?
                    AND LOWER(status) = 'present'
                """, (student_id,))[0]

                if total > 0:
                    percentage = present / total * 100

                    if percentage < 75:
                        low_students.append(
                            (name, round(percentage, 2))
                        )

            if low_students:
                st.dataframe(
                    low_students,
                    column_config={
                        "name": "Student",
                        "attendance": "Attendance %"
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.success(
                    "No students have low attendance."
                )

        else:
            st.info(
                "Try questions like: "
                "How many students are there? "
                "How many BCA students? "
                "Which course has most students? "
                "Show students with CGPA above 8.0."
            )


# =========================
# FOOTER
# =========================
st.markdown("---")

st.caption(
    "College Management System • "
    "Student Placement System • Web Dashboard"
)