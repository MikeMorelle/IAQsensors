import streamlit as st
import sqlite3
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from calculateIndeces import calculate_humidex_series
from kalmanFilter import kalman_filter
import plotly.express as px


st.set_page_config(page_title="Live Sensor Dashboard", layout="wide")
st.title("Live Sensor Data Dashboard")

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

if not df.empty:
    df['timestamp'] = pd.to_datetime(df['timestamp']) #ensure timestamp is in datetime format
    df.set_index('timestamp')
    df = df.sort_values('timestamp')    # for left-to-right plots
    
else:
    print("No data available in the database.")


# Expected pollutant list
pollutants = [
    'co2', 'temperature', 'humidity', 'tvoc', 'eco2',
    'pm_0_5', 'pm_1_0', 'pm_2_5', 'pm_4_0', 'pm_10_0',
    'pm_1_0_nc', 'pm_2_5_nc', 'pm_4_0_nc', 'pm_10_0_nc',
    'typical_particle_size'
]

# Define thresholds for pollutants (add or adjust as needed)
thresholds = {
    'co2': 1000,    # ppm
    'tvoc': 56,     # ppb
    'eco2': 1000,   # ppm
    'pm_2_5': 25,   # µg/m³
    'pm_10_0': 50,  # µg/m³
}

# Check which pollutants are available in the DataFrame
available = [p for p in pollutants if p in df.columns]

# Display latest sensor trends if not df.empty:
if not df.empty: 
    st.subheader("Time Series for Pollutants")
    cols = st.columns(3)    #display in twhree columns

    #time for x-axis
    df['time'] = df['timestamp'].dt.strftime('%H:%M:%S')  

    for i, pollutant in enumerate(available):
        with cols[i % 3]:
            st.markdown(f"**{pollutant.upper()} (with 1-min moving average)**")

            #Calculate rolling mean (1 minute window)
            rolling_mean = df[pollutant].rolling(30,1).mean()   #30 samples for 1 minute at s intervals 

            if pollutant in thresholds and rolling_mean.iloc[-1] > thresholds.get(pollutant):
                st.warning(f"⚠️ {pollutant.upper()} exceeds threshold: {thresholds.get(pollutant)}")
                
            #combine original and smoothed data
            chart_df = pd.DataFrame({
                "Raw": df[pollutant],
                "Mean Average": rolling_mean,
            })
            chart_df.index = df['time']  # Add time for x-axis

            # Plot the data
            st.line_chart(chart_df, use_container_width=True)

    #Display Humidex Comfort Category
    df["humidex_category"] = calculate_humidex_series(df["temperature"], df["humidity"])  
    humidex_cat_df = pd.DataFrame({
        "time": df["time"],
        "Humidex Category": df["humidex_category"]
    })

    fig = px.line(
        humidex_cat_df,
        x="time",
        y="Humidex Category",
        color="Humidex Category",
        title="Humidex Comfort Category Over Time"
    )
    st.plotly_chart(fig, use_container_width=True)


else:
    st.warning("No data available.")

#