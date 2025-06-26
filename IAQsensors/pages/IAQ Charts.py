import streamlit as st
import sqlite3
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import plotly.express as px
from kalmanFilter import kalman_filter_self_predicting

st.set_page_config(page_title="IAQ Monitoring", layout="wide")
st.title("IAQ Time Series")

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

# Check which pollutants are available in the DataFrame
available = [p for p in pollutants if p in df.columns]

# Display latest sensor trends if not df.empty:
if not df.empty: 
    cols = st.columns(3)    #display in twhree columns

    #time for x-axis
    df['time'] = df['timestamp'].dt.strftime('%H:%M:%S')  

    # Compute correlation matrix for available pollutants
    corr_matrix = df[available].corr()

    for i, pollutant in enumerate(available):
        with cols[i % 3]:
            st.markdown(f"**{pollutant.upper()}**")

            #Calculate rolling mean (1 minute window)
            rolling_mean = df[pollutant].rolling(30,1).mean().bfill()  #30 samples for 1 minute at s intervals 
            
            array_data = df[pollutant].bfill().to_numpy()
            kfiltered = kalman_filter_self_predicting(array_data)
  
            #combine original and smoothed data
            chart_df = pd.DataFrame({
                "Raw": df[pollutant],
                "Mean Average": rolling_mean,
                "Kalman Filter": kfiltered
            })
            chart_df.index = df['time']  # Add time for x-axis

                        # Show min, max, avg
            min_val = df[pollutant].min()
            max_val = df[pollutant].max()
            avg_val = df[pollutant].mean()
            st.markdown(
                f"<div style='display: flex; gap: 2em;'>"
                f"<span>Min: <b>{min_val:.2f}</b></span>"
                f"<span>Max: <b>{max_val:.2f}</b></span>"
                f"<span>Avg: <b>{avg_val:.2f}</b></span>"
                f"</div>",
                unsafe_allow_html=True
            )

            # Plot the data
            st.line_chart(chart_df, use_container_width=True)

                        # Show top 2 correlated pollutants (excluding self)
            if len(available) > 1:
                corrs = corr_matrix[pollutant].drop(pollutant).abs().sort_values(ascending=False)
                top_corrs = corrs.head(2)
                if not top_corrs.empty:
                    st.markdown("**Top correlated with:**")
                    for corr_pollutant, corr_val in top_corrs.items():
                        st.markdown(f"- {corr_pollutant.upper()} (corr={corr_val:.2f})")


else:
    st.warning("No data available.")
