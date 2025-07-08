import serial
import sqlite3
import time
from datetime import datetime
from findActivePort import find_active_port

# === CONFIGURATION ===
SERIAL_PORT = find_active_port()
if not SERIAL_PORT:
    raise Exception("No active serial port found. Please connect the sensor and try again.")
BAUDRATE = 115200
DB_NAME = 'sensor_data.db' 

# === CONNECT TO DATABASE ===
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    co2 REAL,
    co2_unit TEXT,
    temperature REAL,
    temperature_unit TEXT,
    humidity REAL,
    humidity_unit TEXT,
    eco2 REAL,
    eco2_unit TEXT,
    tvoc REAL,
    tvoc_unit TEXT,
    pm_2_5 REAL,
    pm_2_5_unit TEXT,
    pm_10_0 REAL,
    pm_10_0_unit TEXT,
    pm_0_5 REAL,
    pm_0_5_unit TEXT,
    pm_1_0 REAL,
    pm_1_0_unit TEXT,
    pm_4_0 REAL,
    pm_4_0_unit TEXT,
    pm_1_0_nc REAL,
    pm_1_0_nc_unit TEXT,
    pm_2_5_nc REAL,
    pm_2_5_nc_unit TEXT,
    pm_4_0_nc REAL,
    pm_4_0_nc_unit TEXT,
    pm_10_0_nc REAL,
    pm_10_0_nc_unit TEXT,
    typical_particle_size REAL,
    typical_particle_size_unit TEXT
)
''')
conn.commit()

cursor.execute("SELECT * FROM sensor_readings LIMIT 10")  # Adjust as needed
sensor_data = cursor.fetchall()
# === PARSE SENSOR LOG FUNCTION ===
def parse_sensor_data(lines):
    data = {}
    for line in lines:
        try:
            line = line.strip().strip(',')
            if not line or ":" not in line:
                print(f"Skipping invalid line: {line}")
                continue
            pollutant, value =line.split(":", 1)
            pollutant = pollutant.strip().strip('"')
            value = value.strip().strip('"')
            try:
                data[pollutant] = float(value)
            except ValueError:
                data[pollutant] = value
        except Exception as e:
            print(f"Error parsing line '{line}': {e}")
            continue
    return data

# === SERIAL INITIALIZATION ===
ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
print("Listening on", SERIAL_PORT)

# === MAIN LOOP ===
while True:
    try:
        lines = []
        while True:
            line = ser.readline().decode(errors='ignore').strip()
            print(line)  # Debug print
            if not line:
                break
            lines.append(line)

        sensor_data = parse_sensor_data(lines)

        print("Received data:", sensor_data)

        if sensor_data:
            #add timestamp 
            timestamp = datetime.now().isoformat()

            # prepare data for database insertion
            fields = [
                'co2', 'co2_unit', 'temperature', 'temperature_unit', 'humidity', 'humidity_unit',
                'eco2', 'eco2_unit', 'tvoc', 'tvoc_unit',
                'pm_2_5', 'pm_2_5_unit', 'pm_10_0', 'pm_10_0_unit',
                'pm_0_5', 'pm_0_5_unit', 'pm_1_0', 'pm_1_0_unit', 'pm_4_0', 'pm_4_0_unit',
                'pm_1_0_nc', 'pm_1_0_nc_unit', 'pm_2_5_nc', 'pm_2_5_nc_unit',
                'pm_4_0_nc', 'pm_4_0_nc_unit', 'pm_10_0_nc', 'pm_10_0_nc_unit',
                'typical_particle_size', 'typical_particle_size_unit'
            ]

            # Ensure all fields are present, filling missing ones with None
            for field in fields:
                if field not in sensor_data:
                    sensor_data[field] = None

            values = [sensor_data.get(field) for field in fields]

            #send data to database
            cursor.execute(f'''
                INSERT INTO sensor_readings (
                    timestamp, {", ".join(fields)}
                ) VALUES (
                    ?, {", ".join(["?"] * len(fields))}
                )
            ''', [timestamp] + values)
            conn.commit()
            print(f"[{timestamp}] Data saved.")

        #wait 5s before next reading
        time.sleep(5)

    except Exception as e:
        print("Error in main loop:", e)
        time.sleep(5)
        