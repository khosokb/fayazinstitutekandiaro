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
GALLERY_DIR = "gallery"

ADMIN_CREDENTIALS = {
    "username": "admin",
    "password_hash": hashlib.sha256("fayazadmin123".encode()).hexdigest()
}

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GALLERY_DIR, exist_ok=True)

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
    "Home",
    "Register",
    "Login",
    "Admission Form",
    "Courses",
    "Teachers",
    "Gallery",
    "Contact",
    "Admin Panel",
])

def show_footer():
    st.write("---")
    st.write("© FAYAZ INSTITUTE OF COMPUTER SCIENCE AND EDUCATION KANDIARO")

# ----------------- Home Page -----------------
if menu == "Home":
    st.header("Welcome")
    st.subheader("FAYAZ INSTITUTE OF COMPUTER SCIENCE AND EDUCATION KANDIARO")
    st.write("We provide high-quality education in Computer Science, English, Maths, ICT and more.")
    # Default home image from gallery if exists
    gallery_images = os.listdir(GALLERY_DIR)
    if gallery_images:
        st.image(os.path.join(GALLERY_DIR, gallery_images[0]), caption="Welcome to FICSE Kandiaro", use_column_width=True)
    show_footer()

# ----------------- Register Page -----------------
elif menu == "Register":
    st.header("Student Registration")
    st.write("Create login for student portal.")
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

# ----------------- Login Page -----------------
elif menu == "Login":
    st.header("Student Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        users = load_json(USERS_FILE)
        if username in users and users[username]["password"] == make_hash(password):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success("Login successful.")
        else:
            st.error("Invalid login.")
    if st.session_state.get("logged_in"):
        st.write("---")
        st.subheader("Student Dashboard")
        uname = st.session_state["username"]
        uinfo = load_json(USERS_FILE).get(uname, {})
        st.write(f"**Name:** {uname}")
        st.write(f"**CNIC:** {uinfo.get('cnic')}")
        st.write(f"**Mobile:** {uinfo.get('mobile')}")
        studs = load_json(STUDENTS_FILE)
        admission_record = None
        for adm_no, rec in studs.items():
            if rec.get("full_name") == uname or rec.get("cnic") == uinfo.get("cnic"):
                admission_record = rec
                break
        if admission_record:
            st.success("Admission Record Found")
            st.write(f"**Admission No:** {admission_record['admission_no']}")
            st.write(f"**Status:** {admission_record['status']}")
            if st.button("Download Admission PDF"):
                pdf_path = generate_admission_pdf(admission_record, f"{admission_record['admission_no']}.pdf")
                with open(pdf_path, "rb") as f:
                    st.download_button("Download PDF", data=f, file_name=f"{admission_record['admission_no']}.pdf", mime="application/pdf")
        else:
            st.info("No admission found. Submit admission form.")
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.rerun()

# ----------------- Admission Form Page -----------------
elif menu == "Admission Form":
    st.header("Admission Form 2025")
    pre_username = st.session_state.get("username") if st.session_state.get("logged_in") else ""
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Full Name", value=pre_username)
        father_name = st.text_input("Father Name")
        date_of_birth = st.date_input("Date of Birth")
        religion = st.text_input("Religion")
        contact_no = st.text_input("Contact No")
        qualification = st.text_input("Qualification")
    with col2:
        caste = st.text_input("Caste")
        gender = st.radio("Gender", ["Male", "Female"])
        nationality = st.text_input("Nationality")
        whatsapp_no = st.text_input("WhatsApp No")
        email = st.text_input("Email")
        photo = st.file_uploader("Upload Passport Size Photo", type=["jpg", "jpeg", "png"])
    present_address = st.text_area("Present Address")
    st.write("### Select Course for Admission")
    colA, colB = st.columns(2)
    with colA:
        c1 = st.checkbox("Diploma in Information Technology (12 Months)")
        c2 = st.checkbox("Certificate in Information Technology (06 Months)")
        c3 = st.checkbox("Short Course of Computer Science (04 Months)")
    with colB:
        c4 = st.checkbox("MS Office / Word / Excel / PowerPoint (02 Months)")
        c5 = st.checkbox("Typing (English, Urdu, Sindhi) (02 Months)")
        c6 = st.checkbox("Special Course - All Subjects Expert (02 Months)")
        c7 = st.checkbox("Tuition (Select Class)")
    tuition_class = ""
    if c7:
        tuition_class = st.text_input("Enter Class (e.g., 6th, 7th, 8th)")
    selected_courses = []
    if c1: selected_courses.append("Diploma in Information Technology (12 Months)")
    if c2: selected_courses.append("Certificate in Information Technology (06 Months)")
    if c3: selected_courses.append("Short Course of Computer Science (04 Months)")
    if c4: selected_courses.append("MS Office / Word / Excel / PowerPoint (02 Months)")
    if c5: selected_courses.append("Typing (English, Urdu, Sindhi) (02 Months)")
    if c6: selected_courses.append("Special Course - All Subjects Expert (02 Months)")
    if c7: selected_courses.append(f"Tuition Class: {tuition_class}")
    if st.button("Submit Admission"):
        if not (full_name and father_name and contact_no and selected_courses and present_address):
            st.error("Please fill all required fields.")
        else:
            admission_no = generate_admission_no()
            photo_path = save_uploaded_file(photo, admission_no)
            student = {
                "admission_no": admission_no,
                "full_name": full_name,
                "father_name": father_name,
                "date_of_birth": str(date_of_birth),
                "religion": religion,
                "caste": caste,
                "gender": gender,
                "nationality": nationality,
                "contact_no": contact_no,
                "whatsapp_no": whatsapp_no,
                "email": email,
                "qualification": qualification,
                "present_address": present_address,
                "courses": selected_courses,
                "photo_path": photo_path,
                "status": "Pending",
                "applied_at": str(datetime.datetime.now())
            }
            save_student(student)
            st.success(f"Admission submitted successfully! Your Admission No: **{admission_no}**")

# ----------------- Courses Page -----------------
elif menu == "Courses":
    st.header("Courses Offered")
    courses = [
        ("Diploma in Information Technology", "12 Months", "PKR 15,000"),
        ("Certificate in Information Technology", "06 Months", "PKR 10,000"),
        ("Short Course of Computer Science", "04 Months", "PKR 8,000"),
        ("MS Office / Word / Excel / PowerPoint", "02 Months", "PKR 5,000"),
        ("Typing English/Urdu/Sindhi", "02 Months", "PKR 4,000"),
        ("Special Course All Subjects Expert", "02 Months", "PKR 6,000"),
    ]
    for c, d, f in courses:
        st.subheader(c)
        st.write(f"Duration: **{d}**, Fee: **{f}**")
        st.write("-----")

# ----------------- Teachers Page -----------------
elif menu == "Teachers":
    st.header("Our Teachers")
    t = load_json(TEACHERS_FILE)
    for tid, info in t.items():
        st.write(f"**{info['name']}** — {info['subject']}")

# ----------------- Gallery Page -----------------
elif menu == "Gallery":
    st.header("Academy Teachers & Alumni Gallery")
    st.subheader("Upload New Photos")
    uploaded_photos = st.file_uploader(
        "Select photos to upload (Teachers / Alumni)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )
    if uploaded_photos:
        for photo in uploaded_photos:
            save_path = os.path.join(GALLERY_DIR, photo.name)
            with open(save_path, "wb") as f:
                f.write(photo.getbuffer())
        st.success(f"{len(uploaded_photos)} photo(s) uploaded successfully!")
    st.subheader("Gallery")
    gallery_images = os.listdir(GALLERY_DIR)
    if gallery_images:
        cols = st.columns(3)
        for idx, img_file in enumerate(gallery_images):
            img_path = os.path.join(GALLERY_DIR, img_file)
            cols[idx % 3].image(img_path, caption=img_file, use_column_width=True)
    else:
        st.info("No photos in gallery yet. Upload to display here.")

# ----------------- Contact Page -----------------
elif menu == "Contact":
    st.header("Contact Us")
    st.write("Address: Kandiaro — Sindh, Pakistan")
    st.write("Phone / WhatsApp: 0300-XXXXXXX")
    st.write("Email: info@fayazinstitute.example")
    st.markdown("[Open Google Maps](https://maps.google.com)")

# ----------------- Admin Panel Page -----------------
elif menu == "Admin Panel":
    st.header("Admin Panel")
    st.write("Admin can view admission requests, approve or reject, and download student PDFs.")
    admin_user = st.text_input("Admin Username")
    admin_pass = st.text_input("Admin Password", type="password")
    if st.button("Admin Login"):
        if admin_user == ADMIN_CREDENTIALS["username"] and make_hash(admin_pass) == ADMIN_CREDENTIALS["password_hash"]:
            st.session_state["admin_logged_in"] = True
            st.success("Admin logged in successfully")
        else:
            st.error("Invalid admin credentials")
    if st.session_state.get("admin_logged_in"):
        st.write("---")
        st.subheader("Admission Requests")
        studs = load_json(STUDENTS_FILE)
        if not studs:
            st.info("No admission requests yet.")
        else:
            for adm_no, rec in studs.items():
                st.markdown(f"### {rec.get('full_name')} — **{adm_no}**")
                st.write(f"**Course(s):** {', '.join(rec.get('courses', []))}")
                st.write(f"**Mobile:** {rec.get('contact_no')}")
                st.write(f"**Status:** {rec.get('status')}")
                if rec.get("photo_path") and os.path.exists(rec["photo_path"]):
                    st.image(rec["photo_path"], width=150)
                cols = st.columns(4)
                if cols[0].button(f"Approve {adm_no}", key=f"app-{adm_no}"):
                    rec["status"] = "Approved"
                    save_student(rec)
                    st.success(f"{adm_no} approved")
                    st.rerun()
                if cols[1].button(f"Reject {adm_no}", key=f"rej-{adm_no}"):
                    rec["status"] = "Rejected"
                    save_student(rec)
                    st.warning(f"{adm_no} rejected")
                    st.rerun()
                if cols[2].button(f"Create User {adm_no}", key=f"cu-{adm_no}"):
                    users = load_json(USERS_FILE)
                    uname = rec.get("full_name")
                    if uname in users:
                        st.info("User already exists.")
                    else:
                        pwd = rec.get("contact_no", "changeme")
                        save_user(uname, {
                            "password": make_hash(pwd),
                            "cnic": rec.get("cnic",""),
                            "mobile": rec.get("contact_no","")
                        })
                        st.success(f"User {uname} created with default password.")
                if cols[3].button(f"Download PDF {adm_no}", key=f"pdf-{adm_no}"):
                    pdf_path = generate_admission_pdf(rec, f"{adm_no}.pdf")
                    with open(pdf_path, "rb") as f:
                        st.download_button("Download PDF", data=f, file_name=f"{adm_no}.pdf", mime="application/pdf")

show_footer()
