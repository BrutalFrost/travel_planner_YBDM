
import requests
import os
from dotenv import load_dotenv
from backend.connect_to_api import ResRobot
from frontend.plot_maps import TripMap

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")

stop_map = ResRobot()

def get_trip_stops(origin_id, destination_id):
    """Fetches all stop names between origin and destination, including departure and final stop."""
    origin_id = stop_map.get_location_id(origin_id)
    destination_id = stop_map.get_location_id(destination_id)

    if origin_id is None or destination_id is None:
        print("Invalid origin or destination")
        return []

    url = f"https://api.resrobot.se/v2.1/trip?format=json&originId={origin_id}&destId={destination_id}&passlist=true&showPassingPoints=true&accessId={API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        stops = []
        for trip in data.get('Trip', []):  # Loop through possible trips
            for leg in trip.get('LegList', {}).get('Leg', []):  # Loop through legs of the trip
                if isinstance(leg, dict) and 'Origin' in leg and 'Destination' in leg:
                    stops.append(leg['Origin']['name'])  # Add departure stop
                    for stop in leg.get('Stops', {}).get('Stop', []):  # Add intermediate stops
                        stops.append(stop['name'])
                    stops.append(leg['Destination']['name'])  # Add final stop

        stops = list(dict.fromkeys(stops))  # Remove duplicates while maintaining order
        
        # Now display the map with these stops using TripMap
        trip_map = TripMap(origin_id, destination_id)
        trip_map.display_map()  # Call the method to display the map
        
        return stops

    except requests.exceptions.RequestException as err:
        print(f"Network or HTTP error: {err}")
        return []

# Example usage:
stops = get_trip_stops("Göteborg Centralstation", "Stockholm Centralstation")
print(stops)
