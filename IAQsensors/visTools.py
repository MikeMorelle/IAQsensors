import plotly.graph_objects as go

def create_gauge(title, value, comfort_label, color, max_value):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [0, max_value]},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
        }
    ))
    fig.update_layout(
        width=350, 
        height=300,
    )  
    return fig

def get_unit_mapping(df):
    # Create a mapping from pollutant to its unit
    unit_map = {}
    unit_suffixes = {
        "co2": "co2_unit",
        "tvoc": "tvoc_unit",
        "pm_2_5": "pm_2_5_unit",
        "pm_10_0": "pm_10_0_unit",
        "temperature": "temperature_unit",
        "humidity": "humidity_unit",
    }

    if not df.empty:
        latest_row = df.iloc[0]
        for pollutant, unit_col in unit_suffixes.items():
            if unit_col in df.columns:
                unit_map[pollutant] = latest_row[unit_col]
            else:
                unit_map[pollutant] = ""
    return unit_map