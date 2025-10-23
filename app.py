
# app.py
import streamlit as st
from datetime import datetime
from utils.chatbot_utils import chatbot_page
from utils.rag_utils import rag_reader_page
from utils.db import init_db, add_user, check_password, get_user, update_password

# Optional: JWT Token Support
import jwt
import datetime as dt

SECRET_KEY = "CHANGE_THIS_TO_A_STRONG_KEY"  # Move this to st.secrets or environment variables in production
SESSION_TIMEOUT_MINUTES = 30  # session validity time

# -------------------------
# JWT Token Functions
# -------------------------
def create_token(username):
    payload = {
        "username": username,
        "exp": dt.datetime.utcnow() + dt.timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["username"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# -------------------------
# Session Timeout Check
# -------------------------
def check_session_timeout():
    if st.session_state.get("logged_in"):
        login_time = st.session_state.get("login_time", 0)
        now = datetime.now().timestamp()
        if now - login_time > SESSION_TIMEOUT_MINUTES * 60:
            logout_user("⏳ Session expired. Please log in again.")

def logout_user(message="Logged out successfully."):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.warning(message)
    st.rerun()

# -------------------------
# Initialize App
# -------------------------
st.set_page_config(page_title="Smart AI Assistant", layout="wide")
init_db()  # Initialize SQLite database

# Run timeout check at the top
check_session_timeout()

# -------------------------
# Streamlit Session Variables
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# -------------------------
# Sidebar Menu
# -------------------------
menu = ["Login", "Sign Up", "Forgot Password"] if not st.session_state.logged_in else ["Home", "Logout"]
choice = st.sidebar.selectbox("Navigation", menu)

# -------------------------
# LOGIN PAGE
# -------------------------
if choice == "Login":
    st.header("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_password(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.login_time = datetime.now().timestamp()
            st.session_state.token = create_token(username)  # create secure token
            st.success("✅ Login successful.")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

# -------------------------
# SIGN UP PAGE
# -------------------------
elif choice == "Sign Up":
    st.header("📝 Sign Up")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")
    question = st.text_input("Secret Question")
    answer = st.text_input("Secret Answer")
    if st.button("Register"):
        if password == confirm:
            try:
                add_user(username, password, question, answer)
                st.success("✅ Signup successful! You can now log in.")
            except Exception as e:
                st.error(f"❌ Username already exists or error: {e}")
        else:
            st.error("⚠️ Passwords do not match!")

# -------------------------
# FORGOT PASSWORD
# -------------------------
elif choice == "Forgot Password":
    st.header("🔑 Forgot Password")
    username = st.text_input("Username")
    user = get_user(username)
    if user:
        st.info(f"Security Question: {user['secret_question']}")
        ans = st.text_input("Answer")
        new_pass = st.text_input("New Password", type="password")
        if st.button("Reset"):
            if ans.strip().lower() == user['secret_answer'].lower():
                update_password(username, new_pass)
                st.success("✅ Password reset successful.")
            else:
                st.error("❌ Incorrect answer.")
    elif username:
        st.error("❌ User not found.")

# -------------------------
# LOGOUT
# -------------------------
elif choice == "Logout":
    logout_user("👋 You have been logged out successfully.")

# -------------------------
# HOME PAGE (AFTER LOGIN)
# -------------------------
elif st.session_state.logged_in and choice == "Home":
    # Token validation before granting access
    token_user = verify_token(st.session_state.get("token"))
    if not token_user:
        logout_user("⏳ Session expired. Please log in again.")
    else:
        st.title(f"🏠 Welcome, {st.session_state.username}")
        st.write("Choose an application to continue:")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💬 Chatbot"):
                st.session_state.page = "chatbot"
                st.rerun()
        with col2:
            if st.button("📚 RAG PDF Reader"):
                st.session_state.page = "rag"
                st.rerun()

# -------------------------
# PROTECTED PAGES
# -------------------------
if st.session_state.get("page") == "chatbot":
    token_user = verify_token(st.session_state.get("token"))
    if not token_user:
        logout_user("⏳ Session expired. Please log in again.")
    else:
        chatbot_page(st.session_state.username)

elif st.session_state.get("page") == "rag":
    token_user = verify_token(st.session_state.get("token"))
    if not token_user:
        logout_user("⏳ Session expired. Please log in again.")
    else:
        rag_reader_page()


