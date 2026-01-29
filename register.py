import streamlit as st
import mysql.connector

# --- DB CONNECTION ---
def get_db_connection():
    return mysql.connector.connect(
        host="localhost", user="root", password="root", database="ai_grader"
    )

if 'view' not in st.session_state:
    st.session_state.view = 'register'

# --- REGISTRATION VIEW ---
if st.session_state.view == 'register':
    st.title("📝 AI Grader Registration")
    with st.form("reg_form"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name")
            u_id = st.text_input("Identification ID")
        with col2:
            uname = st.text_input("Username")
            pwd = st.text_input("Password", type="password")
        
        role = st.selectbox("Role", ["Teacher", "Student"])
        if st.form_submit_button("Create Account"):
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (uname, pwd, role))
                if role == "Teacher":
                    cursor.execute("INSERT INTO teachers (teacher_id, name, username) VALUES (%s, %s, %s)", (u_id, full_name, uname))
                else:
                    cursor.execute("INSERT INTO students (student_id, name, username) VALUES (%s, %s, %s)", (u_id, full_name, uname))
                conn.commit()
                st.success("Registration Successful!")
                conn.close()
            except Exception as e:
                st.error(f"Error: {e}")

    if st.button("Already have an account? Login here"):
        st.session_state.view = 'login'
        st.rerun()

# --- LOGIN VIEW ---
elif st.session_state.view == 'login':
    st.title("🔐 Login to Portal")
    with st.form("login_form"):
        l_user = st.text_input("Username")
        l_pass = st.text_input("Password", type="password")
        l_role = st.selectbox("Select Role", ["Teacher", "Student"])
        if st.form_submit_button("Submit"):
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s AND role=%s", (l_user, l_pass, l_role))
            user = cursor.fetchone()
            conn.close()

            if user and user['role'] == 'Teacher':
                st.session_state.view = 'grader_app'
                st.rerun()
            elif user:
                st.info("Student portal access restricted.")
            else:
                st.error("Invalid credentials.")

    if st.button("Back to Registration"):
        st.session_state.view = 'register'
        st.rerun()

# --- CALLING THE GRADER ---
elif st.session_state.view == 'grader_app':
    from app import main_grader_app
    main_grader_app()