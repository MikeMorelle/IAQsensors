import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import sqlite3

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