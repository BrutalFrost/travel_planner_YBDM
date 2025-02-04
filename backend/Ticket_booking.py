from datetime import datetime

import requests

# fixing ci stuff
API_KEY = "TRAFFICLABS_API_KEY"

# replace with your origin and destination IDs
origin_id = "ORIGIN_ID"
destination_id = "DESTINATION_ID"


url = "https://api.resrobot.se/v2.1/trip"


params = {
    "originId": origin_id,
    "destId": destination_id,
    "format": "json",
    "accessId": API_KEY,
}

response = requests.get(url, params=params)
data = response.json()

# Check if trips are available
if "Trip" in data:
    trip = data["Trip"][0]
    departure_time = (
        trip["LegList"]["Leg"][0]["Origin"]["date"]
        + " "
        + trip["LegList"]["Leg"][0]["Origin"]["time"]
    )
    arrival_time = (
        trip["LegList"]["Leg"][-1]["Destination"]["date"]
        + " "
        + trip["LegList"]["Leg"][-1]["Destination"]["time"]
    )
    departure_dt = datetime.strptime(departure_time, "%Y-%m-%d %H:%M:%S")
    arrival_dt = datetime.strptime(arrival_time, "%Y-%m-%d %H:%M:%S")
    duration = arrival_dt - departure_dt
    print(f"Trip duration: {duration}")
else:
    print("No trips found for the specified route.")
