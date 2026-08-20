import sqlite3
from datetime import datetime

DATABASE = "eduvision.db"


def connect_db():
    return sqlite3.connect(DATABASE)


def create_tables():

    conn = connect_db()
    cursor = conn.cursor()

    # جدول الطلاب
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            student_id TEXT UNIQUE NOT NULL,
            level TEXT,
            department TEXT,
            face_folder TEXT NOT NULL
        )
    """)

    # جدول الحضور
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT NOT NULL,
            UNIQUE(student_id, date)
        )
    """)

    conn.commit()
    conn.close()


def add_student(name, student_id, level, department, face_folder):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO students
        (name, student_id, level, department, face_folder)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        student_id,
        level,
        department,
        face_folder
    ))

    conn.commit()
    conn.close()


def get_student(student_id):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, student_id, level, department, face_folder
        FROM students
        WHERE student_id = ?
    """, (student_id,))

    student = cursor.fetchone()

    conn.close()

    return student


def mark_attendance(student_id):

    now = datetime.now()

    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    conn = connect_db()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO attendance
            (student_id, date, time, status)
            VALUES (?, ?, ?, ?)
        """, (
            student_id,
            date,
            time,
            "Present"
        ))

        conn.commit()

        result = {
            "success": True,
            "student_id": student_id,
            "date": date,
            "time": time,
            "status": "Present"
        }

    except sqlite3.IntegrityError:

        result = {
            "success": False,
            "student_id": student_id,
            "date": date,
            "status": "Already Present"
        }

    conn.close()

    return result


if __name__ == "__main__":
    create_tables()
    print("EduVision database created successfully!")