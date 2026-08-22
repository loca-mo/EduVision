import streamlit as st 
import pandas as pd 
import plotly.express as px 
 
# NOTE: st.set_page_config() is NOT called here — app.py already calls 
# it once for the whole multipage app. Calling it again on this page 
# would raise a StreamlitAPIException. 
 
 
# ============================================================ 
# SAMPLE DATA 
# Replace this later with data_manager.py 
# ============================================================ 
 
students = pd.DataFrame({ 
    "Student": [ 
        "Student A", 
        "Student B", 
        "Student C", 
        "Student D", 
        "Student E", 
        "Student F", 
        "Student G", 
        "Student H", 
        "Student I", 
        "Student J" 
    ], 
 
    "Attendance": [ 
        92, 76, 68, 95, 84, 
        61, 89, 97, 73, 91 
    ], 
 
    "Score": [ 
        88, 72, 61, 94, 79, 
        55, 86, 91, 68, 83 
    ], 
 
    "Previous_Score": [ 
        82, 75, 67, 90, 75, 
        64, 82, 88, 71, 80 
    ], 
 
    "Participation": [ 
        90, 70, 65, 96, 82, 
        58, 88, 94, 69, 86 
    ] 
}) 
 
 
# ============================================================ 
# CALCULATIONS 
# ============================================================ 
 
total_students = len(students) 
 
average_attendance = students["Attendance"].mean() 
 
average_score = students["Score"].mean() 
 
# Students below 75% attendance 
at_risk_attendance = students[ 
    students["Attendance"] < 75 
] 
 
# Students whose score decreased 
students_declining = students[ 
    students["Score"] < students["Previous_Score"] 
] 
 
# Students whose score improved 
students_improving = students[ 
    students["Score"] > students["Previous_Score"] 
] 
 
# Overall risk 
students["Risk"] = "Low" 
 
students.loc[ 
    (students["Attendance"] < 75) | 
    (students["Score"] < 60), 
    "Risk" 
] = "High" 
 
students.loc[ 
    ( 
        ( 
            students["Attendance"] >= 75 
        ) & 
        ( 
            students["Attendance"] < 85 
        ) 
    ) | 
    ( 
        ( 
            students["Score"] >= 60 
        ) & 
        ( 
            students["Score"] < 70 
        ) 
    ), 
    "Risk" 
] = "Medium" 
 
high_risk = students[ 
    students["Risk"] == "High" 
] 
 
medium_risk = students[ 
    students["Risk"] == "Medium" 
] 
 
 
# ============================================================ 
# HEADER 
# ============================================================ 
 
st.title("📊 EduVision Classroom Dashboard") 
 
st.caption( 
    "A real-time overview of classroom attendance, " 
    "performance, and student wellbeing." 
) 
 
 
# ============================================================ 
# LIVE CLASSROOM (from the shared VisionPipeline / camera) 
# ============================================================ 
 
pipeline = st.session_state.get("vision_pipeline") 
live_result = pipeline.last_result if pipeline else None 
 
st.subheader("🎥 Classroom Now (live)") 
 
if live_result is None: 
    st.info( 
        "No live camera data yet — open the **Live AI** page and start " 
        "the camera to see students detected here in real time." 
    ) 
else: 
    live_col1, live_col2, live_col3, live_col4 = st.columns(4) 
 
    with live_col1: 
        st.metric("Students Detected", live_result["people_count"]) 
 
    with live_col2: 
        st.metric("Present", len(live_result["present_ids"])) 
 
    with live_col3: 
        st.metric("Average Focus", f'{live_result["average_focus"]:.0f}%') 
 
    with live_col4: 
        st.metric( 
            "Distractions / Raised Hands", 
            f'{live_result["distraction_count"]} / {live_result["raised_hands"]}', 
        ) 
 
st.divider() 
 
 
# ============================================================ 
# CLASSROOM HEALTH 
# ============================================================ 
 
st.subheader("🏫 Classroom Health") 
 
st.write( 
    "Here's a quick overview of how your classroom is doing." 
) 
 
 
# ============================================================ 
# KPI CARDS 
# ============================================================ 
 
col1, col2, col3 = st.columns(3) 
 
with col1: 
 
    st.metric( 
        label="👨‍🎓 Total Students", 
        value=total_students 
    ) 
 
with col2: 
 
    st.metric( 
        label="📅 Average Attendance", 
        value=f"{average_attendance:.1f}%" 
    ) 
 
with col3: 
 
    st.metric( 
        label="📊 Average Score", 
        value=f"{average_score:.1f}%" 
    ) 
 
 
col4, col5, col6 = st.columns(3) 
 
with col4: 
 
    st.metric( 
        label="🚨 At Risk", 
        value=len(high_risk) 
    ) 
 
with col5: 
 
    st.metric( 
        label="📈 Improving", 
        value=len(students_improving) 
    ) 
 
with col6: 
 
    st.metric( 
        label="📝 Students Needing Attention", 
        value=len(medium_risk) 
    ) 
 
 
st.divider() 
 
 
# ============================================================ 
# HEALTH STATUS 
# ============================================================ 
 
st.subheader("❤️ Overall Classroom Health") 
 
health_score = ( 
    average_attendance * 0.4 
    + average_score * 0.6 
) 
 
 
if health_score >= 85: 
 
    health_status = "Excellent" 
    health_message = ( 
        "Your classroom is performing very well. " 
        "Attendance and academic performance are strong." 
    ) 
 
elif health_score >= 70: 
 
    health_status = "Good" 
    health_message = ( 
        "Your classroom is generally doing well, " 
        "but some students may need additional support." 
    ) 
 
elif health_score >= 55: 
 
    health_status = "Needs Attention" 
    health_message = ( 
        "Several indicators suggest that some " 
        "students may need intervention." 
    ) 
 
else: 
 
    health_status = "Critical" 
    health_message = ( 
        "Classroom performance requires immediate " 
        "attention and targeted support." 
    ) 
 
 
health_col1, health_col2 = st.columns([1, 3]) 
 
with health_col1: 
 
    st.metric( 
        "Classroom Health Score", 
        f"{health_score:.0f}/100" 
    ) 
 
with health_col2: 
 
    if health_status == "Excellent": 
 
        st.success( 
            f"🟢 **{health_status}** — {health_message}" 
        ) 
 
    elif health_status == "Good": 
 
        st.info( 
            f"🔵 **{health_status}** — {health_message}" 
        ) 
 
    elif health_status == "Needs Attention": 
 
        st.warning( 
            f"🟠 **{health_status}** — {health_message}" 
        ) 
 
    else: 
 
        st.error( 
            f"🔴 **{health_status}** — {health_message}" 
        ) 
 
 
st.divider() 
 
 
# ============================================================ 
# CHARTS 
# ============================================================ 
 
left, right = st.columns(2) 
 
 
# ------------------------------------------------------------ 
# ATTENDANCE CHART 
# ------------------------------------------------------------ 
 
with left: 
 
    st.subheader("📅 Student Attendance") 
 
    attendance_chart = px.bar( 
        students, 
        x="Student", 
        y="Attendance", 
        title="Attendance by Student", 
        range_y=[0, 100], 
        labels={ 
            "Attendance": "Attendance (%)", 
            "Student": "Student" 
        } 
    ) 
 
    attendance_chart.add_hline( 
        y=75, 
        line_dash="dash", 
        annotation_text="75% Alert Threshold" 
    ) 
 
    st.plotly_chart( 
        attendance_chart, 
        use_container_width=True 
    ) 
 
 
# ------------------------------------------------------------ 
# PERFORMANCE CHART 
# ------------------------------------------------------------ 
 
with right: 
 
    st.subheader("📊 Student Performance") 
 
    performance_chart = px.bar( 
        students, 
        x="Student", 
        y="Score", 
        title="Current Performance", 
        range_y=[0, 100], 
        labels={ 
            "Score": "Score (%)", 
            "Student": "Student" 
        } 
    ) 
 
    performance_chart.add_hline( 
        y=60, 
        line_dash="dash", 
        annotation_text="60% Support Threshold" 
    ) 
 
    st.plotly_chart( 
        performance_chart, 
        use_container_width=True 
    ) 
 
 
st.divider() 
 
 
# ============================================================ 
# STUDENT RISK TABLE 
# ============================================================ 
 
st.subheader("🚨 Students Requiring Attention") 
 
risk_students = students[ 
    students["Risk"] != "Low" 
].copy() 
 
 
if len(risk_students) == 0: 
 
    st.success( 
        "🎉 No students currently require additional attention." 
    ) 
 
else: 
 
    display_risk = risk_students[ 
        [ 
            "Student", 
            "Attendance", 
            "Score", 
            "Previous_Score", 
            "Participation", 
            "Risk" 
        ] 
    ].copy() 
 
    display_risk.columns = [ 
        "Student", 
        "Attendance", 
        "Current Score", 
        "Previous Score", 
        "Participation", 
        "Risk" 
    ] 
 
    st.dataframe( 
        display_risk, 
        use_container_width=True, 
        hide_index=True 
    ) 
 
 
st.divider() 
 
 
# ============================================================ 
# CLASSROOM INSIGHTS 
# ============================================================ 
 
st.subheader("💡 Classroom Insights") 
 
insight1, insight2, insight3 = st.columns(3) 
 
 
# ------------------------------------------------------------ 
# ATTENDANCE INSIGHT 
# ------------------------------------------------------------ 
 
with insight1: 
 
    st.markdown("### 📅 Attendance") 
 
    if average_attendance >= 90: 
 
        st.success( 
            f"Excellent attendance at " 
            f"**{average_attendance:.1f}%**." 
        ) 
 
    elif average_attendance >= 75: 
 
        st.info( 
            f"Average attendance is " 
            f"**{average_attendance:.1f}%**." 
        ) 
 
    else: 
 
        st.error( 
            f"Attendance needs attention: " 
            f"**{average_attendance:.1f}%**." 
        ) 
 
 
# ------------------------------------------------------------ 
# PERFORMANCE INSIGHT 
# ------------------------------------------------------------ 
 
with insight2: 
 
    st.markdown("### 📊 Performance") 
 
    if average_score >= 85: 
 
        st.success( 
            f"Strong classroom performance: " 
            f"**{average_score:.1f}%**." 
        ) 
 
    elif average_score >= 70: 
 
        st.info( 
            f"Average classroom performance is " 
            f"**{average_score:.1f}%**." 
        ) 
 
    else: 
 
        st.warning( 
            f"Performance may require additional " 
            f"support: **{average_score:.1f}%**." 
        ) 
 
 
# ------------------------------------------------------------ 
# PROGRESS INSIGHT 
# ------------------------------------------------------------ 
 
with insight3: 
 
    st.markdown("### 📈 Progress") 
 
    if len(students_improving) > len(students_declining): 
 
        st.success( 
            f"More students are improving " 
            f"({len(students_improving)}) than declining " 
            f"({len(students_declining)})." 
        ) 
 
    elif len(students_improving) == len(students_declining): 
 
        st.info( 
            "The number of improving and declining " 
            "students is currently balanced." 
        ) 
 
    else: 
 
        st.warning( 
            f"{len(students_declining)} students are " 
            f"currently showing declining performance." 
        ) 
 
 
st.divider() 
 
 
# ============================================================ 
# STUDENT DETAILS 
# ============================================================ 
 
st.subheader("👤 Student Overview") 
 
selected_student = st.selectbox( 
    "Select a student", 
    students["Student"].tolist() 
) 
 
 
student = students[ 
    students["Student"] == selected_student 
].iloc[0] 
 
 
student_col1, student_col2, student_col3, student_col4 = st.columns(4) 
 
 
with student_col1: 
 
    st.metric( 
        "Attendance", 
        f"{student['Attendance']}%" 
    ) 
 
 
with student_col2: 
 
    st.metric( 
        "Current Score", 
        f"{student['Score']}%" 
    ) 
 
 
with student_col3: 
 
    change = ( 
        student["Score"] 
        - student["Previous_Score"] 
    ) 
 
    st.metric( 
        "Score Change", 
        f"{change:+.0f}%" 
    ) 
 
 
with student_col4: 
 
    st.metric( 
        "Risk", 
        student["Risk"] 
    ) 
 
 
# ============================================================ 
# STUDENT RECOMMENDATION 
# ============================================================ 
 
if student["Risk"] == "High": 
 
    st.error( 
        f"🚨 **Recommended Action for {selected_student}**\n\n" 
        "This student may require immediate attention. " 
        "Review attendance and academic performance, " 
        "and consider a one-to-one intervention." 
    ) 
 
elif student["Risk"] == "Medium": 
 
    st.warning( 
        f"⚠️ **Recommended Action for {selected_student}**\n\n" 
        "Monitor this student's progress closely and " 
        "consider providing additional learning support." 
    ) 
 
else: 
 
    st.success( 
        f"✅ **{selected_student} is currently doing well.**\n\n" 
        "Continue monitoring progress and encourage " 
        "consistent participation." 
    ) 
 
 
# ============================================================ 
# FOOTER 
# ============================================================ 
 
st.divider() 
 
st.caption( 
    "🤖 EduVision AI • Classroom Analytics Dashboard" 
)  