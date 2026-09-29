import streamlit as st
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Job Application Tracker", page_icon="💼", layout="wide")

st.title("💼 Job Application Tracker")
st.subheader("ติดตามและจัดการสถานะการสมัครงานของคุณ")

# Mock database using session state
if 'jobs' not in st.session_state:
    st.session_state.jobs = [
        {"Company": "Google", "Position": "AI Engineer", "Date": "2026-09-20", "Status": "Interviewing", "Notes": "รอบเทคนิคอลวันที่ 5 ต.ค."},
        {"Company": "Agoda", "Position": "Software Engineer", "Date": "2026-09-25", "Status": "Applied", "Notes": "ส่งเรซูเม่แล้ว รอติดต่อกลับ"},
    ]

# Sidebar for adding new jobs
st.sidebar.header("➕ เพิ่มรายการสมัครงาน")
with st.sidebar.form(key='job_form', clear_on_submit=True):
    company = st.text_input("ชื่อบริษัท")
    position = st.text_input("ตำแหน่งงาน")
    date_applied = st.date_input("วันที่สมัคร", datetime.now())
    status = st.selectbox("สถานะ", ["Applied", "Interviewing", "Offered", "Rejected"])
    notes = st.text_area("บันทึกเพิ่มเติม")
    
    submit_button = st.form_submit_button(label='บันทึก')
    
    if submit_button and company and position:
        st.session_state.jobs.append({
            "Company": company,
            "Position": position,
            "Date": str(date_applied),
            "Status": status,
            "Notes": notes
        })
        st.sidebar.success(f"บันทึกข้อมูลของ {company} เรียบร้อย!")

# Main Dashboard
df = pd.DataFrame(st.session_state.jobs)

if not df.empty:
    # Status metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("สมัครแล้วทั้งหมด", len(df))
    col2.metric("กำลังสัมภาษณ์ 🗓️", len(df[df['Status'] == 'Interviewing']))
    col3.metric("ได้รับข้อเสนอ 🎉", len(df[df['Status'] == 'Offered']))
    col4.metric("ปฏิเสธ ❌", len(df[df['Status'] == 'Rejected']))
    
    st.divider()
    
    # Filter by status
    status_filter = st.multiselect("กรองตามสถานะ", options=["Applied", "Interviewing", "Offered", "Rejected"], default=["Applied", "Interviewing", "Offered", "Rejected"])
    filtered_df = df[df['Status'].isin(status_filter)]
    
    # Display table
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.info("ยังไม่มีข้อมูลการสมัครงาน เพิ่มข้อมูลใหม่ได้ที่แถบด้านซ้าย")
