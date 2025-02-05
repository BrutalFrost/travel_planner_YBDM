import requests

API_KEY = "TRAFFICLABS_API_KEY"

# Replace with actual origin and destination IDs
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
    departure_date = trip["LegList"]["Leg"][0]["Origin"]["date"].replace("-", "")
    departure_time = trip["LegList"]["Leg"][0]["Origin"]["time"].replace(":", "")

    # Generate deep link for the trip ticket
    deep_link = f"https://reseplanerare.resrobot.se/bin/query.exe/en?S={origin_id}&Z={destination_id}&date={departure_date}&time={departure_time}"

    print(f"Trip Link: {deep_link}")
else:
    print("No trips found for the specified route.")
