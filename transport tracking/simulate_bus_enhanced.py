import requests
import time
import sqlite3
import json
import math

# Flask backend URL
BASE_URL = "http://127.0.0.1:5000"

# Predefined bus routes with realistic coordinates
BUS_ROUTES = {
    1: {
        "name": "City Center Loop",
        "stops": [
            {"name": "Central Station", "lat": 12.9716, "lon": 77.5946},
            {"name": "Mall Road", "lat": 12.9750, "lon": 77.6000},
            {"name": "University", "lat": 12.9800, "lon": 77.6050},
            {"name": "Hospital", "lat": 12.9850, "lon": 77.6100},
            {"name": "Airport Road", "lat": 12.9900, "lon": 77.6150},
            {"name": "Tech Park", "lat": 12.9950, "lon": 77.6200},
            {"name": "Shopping Center", "lat": 13.0000, "lon": 77.6250},
            {"name": "Residential Area", "lat": 13.0050, "lon": 77.6300},
            {"name": "Central Station", "lat": 12.9716, "lon": 77.5946}  # Return to start
        ]
    },
    2: {
        "name": "Airport Express",
        "stops": [
            {"name": "Airport Terminal", "lat": 13.1986, "lon": 77.7063},
            {"name": "Highway Junction", "lat": 13.1500, "lon": 77.7000},
            {"name": "Business District", "lat": 13.1000, "lon": 77.6800},
            {"name": "Central Station", "lat": 12.9716, "lon": 77.5946},
            {"name": "Convention Center", "lat": 12.9500, "lon": 77.5800},
            {"name": "Airport Terminal", "lat": 13.1986, "lon": 77.7063}  # Return to start
        ]
    },
    3: {
        "name": "University Shuttle",
        "stops": [
            {"name": "University Main Gate", "lat": 12.9800, "lon": 77.6050},
            {"name": "Library", "lat": 12.9820, "lon": 77.6070},
            {"name": "Student Center", "lat": 12.9840, "lon": 77.6090},
            {"name": "Sports Complex", "lat": 12.9860, "lon": 77.6110},
            {"name": "Hostel Area", "lat": 12.9880, "lon": 77.6130},
            {"name": "Cafeteria", "lat": 12.9900, "lon": 77.6150},
            {"name": "University Main Gate", "lat": 12.9800, "lon": 77.6050}  # Return to start
        ]
    }
}

class BusTracker:
    def __init__(self, bus_id):
        self.bus_id = bus_id
        self.route = BUS_ROUTES.get(bus_id, BUS_ROUTES[1])  # Default to route 1
        self.current_stop_index = 0
        self.next_stop_index = 1
        self.current_position = self.route["stops"][0].copy()
        self.speed = 0.0001  # Movement speed (degrees per update)
        self.update_interval = 3  # seconds between updates
        
    def move_to_next_stop(self):
        """Move the bus towards the next stop"""
        current_stop = self.route["stops"][self.current_stop_index]
        next_stop = self.route["stops"][self.next_stop_index]
        
        # Calculate direction vector
        lat_diff = next_stop["lat"] - current_stop["lat"]
        lon_diff = next_stop["lon"] - current_stop["lon"]
        
        # Calculate distance
        distance = math.sqrt(lat_diff**2 + lon_diff**2)
        
        if distance < self.speed:
            # Reached the next stop
            self.current_stop_index = self.next_stop_index
            self.next_stop_index = (self.next_stop_index + 1) % len(self.route["stops"])
            self.current_position = next_stop.copy()
            print(f"Bus {self.bus_id} reached {next_stop['name']}")
        else:
            # Move towards next stop
            move_lat = (lat_diff / distance) * self.speed
            move_lon = (lon_diff / distance) * self.speed
            
            self.current_position["lat"] += move_lat
            self.current_position["lon"] += move_lon
    
    def send_location_update(self):
        """Send current location to the server"""
        data = {
            "bus_id": self.bus_id,
            "latitude": self.current_position["lat"],
            "longitude": self.current_position["lon"]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/update_location", json=data)
            stop_name = self.route["stops"][self.current_stop_index]["name"]
            print(f"Bus {self.bus_id} ({self.route['name']}) at {stop_name}: "
                  f"({self.current_position['lat']:.6f}, {self.current_position['lon']:.6f})")
            return True
        except Exception as e:
            print(f"Error sending location for bus {self.bus_id}: {e}")
            return False

def get_or_create_buses():
    """Get buses from database and create default ones if needed"""
    buses = []
    try:
        with sqlite3.connect("transport.db") as conn:
            c = conn.cursor()
            c.execute("SELECT id, bus_number, route FROM buses")
            existing_buses = c.fetchall()
            
            if not existing_buses:
                # Create default buses
                default_buses = [
                    ("BUS-001", "City Center Loop"),
                    ("BUS-002", "Airport Express"),
                    ("BUS-003", "University Shuttle")
                ]
                
                for bus_number, route_name in default_buses:
                    c.execute("INSERT INTO buses (bus_number, route) VALUES (?, ?)", 
                             (bus_number, route_name))
                
                conn.commit()
                print("Created default buses")
                
                # Get the created buses
                c.execute("SELECT id, bus_number, route FROM buses")
                existing_buses = c.fetchall()
            
            buses = existing_buses
            
    except Exception as e:
        print(f"Error accessing database: {e}")
        # Fallback to single bus
        buses = [(1, "BUS-001", "City Center Loop")]
    
    return buses

def main():
    print("Starting Enhanced Bus Location Simulator...")
    print("This simulator creates realistic bus routes without GPS devices")
    
    # Get buses from database
    buses = get_or_create_buses()
    
    if not buses:
        print("No buses found. Exiting.")
        return
    
    # Create bus trackers
    trackers = {}
    for bus_id, bus_number, route_name in buses:
        trackers[bus_id] = BusTracker(bus_id)
        print(f"Created tracker for Bus {bus_id} ({bus_number}) - {route_name}")
    
    print(f"\nTracking {len(trackers)} buses on predefined routes...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            for bus_id, tracker in trackers.items():
                tracker.move_to_next_stop()
                tracker.send_location_update()
            
            time.sleep(3)  # Update every 3 seconds
            
    except KeyboardInterrupt:
        print("\nSimulator stopped by user")
    except Exception as e:
        print(f"Simulator error: {e}")

if __name__ == "__main__":
    main()
