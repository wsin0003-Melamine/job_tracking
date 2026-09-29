import streamlit as st
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้าเพจ
st.set_page_config(page_title="Job Application Tracker", layout="wide")

# หัวข้อแอปพลิเคชัน
st.title("💼 Job Application Tracker")
st.markdown("ระบบบันทึกและติดตามสถานะการสมัครงานของคุณ")

# เริ่มต้น Session State สำหรับเก็บข้อมูล (เริ่มต้นด้วยตารางว่าง ไม่มี Mock Data)
if "job_data" not in st.session_state:
    st.session_state.job_data = pd.DataFrame(
        columns=["Company", "Position", "Date Applied", "Status", "Notes"]
    )

# ส่วน Sidebar สำหรับเพิ่มข้อมูลใหม่
st.sidebar.header("➕ เพิ่มรายการสมัครงาน")
with st.sidebar.form(key="add_job_form", clear_on_submit=True):
    company = st.text_input("ชื่อบริษัท *")
    position = st.text_input("ตำแหน่งงาน *")
    date_applied = st.date_input("วันที่สมัคร", datetime.today())
    status = st.selectbox(
        "สถานะ",
        ["Applied (สมัครแล้ว)", "Interviewing (กำลังสัมภาษณ์)", "Offered (ได้ข้อเสนอ)", "Rejected (ปฏิเสธ)"]
    )
    notes = st.text_area("หมายเหตุเพิ่มเติม")
    
    submit_button = st.form_submit_button(label="บันทึกข้อมูล")

# ประมวลผลเมื่อกดปุ่มบันทึก
if submit_button:
    if company.strip() == "" or position.strip() == "":
        st.sidebar.error("กรุณากรอกชื่อบริษัทและตำแหน่งงาน")
    else:
        new_row = pd.DataFrame([{
            "Company": company,
            "Position": position,
            "Date Applied": date_applied.strftime("%Y-%m-%d"),
            "Status": status,
            "Notes": notes
        }])
        st.session_state.job_data = pd.concat([st.session_state.job_data, new_row], ignore_index=True)
        st.sidebar.success("บันทึกข้อมูลสำเร็จ!")

# แสดงผลภาพรวม (Metrics Dashboard)
df = st.session_state.job_data

st.subheader("📊 ภาพรวมการสมัครงาน")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("สมัครทั้งหมด", len(df))
with col2:
    st.metric("⏳ กำลังสัมภาษณ์", len(df[df["Status"].str.contains("Interviewing")]))
with col3:
    st.metric("🎉 ได้รับข้อเสนอ", len(df[df["Status"].str.contains("Offered")]))
with col4:
    st.metric("❌ ปฏิเสธ", len(df[df["Status"].str.contains("Rejected")]))

st.markdown("---")

# ส่วนแสดงตารางข้อมูล
st.subheader("📋 รายการสมัครงานทั้งหมด")
if df.empty:
    st.info("ยังไม่มีข้อมูลการสมัครงาน กรุณาเพิ่มข้อมูลที่แถบด้านข้าง (Sidebar)")
else:
    # ตัวกรองสถานะ
    status_filter = st.multiselect(
        "กรองตามสถานะ:",
        options=["Applied (สมัครแล้ว)", "Interviewing (กำลังสัมภาษณ์)", "Offered (ได้ข้อเสนอ)", "Rejected (ปฏิเสธ)"],
        default=[]
    )
    
    filtered_df = df
    if status_filter:
        filtered_df = df[df["Status"].isin(status_filter)]
        
    st.dataframe(filtered_df, use_container_width=True)
    
    # ปุ่มสำหรับล้างข้อมูลทั้งหมด
    if st.button("🗑️ ล้างข้อมูลทั้งหมด"):
        st.session_state.job_data = pd.DataFrame(columns=["Company", "Position", "Date Applied", "Status", "Notes"])
        st.rerun()
