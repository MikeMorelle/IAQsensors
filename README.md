# IAQsensors

1. sensorDataCollector receives sensor data on serial port/USB -> connects to sqlite db -> parses data in table format to local sensor_data.db

2. dataVis connects to sensor_data.db -> reads data, adds timestamps and shows in graphs -> compares to thresholds and gives warning
2.1. calculateIndeces calculates Humidex (temperature ~ humidity)

How to use:
- comment db connection out and use fictional data or data from serial_log.txt
- in terminal: streamlit run dataVis.py


TODO: 
- serial port check (Michael)
- improve GUI (dark mode, structure, pollutant selects,...)
- Microcontoller LED alarms (Michael)
- db clean after certain amount of time to prevent memory overflow
- correct kalman filter (Michael)
- outlier handling and logging
- system health logs
- IAQ index
- show min/max/avg of each pollutant
- correlation graphs between pollutants
- compare with FMEA requirements and add error handlings
