#import os
from datetime import datetime

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_KEY_RESROBOT = os.getenv("API_KEY")
if not API_KEY_RESROBOT:
    st.error("API key not found. Please set the API_KEY environment variable.")

from backend.connect_to_api import ResRobot

resa = ResRobot()
# API_KEY = os.getenv("TRAFFICLABS_API_KEY")

API_KEY = resa.API_KEY
if not API_KEY:
    st.error(
        "API key not found. Please set the TRAFFICLABS_API_KEY environment variable."
    )
    st.stop()

TRIP_URL = "https://api.resrobot.se/v2.1/trip"
STATION_URL = "https://api.resrobot.se/v2.1/location.name"

st.title("🚆 Train Ticket Planner")
st.write(
    "Enter your starting location and destination to find available train tickets."
)

origin_name = st.text_input("Enter Origin Station Name", "Stockholm")
destination_name = st.text_input("Enter Destination Station Name", "Göteborg")


def lookup_station_id(station_name):
    """Lookup station ID using the ResRobot location API."""
    params = {"input": station_name, "format": "json", "accessId": API_KEY_RESROBOT}
    response = requests.get(STATION_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if "stopLocationOrCoordLocation" in data:
            stop_location = data["stopLocationOrCoordLocation"][0]["StopLocation"]
            station_id = stop_location["extId"]
            return station_id
        else:
            st.write(f"No station ID found for {station_name}.")
            return None
    else:
        st.write("Error:", response.status_code, response.text)
        return None


def fetch_train_tickets(origin_id, destination_id):
    """Fetch train trip details and available tickets."""
    params = {
        "originId": origin_id,
        "destId": destination_id,
        "format": "json",
        "accessId": API_KEY_RESROBOT,
        "transportMode": "train",
    }

    response = requests.get(TRIP_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if "Trip" in data:
            trips = data["Trip"]
            trip_options = []

            for idx, trip in enumerate(trips):
                departure = (
                    trip["LegList"]["Leg"][0]["Origin"]["date"]
                    + " "
                    + trip["LegList"]["Leg"][0]["Origin"]["time"]
                )
                arrival = (
                    trip["LegList"]["Leg"][-1]["Destination"]["date"]
                    + " "
                    + trip["LegList"]["Leg"][-1]["Destination"]["time"]
                )

                # Calculate duration
                departure_dt = datetime.strptime(departure, "%Y-%m-%d %H:%M:%S")
                arrival_dt = datetime.strptime(arrival, "%Y-%m-%d %H:%M:%S")
                duration = arrival_dt - departure_dt
                duration_str = f"{duration.seconds // 3600} hours {((duration.seconds // 60) % 60)} minutes"

                st.write(f"**Departure:** {departure}")
                st.write(f"**Arrival:** {arrival}")
                st.write(f"**Duration:** {duration_str}")
                st.write(f"**Origin:** {trip['LegList']['Leg'][0]['Origin']['name']}")
                st.write(
                    f"**Destination:** {trip['LegList']['Leg'][-1]['Destination']['name']}"
                )
                st.write("**Available Tickets:**")

                for ticket in trip.get("TariffResultList", []):
                    ticket_type = ticket.get("tariffName", "N/A")
                    price = ticket.get("price", "N/A")
                    provider_name = ticket.get("providerName", "N/A")
                    booking_url = f"https://www.resrobot.se/journey/search?from={origin_name}&to={destination_name}&date={departure.split(' ')[0]}&time={departure.split(' ')[1]}"
                    ticket_info = (
                        f"{ticket_type}: SEK {price} (Provider: {provider_name})"
                    )
                    trip_options.append(
                        {
                            "departure": departure,
                            "arrival": arrival,
                            "duration": duration_str,
                            "ticket_info": ticket_info,
                            "booking_url": booking_url,
                        }
                    )
                    st.markdown(
                        f" - {ticket_info} [**Book Here**]({booking_url})",
                        unsafe_allow_html=True,
                    )

            if trip_options:
                selected_option = st.selectbox(
                    "Select a ticket to book:",
                    options=[
                        f"{opt['departure']} - {opt['arrival']} ({opt['ticket_info']})"
                        for opt in trip_options
                    ],
                )

                selected_ticket = trip_options[
                    [
                        f"{opt['departure']} - {opt['arrival']} ({opt['ticket_info']})"
                        for opt in trip_options
                    ].index(selected_option)
                ]

                if st.button("Book Ticket"):
                    st.write(
                        f"You're about to book a ticket for the trip from **{selected_ticket['departure']}** to **{selected_ticket['arrival']}**."
                    )
                    st.write(f"Ticket Info: **{selected_ticket['ticket_info']}**")
                    st.write("Click below to complete the booking.")
                    st.markdown(
                        f"[**Book Now**]({selected_ticket['booking_url']})",
                        unsafe_allow_html=True,
                    )

        else:
            st.write("No train trips found for the specified route.")
    else:
        st.write("Error:", response.status_code, response.text)


if st.button("Find Train Tickets"):
    if not origin_name or not destination_name:
        st.error("Please enter both origin and destination station names.")
    else:
        origin_id = lookup_station_id(origin_name)
        destination_id = lookup_station_id(destination_name)
        if origin_id and destination_id:
            fetch_train_tickets(origin_id, destination_id)
        else:
            st.error("Invalid station names. Please check your input.")
