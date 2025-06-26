import streamlit as st
import os

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