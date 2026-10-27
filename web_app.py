import streamlit as st
import sqlite3
from pathlib import Path

# -----------------------------
# Database
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "college.db"


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