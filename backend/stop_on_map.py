import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")


def get_location_id(location):
    url = f"https://api.resrobot.se/v2.1/location.name?input={location}&format=json&accessId={API_KEY}"
    result = requests.get(url).json()
    int_res = result.get("stopLocationOrCoordLocation")
    if int_res:
        return int(int_res[0]["StopLocation"]["extId"])
    return None  


def get_trip_stops(origin, destination):  
    origin_id = get_location_id(origin)  
    destination_id = get_location_id(destination)  

    if origin_id is None or destination_id is None:  
        print("Invalid origin or destination")  
        return []  

    url = f"https://api.resrobot.se/v2.1/trip?format=json&originId={origin_id}&destId={destination_id}&passlist=true&showPassingPoints=true&accessId={API_KEY}"  

    try:  
        response = requests.get(url)  
        response.raise_for_status()  
        data = response.json()  

        stops = []  
        for trip in data.get("Trip", []):  
            for leg in trip.get("LegList", {}).get("Leg", []):  
                if isinstance(leg, dict) and "Origin" in leg and "Destination" in leg:  
                    if not stops:  
                        stops.append(leg["Origin"]["name"])  
                    
                    for stop in leg.get("Stops", {}).get("Stop", []):  
                        stops.append(stop["name"])  

                    stops.append(leg["Destination"]["name"])  

            break  

        stops = list(dict.fromkeys(stops))  

        return stops  

    except requests.exceptions.RequestException as err:  
        print(f"Network or HTTP error: {err}")  
        return []  
stops = get_trip_stops("Göteborg Centalstation", "Stockholm Centralstation")  
print(stops)
