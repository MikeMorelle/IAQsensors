import streamlit as st
import os

import streamlit as st
import time

# Authentication check
if not st.session_state.get('logged_in', False):
    st.warning("Please login first")
    if st.button("Go to Login Page"):
        st.switch_page("./login.py")  # Goes back to main login page
    st.stop()

# Dashboard content
st.set_page_config(page_title="Dashboard", layout="wide")
st.title(f"Welcome, {st.session_state.username}!")

# Logout button
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.success("Logged out successfully!")
    time.sleep(1)
    st.switch_page("./login.py")

# Your dashboard content here
st.write("This is your main dashboard content")
st.set_page_config(page_title="IAQ Monitoring", layout="wide")
st.title("Error Logging")

LOG_FILE = "error.log"  # Adjust path if needed

def read_log(file_path):
    if not os.path.exists(file_path):
        return "No errors occurred."
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

st.subheader("Latest Errors")
log_content = read_log(LOG_FILE)
st.code(log_content, language="text")

if st.button("Clear Log"):
    if os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()
        st.success("Log cleared.")
    else:
        st.info("No log file to clear.")