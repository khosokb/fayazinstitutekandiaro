import streamlit as st
import hashlib
import json
import os
import datetime
import random
from fpdf import FPDF
import base64

# ----------------- Configuration -----------------
APP_TITLE = "FAYAZ INSTITUTE OF COMPUTER SCIENCE AND EDUCATION KANDIARO"
USERS_FILE = "users.json"
STUDENTS_FILE = "students.json"
TEACHERS_FILE = "teachers.json"
FEES_FILE = "fees.json"
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

# ----------------- forgot_password -----------------
def forgot_password():
    st.subheader("Reset Password")

    username = st.text_input("Enter Username")
    cnic = st.text_input("Enter CNIC / Mobile")
    new_pass = st.text_input("Enter New Password", type="password")
    confirm_pass = st.text_input("Confirm New Password", type="password")

    if st.button("Reset Password"):
        if new_pass != confirm_pass:
            st.error("Passwords do not match!")
            return
        
        users = load_json(USERS_FILE)

        if username in users and users[username]["cnic"] == cnic:

            hashed = make_hash(new_pass)
            users[username]["password"] = hashed

            save_json(USERS_FILE, users)

            st.success("Password reset successfully! Please login again.")
            st.rerun()

        else:
            st.error("User not found or CNIC mismatch!")

# ---------------- Scholarship Page ----------------
def scholarship_page():
    st.title("🎓 Scholarships")
    st.markdown("---")
    
    st.info("Explore available scholarships, eligibility criteria, and application procedures below.")
    
    # Example scholarship cards
    st.subheader("Available Scholarships")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Merit-Based Scholarship**")
        st.write("Awarded to students with outstanding academic performance.")
        st.write("- Eligibility: GPA ≥ 3.5")
        st.write("- Amount: 50% tuition fee waiver")
        if st.button("Apply Now", key="merit_scholarship"):
            st.success("Redirecting to scholarship application form...")

    with col2:
        st.markdown("**Need-Based Scholarship**")
        st.write("For students who need financial assistance.")
        st.write("- Eligibility: Verified financial documents")
        st.write("- Amount: Up to 100% tuition fee waiver")
        if st.button("Apply Now", key="need_scholarship"):
            st.success("https://www.google.com/")

    st.markdown("---")
    st.write("For more information, contact our office or visit the official scholarship page.")

# ---------------- Careers Page ----------------
def careers_page():
    st.title("💼 Careers")
    st.markdown("---")
    
    st.info("Find latest job opportunities, internships, and guidance on career planning.")
    
    # Example career cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Teaching Positions**")
        st.write("Join our academy as a qualified instructor.")
        st.write("- Subjects: Computer Science, Math, English")
        st.write("- Apply: Submit resume and cover letter")
        if st.button("Apply Now", key="teaching_job"):
            st.success("Redirecting to career application form...")

    with col2:
        st.markdown("**Administrative Positions**")
        st.write("Work in academy administration, admissions, and support.")
        st.write("- Roles: Admin, Accounts, Student Support")
        if st.button("Apply Now", key="admin_job"):
            st.success("Redirecting to career application form...")
    
    st.markdown("---")
    st.write("For more information about careers, contact HR or visit our careers portal.")

# ---------------- Result Page ----------------
def result_page():
    st.title("📊 Scholarship Result")
    st.markdown("---")
    
    st.info("Check your scholarship exam results below.")

    # Input student info to fetch result
    admission_no = st.text_input("Enter your Admission Number")
    
    if st.button("View Result"):
        students = load_json(STUDENTS_FILE)
        
        if admission_no in students:
            student = students[admission_no]
            
            if "scholarship_marks" in student:
                # Use .get() to safely fetch the name
                student_name = student.get("name") or student.get("full_name") or "Unknown"
                
                st.success(f"Student: {student_name}")
                st.write(f"Marks Obtained: {student['scholarship_marks']}")
                st.write(f"Status: {'Passed' if student['scholarship_marks'] >= 50 else 'Failed'}")
            else:
                st.warning("Marks not available yet.")
        else:
            st.error("Admission Number not found.")


# ---------------- Certificate Page ----------------
CERT_DIR = "certificates"
os.makedirs(CERT_DIR, exist_ok=True)

def certificate_page():
    st.title("🎓 Course Completion Certificate")
    st.markdown("---")
    
    st.info("Download your professionally designed course completion certificate below.")
    
    admission_no = st.text_input("Enter your Admission Number")
    
    if st.button("Download Certificate"):
        students = load_json(STUDENTS_FILE)
        
        if admission_no in students:
            student = students[admission_no]
            
            if student.get("course_completed", False):
                pdf = FPDF('L', 'mm', 'A4')
                pdf.add_page()

                # Add border
                pdf.set_line_width(1)
                pdf.rect(5, 5, 287, 200)  # A4 landscape

                # Add Logo
                logo_path = "logo.png"
                if os.path.exists(logo_path):
                    pdf.image(logo_path, x=10, y=10, w=30)

                # Title
                pdf.set_font("Arial", 'B', 36)
                pdf.set_text_color(0, 51, 102)  # Dark Blue
                pdf.cell(0, 60, "Certificate of Completion", ln=True, align='C')

                # Subtitle
                pdf.set_font("Arial", '', 20)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(10)
                pdf.multi_cell(0, 10, f"This is to certify that {student['name']}", align='C')
                pdf.ln(5)
                pdf.multi_cell(0, 10, "has successfully completed the course at FICSE.", align='C')

                # Footer / date
                pdf.ln(20)
                pdf.set_font("Arial", 'I', 14)
                pdf.cell(0, 10, f"Date: {datetime.datetime.now().strftime('%d-%m-%Y')}", ln=True, align='C')

                # Optional signature
                pdf.ln(15)
                pdf.set_font("Arial", '', 12)
                pdf.cell(0, 10, "_____________________", ln=True, align='R')
                pdf.cell(0, 5, "Director / Principal", ln=True, align='R')

                # Save PDF
                pdf_file = os.path.join(CERT_DIR, f"Certificate_{student['name']}.pdf")
                pdf.output(pdf_file)

                # Download button
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="📥 Download Certificate",
                        data=f,
                        file_name=f"Certificate_{student['name']}.pdf",
                        mime="application/pdf"
                    )
            else:
                st.warning("Course not completed yet.")
        else:
            st.error("Admission Number not found.")


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
fees = load_json(FEES_FILE)
teachers = load_json(TEACHERS_FILE)
if not teachers:
    teachers = {
        "T001": {"name": "Muhammad Ali", "subject": "Mathematics"},
        "T002": {"name": "Aisha Bano", "subject": "Computer Science"},
        "T003": {"name": "Sara Khan", "subject": "English"},
    }
    save_json(TEACHERS_FILE, teachers)

# ----------------- Streamlit Page Config -----------------
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)

menu = st.sidebar.selectbox("Go to", [
    "Home",
    "Register",
    "Forgot Password",
    "Login",
    "Admission Form",
    "Courses",
    "Teachers",
    "Gallery",
    "Contact",
    "Admin Panel",
    "Scholarship",
    "Careers",
    "Result",
    "Certificate",
])

# ----------------- Footer -----------------
def show_footer():
    st.write("---")
    st.write("© FAYAZ INSTITUTE OF COMPUTER SCIENCE AND EDUCATION KANDIARO")

# ----------------- Home Page -----------------
if menu == "Home":
    st.header("Welcome")
    st.subheader(APP_TITLE)
    st.write("We provide high-quality education in Computer Science, English, Maths, ICT and more.")
    
    # Display gallery images uploaded by admin
    gallery_images = os.listdir(GALLERY_DIR)
    if gallery_images:
        st.subheader("Gallery")
        cols = st.columns(3)
        for idx, img_file in enumerate(gallery_images):
            img_path = os.path.join(GALLERY_DIR, img_file)
            cols[idx % 3].image(img_path, caption=img_file, use_container_width=True)
    else:
        st.info("No photos in gallery yet. Admin can upload images in the Admin Panel.")
    
    # Display alumni / achievements images
    alumni_dir = "alumni"
    os.makedirs(alumni_dir, exist_ok=True)
    alumni_images = os.listdir(alumni_dir)
    if alumni_images:
        st.subheader("Alumni Achievements")
        cols = st.columns(3)
        for idx, img_file in enumerate(alumni_images):
            img_path = os.path.join(alumni_dir, img_file)
            cols[idx % 3].image(img_path, caption=img_file, use_container_width=True)
    else:
        st.info("No alumni achievements uploaded yet.")
    
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

# ----------------- Forgot_Password -----------------
elif menu == "Forgot Password":
    forgot_password()

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
        # Date of Birth updated from 1950 to today
        date_of_birth = st.date_input(
            "Date of Birth", 
            min_value=datetime.date(1950, 1, 1),
            max_value=datetime.date.today()
        )
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
    st.header("Gallery")
    st.info("Gallery images are uploaded by Admin only.")
    gallery_images = os.listdir(GALLERY_DIR)
    if gallery_images:
        cols = st.columns(3)
        for idx, img_file in enumerate(gallery_images):
            img_path = os.path.join(GALLERY_DIR, img_file)
            cols[idx % 3].image(img_path, caption=img_file, use_container_width=True)
    else:
        st.info("No images in gallery yet.")

# ----------------- Contact Page -----------------
elif menu == "Contact":
    st.header("Contact Us")
    st.write("Address: Kandiaro — Sindh, Pakistan")
    st.write("Phone / WhatsApp: 0300-XXXXXXX")
    st.write("Email: info@fayazinstitute.example")
    st.markdown("[Open Google Maps](https://maps.google.com)")

# ----------------- Admin Panel -----------------
elif menu == "Admin Panel":
    st.header("Admin Panel")
    
    admin_user = st.text_input("Admin Username")
    admin_pass = st.text_input("Admin Password", type="password")
    if st.button("Admin Login"):
        if admin_user == ADMIN_CREDENTIALS["username"] and make_hash(admin_pass) == ADMIN_CREDENTIALS["password_hash"]:
            st.session_state["admin_logged_in"] = True
            st.success("Admin logged in successfully")
        else:
            st.error("Invalid admin credentials")

    if st.session_state.get("admin_logged_in"):
        if st.button("Logout"):
            st.session_state["admin_logged_in"] = False
            st.rerun()

        st.write("---")

        # ----------------- Student Information -----------------
        st.subheader("Registered Students & Admission Forms")
        users_data = load_json(USERS_FILE)
        students_data = load_json(STUDENTS_FILE)

        search_option = st.radio("Search by:", ["All", "Name", "CNIC", "Admission No"])

        search_query = ""
        if search_option != "All":
            search_query = st.text_input(f"Enter {search_option}")

        filtered_students = []
        for adm_no, student in students_data.items():
            user_match = users_data.get(student.get("full_name"), {})
            if search_option == "All":
                filtered_students.append(student)
            elif search_option == "Name" and search_query.lower() in student.get("full_name","").lower():
                filtered_students.append(student)
            elif search_option == "CNIC" and search_query in user_match.get("cnic",""):
                filtered_students.append(student)
            elif search_option == "Admission No" and search_query.lower() in adm_no.lower():
                filtered_students.append(student)

        st.write(f"**Total Students Found: {len(filtered_students)}**")
        for student in filtered_students:
            st.markdown(f"### {student.get('full_name')} | Admission No: {student.get('admission_no')}")
            st.write(f"- Father Name: {student.get('father_name')}")
            st.write(f"- Date of Birth: {student.get('date_of_birth')}")
            st.write(f"- Gender: {student.get('gender')}")
            st.write(f"- Contact No: {student.get('contact_no')}")
            st.write(f"- WhatsApp No: {student.get('whatsapp_no')}")
            st.write(f"- Email: {student.get('email')}")
            st.write(f"- Qualification: {student.get('qualification')}")
            st.write(f"- Courses: {', '.join(student.get('courses', []))}")
            st.write(f"- Status: {student.get('status')}")
            if student.get("photo_path") and os.path.exists(student["photo_path"]):
                st.image(student["photo_path"], width=120)
            
            if st.button(f"Delete Student {student.get('full_name')}", key=f"del_student_{student['admission_no']}"):
                students_data.pop(student["admission_no"])
                save_json(STUDENTS_FILE, students_data)
                st.success(f"{student.get('full_name')} deleted successfully!")
                st.rerun()

        st.write("---")

        # ----------------- Upload Scholarship Marks -----------------
        st.subheader("Upload Scholarship Marks")

        if students_data:
            student_names = [
                f"{s.get('name', 'Unknown')} ({admission_no})" 
                for admission_no, s in students_data.items()
            ]
            selected_student = st.selectbox("Select Student for Scholarship Marks", student_names)

            marks = st.number_input("Enter Scholarship Marks (0-100)", min_value=0, max_value=100, step=1)

            if st.button("Submit Scholarship Marks"):
                admission_no = selected_student.split("(")[-1].replace(")", "")
                students_data[admission_no]["scholarship_marks"] = marks
                save_json(STUDENTS_FILE, students_data)
                st.success(f"Scholarship marks updated for {students_data[admission_no].get('name', 'Unknown')}!")

        # ----------------- Show All Students Scholarship Marks -----------------
        st.subheader("All Students Scholarship Marks")

        if students_data:
            student_list = []
            for admission_no, student in students_data.items():
                student_list.append({
                    "Admission No": admission_no,
                    "Name": student.get("name", "Unknown"),
                    "Scholarship Marks": student.get("scholarship_marks", "")
                })
            st.dataframe(student_list)
        else:
            st.info("No student data to display.")

        st.write("---")

        # ----------------- Gallery Upload -----------------
        st.subheader("Manage Gallery Photos")
        uploaded_gallery = st.file_uploader(
            "Upload Photos to Gallery (Will appear on Home Page)", 
            type=["jpg","jpeg","png"], 
            accept_multiple_files=True
        )
        if uploaded_gallery:
            for file in uploaded_gallery:
                save_path = os.path.join(GALLERY_DIR, file.name)
                with open(save_path, "wb") as f:
                    f.write(file.getbuffer())
            st.success("Gallery photos uploaded successfully!")

        st.write("### Existing Gallery Images")
        gallery_images = os.listdir(GALLERY_DIR)
        if gallery_images:
            cols = st.columns(3)
            for idx, img_file in enumerate(gallery_images):
                img_path = os.path.join(GALLERY_DIR, img_file)
                with cols[idx % 3]:
                    st.image(img_path, caption=img_file, use_container_width=True)
                    if st.button("Delete", key=f"del_gallery_{img_file}"):
                        os.remove(img_path)
                        st.success(f"{img_file} deleted successfully")
                        st.rerun()
        else:
            st.info("No images in gallery yet.")

        st.write("---")

        # ----------------- Manage Teachers -----------------
        st.subheader("Manage Teachers")
        teacher_name = st.text_input("Teacher Name")
        teacher_subject = st.text_input("Teacher Subject")
        teacher_photo = st.file_uploader("Teacher Photo", type=["jpg", "jpeg", "png"], key="t_photo")
        if st.button("Add / Update Teacher"):
            if teacher_name and teacher_subject:
                t_id = f"T{random.randint(100,999)}"
                photo_path = None
                if teacher_photo:
                    photo_path = os.path.join(GALLERY_DIR, f"teacher_{teacher_name}_{teacher_photo.name}")
                    with open(photo_path, "wb") as f:
                        f.write(teacher_photo.getbuffer())
                teachers[t_id] = {
                    "name": teacher_name,
                    "subject": teacher_subject,
                    "photo_path": photo_path
                }
                save_json(TEACHERS_FILE, teachers)
                st.success(f"Teacher {teacher_name} added/updated successfully")

        st.write("### Existing Teachers")
        for tid, info in teachers.items():
            cols = st.columns([2,2,1,1])
            cols[0].write(f"**{info['name']}**")
            cols[1].write(f"{info['subject']}")
            if info.get("photo_path") and os.path.exists(info["photo_path"]):
                cols[2].image(info["photo_path"], width=70)
            if cols[3].button("Delete", key=f"del_teacher_{tid}"):
                teachers.pop(tid)
                save_json(TEACHERS_FILE, teachers)
                st.success("Deleted successfully")
                st.rerun()

        st.write("---")

        # ----------------- Alumni / Achievements Upload -----------------
        st.subheader("Manage Alumni Achievements")
        alumni_dir = "alumni"
        os.makedirs(alumni_dir, exist_ok=True)
        uploaded_alumni = st.file_uploader(
            "Upload Alumni Achievement Photos", 
            type=["jpg","jpeg","png"], 
            accept_multiple_files=True,
            key="alumni_upload"
        )
        if uploaded_alumni:
            for file in uploaded_alumni:
                save_path = os.path.join(alumni_dir, file.name)
                with open(save_path, "wb") as f:
                    f.write(file.getbuffer())
            st.success("Alumni photos uploaded successfully!")

        st.write("### Existing Alumni Photos")
        alumni_images = os.listdir(alumni_dir)
        if alumni_images:
            cols = st.columns(3)
            for idx, img_file in enumerate(alumni_images):
                img_path = os.path.join(alumni_dir, img_file)
                with cols[idx % 3]:
                    st.image(img_path, caption=img_file, use_container_width=True)
                    if st.button("Delete", key=f"del_alumni_{img_file}"):
                        os.remove(img_path)
                        st.success(f"{img_file} deleted successfully")
                        st.rerun()
        else:
            st.info("No alumni achievements uploaded yet.")


	# ------------------ Upload Scholarship Marks ------------------
	

# ----------------- Scholarship -----------------
elif menu == "Scholarship":
    scholarship_page()

# ----------------- Careers -----------------
elif menu == "Careers":
    careers_page()


# ----------------- Result -----------------
elif menu == "Result":
    result_page()


# ----------------- Certificate -----------------
elif menu == "Certificate":
    certificate_page()




show_footer()
