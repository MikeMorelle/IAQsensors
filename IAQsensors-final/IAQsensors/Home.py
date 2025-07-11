import streamlit as st
import streamlit as st



#ALI
st.set_page_config(page_title="IAQ Monitoring", layout="wide")
st.title("Real-Time Indoor Air Quality Monitoring")

st.subheader("Scope")
st.markdown(
    "The quality of the air we breathe has a profound impact on human health, perceived wellbeing and performance. "
    "Especially regarding that people spend on an average **90%** of their time indoors [1], a growing body of research considers using smart sensor system to highlight increasing levels of indoor pollutants - such as VOCs, particulate matter or CO2 - and environmental factors - such as temperature and humidity. "
    "Originating from outdoor infiltration, as well as indoor sources like building materials or human activities, the need for real-time monitoring and practical indoor air quality (IAQ) management insights is urgent. "
    "This tool serves those purposes on a modular, low-cost and easy-to-implement basis, therefore being capable for a wide range of use cases like:"
)

st.markdown("""
- Schools and universities
- Offices and workplaces
- Residential buildings
""")

st.subheader("Data")
st.markdown("**TVOC** [2]")
st.markdown("Total Volatile Organic Compounds is a collective measure of the concentration of various volatile organic compounds present in indoor air. These compounds are organic chemicals that easily vaporize at room temperature and originate from sources like building materials, cleaning products, paints, furnishings, and human activities.")
st.markdown("Dangers incl. sensory irritations, headaches, dizziness, fatigue, respiratory issues, chemical reactions to form secondary pollutants like formaldehyde or ozone")

st.markdown("**eCO2**: Assuming that every person emits a certain amount of VOCs over time, a CO2 concentration can be estimated. As this is a calculated CO2 concentration, it is referred to as an equivalent concentration (eCO2 = equivalent CO2)")

st.markdown("**PM** [3]")
st.markdown("Particulate Matter (PM) refers to tiny solid and liquid particles suspended in the air, originating from sources like dust, soot, smoke, construction activities, fires, and chemical reactions from pollutants such as sulfur dioxide and nitrogen oxides. PM is categorized by size: PM10 (particles 10 micrometers or smaller) and PM2.5 (particles 2.5 micrometers or smaller).")
st.markdown("Dangers incl. premature death in people with heart or lung disease, nonfatal heart attacks, irregular heartbeat, aggravated asthma, decreased lung function, increased respiratory symptoms (such as irritation of the airways, coughing or difficulty breathing)")

st.markdown("**CO2** [4]")
st.markdown("Carbon dioxide (CO₂) is a colorless and odorless gas that occurs naturally in the air and is produced during cellular respiration and combustion processes.")
st.markdown("Dangers incl. discomfort, concentration problems, headaches, fatigue, respiratory issues")

st.markdown("**Humidex** [5]")
st.markdown("The Humidex originated in 1979 by R.G. Steadman [6]. It is a weather index that combines air temperature and humidity to estimate how hot the weather feels to the human body. It provides a measure of perceived heat by accounting for the cooling effect of humidity on the body's ability to sweat and evaporate heat, effectively indicating how uncomfortable or dangerous hot and humid conditions may feel.")
st.markdown("Dangers incl. the increase risk of heat exhaustion, heat stroke, and dehydration because high humidity hampers the body's ability to cool itself through sweating")

st.subheader("Limitations")
st.markdown("- Measuring Errors: Systematic (consistent e.g. sensor miscalibration or environmental influences), Random (unpredictable e.g. electrical noise), Human (e.g. wiring mistakes, heavy use of perfumes)")
st.markdown("- Low-cost sensor inaccuracies and drift")
st.markdown("- TVOC heavily affected by some VOC compound flucuations")
st.markdown("- Sensors not meant for security or high-integrity use cases")

st.subheader("Sources")
st.markdown("[1] https://www.epa.gov/indoor-air-quality-iaq/improving-your-indoor-environment")
st.markdown("[2] https://www.umweltbundesamt.de/sites/default/files/medien/pdfs/TVOC.pdf")
st.markdown("[3] https://www.epa.gov/pm-pollution/particulate-matter-pm-basics")
st.markdown("[4] https://www.umweltbundesamt.de/sites/default/files/medien/pdfs/kohlendioxid_2008.pdf")
st.markdown("[5] https://www.ccohs.ca/oshanswers/phys_agents/humidex.html")
st.markdown("[6] Steadman, R. G. (1979). The assessment of sultriness. Part I: A temperature-humidity index based on human physiology and clothing science. Journal of Applied Meteorology and Climatology, 18(7), 861-873.")
