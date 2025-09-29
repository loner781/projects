import requests
import time
import random
import sqlite3

# Flask backend URL
BASE_URL = "http://127.0.0.1:5000"

def get_or_create_bus():
    """Get the first bus from database or create one if none exists"""
    try:
        with sqlite3.connect("transport.db") as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM buses LIMIT 1")
            bus = c.fetchone()
            if bus:
                return bus[0]
            else:
                # Create a default bus
                c.execute("INSERT INTO buses (bus_number, route) VALUES (?, ?)", ("BUS-001", "City Center Loop"))
                conn.commit()
                return c.lastrowid
    except Exception as e:
        print(f"Error accessing database: {e}")
        return 1  # Fallback to bus ID 1

# Get bus ID
BUS_ID = get_or_create_bus()
print(f"Using Bus ID: {BUS_ID}")

# Starting location (Example: Bangalore coordinates)
lat, lon = 12.9716, 77.5946

print("Starting bus location simulator...")
print("Press Ctrl+C to stop")

try:
    while True:
        # Randomly move the bus a little bit
        lat += random.uniform(-0.001, 0.001)
        lon += random.uniform(-0.001, 0.001)

        data = {
            "bus_id": BUS_ID,
            "latitude": lat,
            "longitude": lon
        }

        try:
            res = requests.post(f"{BASE_URL}/api/update_location", json=data)
            print(f"Sent: Bus {BUS_ID} at ({lat:.6f}, {lon:.6f}) - Response: {res.json()}")
        except Exception as e:
            print(f"Error sending location: {e}")

        time.sleep(5)  # send update every 5 seconds

except KeyboardInterrupt:
    print("\nSimulator stopped by user")
except Exception as e:
    print(f"Simulator error: {e}")
