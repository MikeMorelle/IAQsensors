from serial.tools import list_ports
import serial
import time

def find_active_port():
    expected_keywords = ["co2", "temperature", "humidity", "tvoc", "pm"]  # Expected keys in sensor data
    ports = list_ports.comports()

    for port in ports:
        try: 
            print(f"Trying port: {port.device}")
            with serial.Serial(port.device, baudrate=115200, timeout=1) as ser:
                time.sleep(2)  # Wait for the port to initialize
                for _ in range(10): #read attempts to go through multiple lines 
                    line = ser.readline().decode(errors='ignore').strip()
                    if not line:
                        continue
                    if any(keyword in line for keyword in expected_keywords):
                        print(f"Active port found: {port.device}")
                        return port.device
        except Exception as e:
            print(f"Failed to read from port {port.device}: {e}")
            continue
    return None  
