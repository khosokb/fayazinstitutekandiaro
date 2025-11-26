import streamlit as st
import hashlib
import json
import os
import csv
import datetime
import random
from io import StringIO
from fpdf import FPDF

# ----------------- Configuration -----------------
APP_TITLE = "FAYAZ INSTITUTE OF COMPUTER SCIENCE AND EDUCATION KANDIARO"
USERS_FILE = "users.json"
STUDENTS_FILE = "students.json"
TEACHERS_FILE = "teachers.json"
UPLOAD_DIR = "uploads"

ADMIN_CREDENTIALS = {
    "username": "admin",
    "password_hash": hashlib.sha256("fayazadmin123".encode()).hexdigest()
}

os.makedirs(UPLOAD_DIR, exist_ok=True)

# ----------------- Helper functions -----------------

def make_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_json(path: str):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def save_student(student: dict):
    data = load_json(STUDENTS_FILE)
    data[student["admission_no"]] = student
    save_json(STUDENTS_FILE, data)

def save_user(username: str, info: dict):
    users = load_json(USERS_FILE)
    users[username] = info
    save_json(USERS_FILE, users)

def generate_admission_no():
    now = datetime.datetime.now()
    rand = random.randint(100, 999)
    return f"FICSE-{now.year}{now.month:02d}{now.day:02d}-{rand}"

def save_uploaded_file(uploaded_file, admission_no: str):
    if uploaded_file is None:
        return None
    ext = os.path.splitext(uploaded_file.name)[1]
    filename = f"{admission_no}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path

# ----------------- PDF Generator -----------------

def generate_admission_pdf(student, output_path="admission_form.pdf"):
    pdf = FPDF("P", "mm", "A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Fayaz Institute", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 6, "Of Computer Science & Education Kandiaro", ln=True, align="C")
    pdf.ln(4)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Admission Form 2025", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, f"Registration No: {student.get('admission_no')}", ln=True)

    if student.get("photo_path") and os.path.exists(student["photo_path"]):
        pdf.image(student["photo_path"], x=160, y=35, w=35)

    pdf.set_font("Arial", "", 11)
    pdf.ln(10)
    pdf.cell(0, 8, f"Full Name: {student.get('full_name','')}", ln=True)
    pdf.cell(0, 8, f"Father Name: {student.get('father_name','')}", ln=True)
    pdf.cell(0, 8, f"Date of Birth: {student.get('date_of_birth','')}", ln=True)
    pdf.cell(0, 8, f"Gender: {student.get('gender','')}", ln=True)
    pdf.cell(0, 8, f"Religion: {student.get('religion','')}", ln=True)
    pdf.cell(0, 8, f"Caste: {student.get('caste','')}", ln=True)
    pdf.cell(0, 8, f"Nationality: {student.get('nationality','')}", ln=True)
    pdf.cell(0, 8, f"Qualification: {student.get('qualification','')}", ln=True)
    pdf.cell(0, 8, f"Contact No: {student.get('contact_no','')}", ln=True)
    pdf.cell(0, 8, f"WhatsApp No: {student.get('whatsapp_no','')}", ln=True)
    pdf.cell(0, 8, f"Email: {student.get('email','')}", ln=True)

    pdf.multi_cell(0, 8, f"Present Address: {student.get('present_address','')}")
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Selected Courses:", ln=True)
    pdf.set_font("Arial", "", 11)

    for c in student.get("courses", []):
        pdf.cell(0, 7, f"- {c}", ln=True)

    pdf.ln(10)
    pdf.cell(0, 8, "Signature of Student: ______________________", ln=True)

    pdf.output(output_path)
    return output_path

# ----------------- Load Initial Data -----------------

users = load_json(USERS_FILE)
students = load_json(STUDENTS_FILE)
teachers = load_json(TEACHERS_FILE)

if not teachers:
    teachers = {
        "T001": {"name": "Muhammad Ali", "subject": "Mathematics"},
        "T002": {"name": "Aisha Bano", "subject": "Computer Science"},
        "T003": {"name": "Sara Khan", "subject": "English"},
    }
    save_json(TEACHERS_FILE, teachers)

# ----------------- Streamlit Page Layout -----------------
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)

menu = st.sidebar.selectbox("Go to", [
    "Home", "Register", "Login", "Admission Form", "Courses", "Teachers", "Contact", "Admin Panel"
])

def show_footer():
    st.write("---")
    st.write("© FAYAZ INSTITUTE OF COMPUTER SCIENCE AND EDUCATION KANDIARO")

# ----------------- Home -----------------
if menu == "Home":
    st.header("Welcome")
    st.subheader(APP_TITLE)
    st.write("We provide high-quality education in Computer Science, English, Maths, ICT and more.")
    st.image("https://images.unsplash.com/photo-1522071820081-009f0129c71c", caption="Learn — Practice — Succeed")
    show_footer()

# ----------------- Register -----------------
elif menu == "Register":
    st.header("Student Registration")
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Full Name")
        cnic = st.text_input("CNIC (without dashes)")
        mobile = st.text_input("Mobile Number")
    with col2:
        password = st.text_input("Password", type="password")
        password2 = st.text_input("Confirm Password", type="password")
        agree = st.checkbox("I confirm the information is correct.")

    if st.button("Register"):
        if not (username and password and password2 and cnic and mobile):
            st.error("All fields required.")
        elif password != password2:
            st.error("Passwords do not match.")
        elif username in users:
            st.error("Username already exists.")
        elif not agree:
            st.error("Please confirm the info.")
        else:
            save_user(username, {
                "cnic": cnic,
                "mobile": mobile,
                "password": make_hash(password),
                "created_at": str(datetime.datetime.now())
            })
            st.success("Registration successful. Go to Login.")

# ----------------- Login -----------------
elif menu == "Login":
    st.header("Student Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        users = load_json(USERS_FILE)
        if username in users and users[username]["password"] == make_hash(password):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success("Login successful")
        else:
            st.error("Invalid login.")

    # Reset password
    st.subheader("Reset Password")
    reset_username = st.text_input("Enter username to reset password")
    new_password = st.text_input("New password", type="password")
    if st.button("Reset Password"):
        users = load_json(USERS_FILE)
        if reset_username in users:
            users[reset_username]["password"] = make_hash(new_password)
            save_json(USERS_FILE, users)
            st.success(f"Password reset successfully for {reset_username}")
        else:
            st.error("Username not found.")

show_footer()
