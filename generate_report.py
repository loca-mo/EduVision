import os
import pandas as pd
from datetime import datetime

FACES_DIR = "faces"
ATTENDANCE_FILE = "attendance.csv"
REPORT_FILE = "final_report.csv"

def generate_absence_report():
    # 1. جلب قائمة كل الطلاب المسجلين من مجلد الأسماء
    if not os.path.exists(FACES_DIR):
        print("خطأ: مجلد الأسماء غير موجود.")
        return

    all_students = [d for d in os.listdir(FACES_DIR) if os.path.isdir(os.path.join(FACES_DIR, d))]
    
    # 2. قراءة قضايا الحضور
    present_students = []
    if os.path.exists(ATTENDANCE_FILE):
        df_att = pd.read_csv(ATTENDANCE_FILE)
        present_students = df_att['Name'].unique().tolist()

    # 3. تحديد الغائبين والحاضرين
    today_date = datetime.now().strftime("%Y-%m-%d")
    report_data = []

    for student in all_students:
        status = "Present" if student in present_students else "Absent"
        report_data.append({
            "Student Name": student,
            "Date": today_date,
            "Status": status
        })

    # 4. حفظ التقرير النهائي
    df_report = pd.DataFrame(report_data)
    df_report.to_csv(REPORT_FILE, index=False)
    
    print("\n=== تم إنشاء تقرير الحضور والغياب بنجاح ===")
    print(df_report)

if __name__ == "__main__":
    generate_absence_report()