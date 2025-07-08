import streamlit as st
import sqlite3
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from calculateIndeces import calculate_humidex_series
from visTools import create_gauge
from visTools import get_unit_mapping
# ========== LOGIN CHECK - YAHAN ADD KARO ========== #
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
#ALI
st.set_page_config(page_title="IAQ Monitoring", layout="wide")
st.title("IAQ Dashboard")

# Auto-refresh every 5 seconds based on incoming data
st_autorefresh(interval=5000, key="data_refresh")

# Connect to the SQLite database
conn = sqlite3.connect("sensor_data.db", check_same_thread=False)

query = """
    SELECT timestamp, co2, co2_unit, tvoc, tvoc_unit, pm_2_5, pm_2_5_unit, pm_10_0, pm_10_0_unit,
    temperature, temperature_unit, humidity, humidity_unit
    FROM sensor_readings
    ORDER BY timestamp DESC
    LIMIT 100
"""

# Read latest N entries
df = pd.read_sql_query(
    query,
    conn,
    parse_dates=['timestamp']
)

# Only keep relevant pollutants
pollutants = ['co2', 'tvoc', 'pm_2_5', 'pm_10_0']

if not df.empty and 'temperature' in df.columns and 'humidity' in df.columns:
    df["humidex"] = calculate_humidex_series(df["temperature"], df["humidity"])
    pollutants.append("humidex")

# Define final units to display
pollutants_to_display = ['co2', 'tvoc', 'pm_2_5', 'pm_10_0', 'humidex']
available = [p for p in pollutants_to_display if p in df.columns]

comfort_levels = {
    "tvoc": [
        (0, "Most Comfort", "#00FF00"),      
        (0.2, "Irritations and Discomfort", "#FFFF00"),     
        (3, "Headaches possible", "#FFA500"),     
        (25, "Neurotoxic", "#FF4500"),            
    ],
    "co2": [
        (0, "Most Comfort", "#00FF00"),
        (1000, "Concentration problems", "#FFFF00"),
        (2000, "Dangerous", "#FF4500")
    ],
    "pm_2_5": [
        (0, "Most Comfort",  "#00FF00"),
        (10, "Dangerous over a year", "#FFFF00"),
        (25, "Dangerous within a day", "#FF4500"),
    ],
    "pm_10_0": [
        (0, "Most Comfort", "#00FF00"),
        (20, "Dangerous over a year", "#FFFF00"),
        (50, "Dangerous within a day", "#FF4500")
    ],
    "humidex": [
        (0, "Comfort", "#00FF00"),           
        (20, "Little Comfort", "#FFFF00"),   
        (30, "Some Discomfort", "#FFA500"),  
        (40, "Great Discomfort, avoid exertion", "#FF4500"), 
        (45, "Dangerous, heat strokes possible", "#8B0000")         
    ],
}

# Add info text for each pollutant
pollutant_info = {
    "co2": (
        "Mitigation Strategies:"
        "- Improve ventilation especially in crowdy places "
        "- Use photosynthesis of indoor plants"
    ),
    "tvoc": (
        "Mitigation Strategies:"
        "- Use low-emission building materials "
        "- Choose furniture and cleaning products with low VOC-emitting substances "
        "- Ventiltion "
        "- Regular cleaning to remove VOC sources like dust and residues "
        "- Air filtration systems with activated charcoal or other adsorptive filters "
        "- Avoid smoking indoors "
    ),
    "pm_2_5": (
        "Mitigation Strategies:"
        "- Air Purification with HEPA filter "
        "- Avoid using gas stoves, wood-burning fireplaces, smoking and candles indoors, especially if not properly ventilated "
        "- Minimize the use of aerosol sprays "
        "- Improve ventilation "
    ),
    "pm_10_0": (
        "Mitigation Strategies:"
        "- Air Purification with HEPA filter "
        "- Avoid using gas stoves, wood-burning fireplaces, smoking and candles indoors, especially if not properly ventilated "
        "- Minimize the use of aerosol sprays "
        "- Improve ventilation "
    ),
    "humidex": (
        "Mitigation Strategies:"
        "- Stay hydrated "
        "- Light, loose-fitting, and light-colored clothing helps facilitate heat loss "
        "- Use Fans or Air Conditioning "
        "- Prefer shaded areas "
    )
}

def get_comfort_level(pollutant, value):
    thresholds = comfort_levels.get(pollutant.lower())
    if not thresholds or pd.isna(value) or value < 0:
        return "Unknown", "gray"

    for threshold, lvl_label, lvl_color in thresholds:
        if value >= threshold:
            label, color = lvl_label, lvl_color
        else:
            break  # Stop at first threshold greater than value

    return label, color

# Display latest sensor trends if not df.empty:
if not df.empty: 
    cols = st.columns(3)    #display in three columns
    unit_map = get_unit_mapping(df)

    for i, pollutant in enumerate(available):
        latest_value = df[pollutant].iloc[0]  # Most recent value
        label, color = get_comfort_level(pollutant, (latest_value))
        info = pollutant_info.get(pollutant, "")
        max_value = comfort_levels[pollutant][-1][0]  # Last threshold value
        unit = unit_map.get(pollutant, "")  # Get unit from the map
        title = f"{pollutant.upper()} ({unit})" if unit else pollutant.upper()

        with cols[i % 3]:
            st.plotly_chart(
                create_gauge(title, latest_value, label, color, max_value)
                ,use_container_width=True
                )

            # Centered current label with info icon
            st.markdown(
                f"""<div style="text-align:center;">
                        <strong>{label}</strong>
                        <span title="{info}" style="cursor: pointer;">&#8505;</span>
                    </div>""",
                unsafe_allow_html=True
            )

                        # Show all possible labels as a legend, centered
            legend_html = '<div style="text-align:center; margin-top: 0.5em;">'
            for _, lvl_label, lvl_color in comfort_levels[pollutant]:
                legend_html += (
                    f'<span style="display:inline-flex; align-items:center; margin:0 8px;">'
                    f'<span style="display:inline-block; width:16px; height:16px; background:{lvl_color}; border-radius:3px; margin-right:6px; border:1px solid #888;"></span>'
                    f'<span style="color:#111;">{lvl_label}</span>'
                    f'</span>'
                )
            legend_html += '</div>'                    
            st.markdown(legend_html, unsafe_allow_html=True)
            
else:
    st.warning("No data available.")

st.markdown("Threshold sources: ")
st.markdown("- https://www.umweltbundesamt.de/sites/default/files/medien/pdfs/feinstaub_2008.pdf")
st.markdown("- https://www.umweltbundesamt.de/sites/default/files/medien/pdfs/kohlendioxid_2008.pdf")
st.markdown("- https://www.umweltbundesamt.de/sites/default/files/medien/pdfs/TVOC.pdf")
