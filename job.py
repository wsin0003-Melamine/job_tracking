import streamlit as tf
import pandas as pd
import os

# ตั้งค่าหน้าเว็บ
tf.set_page_config(page_title="Job Application Tracker", layout="wide")
tf.title("💼 Job Application Tracker")

# ชื่อไฟล์สำหรับเก็บข้อมูล (จำลองฐานข้อมูลเป็นไฟล์ CSV)
DB_FILE = "job_applications.csv"

# ฟังก์ชันสำหรับโหลดข้อมูล
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Company", "Position", "Date Applied", "Status", "Notes"])

# ฟังก์ชันสำหรับบันทึกข้อมูล
def save_data(df):
    df.to_csv(DB_FILE, index=False)

# โหลดข้อมูลปัจจุบันลงใน Session State
if "df" not in tf.session_state:
    tf.session_state.df = load_data()

df = tf.session_state.df

# --- ส่วนจัดการข้อมูลใน Sidebar ---
tf.sidebar.header("📝 Manage Applications")
action = tf.sidebar.radio("Choose Action:", ["➕ Add New Job", "🔄 Update Existing Job"])

# รายการสถานะทั้งหมด
status_options = ["Applied", "Interviewing", "Offered", "Rejected", "Withdrawn"]

if action == "➕ Add New Job":
    tf.sidebar.subheader("Add New Application")
    with tf.sidebar.form("add_form", clear_on_submit=True):
        company = tf.text_input("Company Name")
        position = tf.text_input("Position")
        date_applied = tf.date_input("Date Applied")
        status = tf.selectbox("Status", status_options)
        notes = tf.text_area("Notes / Details")
        
        submit_btn = tf.form_submit_button("Add Job")
        
        if submit_btn:
            if company and position:
                # ตรวจสอบว่าบริษัทนี้มีอยู่แล้วหรือไม่ เพื่อป้องกันการสับสน
                if company.lower() in df["Company"].str.lower().values:
                    tf.sidebar.warning(f"⚠️ {company} already exists! Use 'Update Existing Job' to change its status.")
                else:
                    new_row = pd.DataFrame([{
                        "Company": company,
                        "Position": position,
                        "Date Applied": str(date_applied),
                        "Status": status,
                        "Notes": notes
                    }])
                    df = pd.concat([df, new_row], ignore_index=True)
                    save_data(df)
                    tf.session_state.df = df
                    tf.sidebar.success(f"🎉 Added {company} successfully!")
                    tf.rerun()
            else:
                tf.sidebar.error("❌ Please fill in Company Name and Position.")

elif action == "🔄 Update Existing Job":
    tf.sidebar.subheader("Update Job Status")
    if df.empty:
        tf.sidebar.info("No applications found to update. Please add a new job first.")
    else:
        # ดึงรายชื่อบริษัทที่มีอยู่มาทำเป็นรายการให้เลือก
        company_list = df["Company"].tolist()
        selected_company = tf.sidebar.selectbox("Select Company to Update:", company_list)
        
        # ดึงข้อมูลแถวเดิมของบริษัทที่เลือกมาแสดงเป็นค่าเริ่มต้น
        row_idx = df[df["Company"] == selected_company].index[0]
        current_position = df.loc[row_idx, "Position"]
        current_status = df.loc[row_idx, "Status"]
        current_notes = df.loc[row_idx, "Notes"] if pd.notna(df.loc[row_idx, "Notes"]) else ""
        
        with tf.sidebar.form("update_form"):
            tf.write(f"**Updating:** {selected_company}")
            position = tf.text_input("Position", value=current_position)
            
            # ค้นหาตำแหน่งดัชนีของสถานะปัจจุบันเพื่อเลือกเป็นค่าเริ่มต้นในกล่อง
            try:
                status_idx = status_options.index(current_status)
            except ValueError:
                status_idx = 0
                
            status = tf.selectbox("New Status", status_options, index=status_idx)
            notes = tf.text_area("Update Notes / Details", value=current_notes)
            
            update_btn = tf.form_submit_button("Save Updates")
            
            if update_btn:
                # อัปเดตข้อมูลทับแถวเดิมโดยตรง ไม่เพิ่มแถวใหม่
                df.loc[row_idx, "Position"] = position
                df.loc[row_idx, "Status"] = status
                df.loc[row_idx, "Notes"] = notes
                
                save_data(df)
                tf.session_state.df = df
                tf.sidebar.success(f"🔄 Updated {selected_company} successfully!")
                tf.rerun()

# --- ส่วนแสดงผลหน้าแรก (Dashboard & Table) ---
if df.empty:
    tf.info("👋 Welcome! Your tracker is currently empty. Use the sidebar on the left to add your first job application.")
else:
    # 1. แดชบอร์ดสรุปภาพรวม (Metrics)
    col1, col2, col3, col4 = tf.columns(4)
    col1.metric("Total Applications", len(df))
    col2.metric("Interviewing 🎯", len(df[df["Status"] == "Interviewing"]))
    col3.metric("Offered 🎉", len(df[df["Status"] == "Offered"]))
    col4.metric("Pending ⏳", len(df[df["Status"] == "Applied"]))
    
    tf.markdown("---")
    
    # 2. ตัวกรองข้อมูลบนตาราง (Filters)
    tf.subheader("🔍 Filter & View Applications")
    filter_status = tf.multiselect("Filter by Status:", status_options, default=status_options)
    
    # กรองข้อมูลตามที่เลือก
    filtered_df = df[df["Status"].isin(filter_status)]
    
    # 3. ตารางแสดงผล
    tf.dataframe(filtered_df, use_container_width=True, hide_index=True)
