import numpy as np

def calculate_humidex_series(temp, relhum):
    humidex = temp + (5/9) * (6.112 * pow(10, (7.5 * temp) / (237.7 + temp)) * (relhum / 100) - 10)
    humidex = round(humidex, 1)  # Round to one decimal place

    # Define conditions and categories
    conditions = [
        humidex <= 19,
        (humidex > 19) & (humidex <= 29),
        (humidex > 29) & (humidex <= 39),
        (humidex > 39) & (humidex <= 45),
        humidex > 45
    ]
    categories = [
        "Comfort",
        "Little discomfort",
        "Some discomfort",
        "Great discomfort",
        "Dangerous"
    ]
    return np.select(conditions, categories, default="Unknown")