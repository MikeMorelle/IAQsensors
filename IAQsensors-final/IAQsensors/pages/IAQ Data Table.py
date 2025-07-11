import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import sqlite3

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

st.title("IAQ Data Table")

# Auto-refresh every 5 seconds based on incoming data
st_autorefresh(interval=5000, key="data_refresh")

# Connect to the SQLite database
conn = sqlite3.connect("sensor_data.db", check_same_thread=False)

# Read latest N entries
df = pd.read_sql_query(
    "SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 100",
    conn,
    parse_dates=['timestamp']
)

df_display = df.drop(columns=['id'], errors='ignore')  # safely drop 'id' if exists
st.dataframe(df_display, use_container_width=True, hide_index=True)