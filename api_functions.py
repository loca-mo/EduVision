import sqlite3

DATABASE = "eduvision.db"


# ==========================================
# Get one student
# ==========================================

def get_student(student_id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            name,
            student_id,
            level,
            department
        FROM students
        WHERE student_id = ?
    """, (student_id,))

    student = cursor.fetchone()

    conn.close()

    if not student:
        return None

    return {
        "name": student[0],
        "student_id": student[1],
        "level": student[2],
        "department": student[3]
    }


# ==========================================
# Check Attendance
# ==========================================

def get_attendance(student_id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            date,
            time,
            status
        FROM attendance
        WHERE student_id = ?
        ORDER BY date DESC, time DESC
        LIMIT 1
    """, (student_id,))

    attendance = cursor.fetchone()

    conn.close()

    if not attendance:

        return {
            "present": False,
            "date": None,
            "time": None,
            "status": "Absent"
        }

    return {
        "present": attendance[2] == "Present",
        "date": attendance[0],
        "time": attendance[1],
        "status": attendance[2]
    }


# ==========================================
# Get Student + Attendance
# ==========================================

def get_student_attendance(student_id):

    student = get_student(student_id)

    if not student:
        return {
            "success": False,
            "message": "Student not found"
        }

    attendance = get_attendance(student_id)

    return {
        "success": True,
        "student": student,
        "attendance": attendance
    }


# ==========================================
# Get all students
# ==========================================

def get_all_students():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            name,
            student_id,
            level,
            department
        FROM students
        ORDER BY name
    """)

    rows = cursor.fetchall()

    conn.close()

    students = []

    for row in rows:

        students.append({
            "name": row[0],
            "student_id": row[1],
            "level": row[2],
            "department": row[3]
        })

    return students


# ==========================================
# Test
# ==========================================

if __name__ == "__main__":

    print("\n========== EduVision API Test ==========\n")

    student = get_student_attendance("23456")

    print(student)

    print("\n---------- All Students ----------")

    students = get_all_students()

    for s in students:
        print(s)