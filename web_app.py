import streamlit as st
import sqlite3
from pathlib import Path

# -----------------------------
# Database
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "college.db"
def create_demo_database():
    if DB_PATH.exists():
        return

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE students (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            course TEXT,
            cgpa REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE placement_companies (
            id INTEGER PRIMARY KEY,
            company_name TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE placement_applications (
            id INTEGER PRIMARY KEY,
            student_id INTEGER,
            company_id INTEGER
        )
    """)

    students = [
        (1, "Aarav Sharma", "aarav@example.com", "BCA", 8.7),
        (2, "Riya Verma", "riya@example.com", "BCA", 9.1),
        (3, "Aditya Kumar", "aditya@example.com", "BTech", 8.5),
        (4, "Neha Singh", "neha@example.com", "BCA", 8.9),
        (5, "Rahul Meena", "rahul@example.com", "BTech", 7.8),
    ]

    cursor.executemany(
        "INSERT INTO students VALUES (?, ?, ?, ?, ?)",
        students
    )

    companies = [
        (1, "TCS"),
        (2, "Infosys")
    ]

    cursor.executemany(
        "INSERT INTO placement_companies VALUES (?, ?)",
        companies
    )

    applications = [
        (1, 1, 1),
        (2, 2, 1),
        (3, 3, 2)
    ]

    cursor.executemany(
        "INSERT INTO placement_applications VALUES (?, ?, ?)",
        applications
    )

    conn.commit()
    conn.close()


create_demo_database()

def get_connection():
    return sqlite3.connect(str(DB_PATH))


# -----------------------------
# Page Settings
# -----------------------------
st.set_page_config(
    page_title="Student Placement System",
    page_icon="🎓",
    layout="wide"
)

# -----------------------------
# Header
# -----------------------------
st.title("🎓 Student Placement System")
st.write("College Student & Placement Management Dashboard")

st.divider()

# -----------------------------
# Database Statistics
# -----------------------------
try:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM placement_companies")
    total_companies = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM placement_applications")
    total_applications = cursor.fetchone()[0]

    conn.close()

except Exception as error:
    st.error(f"Database error: {error}")
    total_students = 0
    total_companies = 0
    total_applications = 0


# -----------------------------
# Dashboard Cards
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("👨‍🎓 Total Students", total_students)

with col2:
    st.metric("🏢 Placement Companies", total_companies)

with col3:
    st.metric("📄 Applications", total_applications)


st.divider()

# -----------------------------
# Student Data
# -----------------------------
st.subheader("👨‍🎓 Student Data")

try:
    conn = get_connection()

    students = conn.execute(
        "SELECT * FROM students"
    ).fetchall()

    columns = [
        description[0]
        for description in conn.execute(
            "SELECT * FROM students LIMIT 1"
        ).description
    ]

    conn.close()

    if students:
        st.dataframe(
            students,
            column_config={
                columns[i]: st.column_config.Column(columns[i])
                for i in range(len(columns))
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No student data found.")

except Exception as error:
    st.error(f"Could not load student data: {error}")


st.divider()

# -----------------------------
# Placement Companies
# -----------------------------
st.subheader("🏢 Placement Companies")

try:
    conn = get_connection()

    companies = conn.execute(
        "SELECT * FROM placement_companies"
    ).fetchall()

    company_columns = [
        description[0]
        for description in conn.execute(
            "SELECT * FROM placement_companies LIMIT 1"
        ).description
    ]

    conn.close()

    if companies:
        st.dataframe(
            companies,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No placement companies found.")

except Exception as error:
    st.error(f"Could not load company data: {error}")


st.divider()

# -----------------------------
# Footer
# -----------------------------
st.caption("Student Placement System • Web Version")