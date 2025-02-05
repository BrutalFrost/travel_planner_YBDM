import os

import requests
import streamlit as st
from dotenv import load_dotenv

from backend.bus_tram_on_stop import (
    arrival_time,
    depart_time,
    fetch_timetable_arrival,
    fetch_timetable_departure,
)
from backend.connect_to_api import ResRobot

load_dotenv()
API_KEY = os.getenv("API_KEY")

timetable = ResRobot()


def get_stops(location_name):
    url = f"https://api.resrobot.se/v2.1/location.name?input={location_name}&format=json&accessId={API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        stops = [
            stop["StopLocation"]["name"]
            for stop in data.get("stopLocationOrCoordLocation", [])
            if "StopLocation" in stop
        ]
        return stops

    except requests.exceptions.RequestException as err:
        st.error(f"Error fetching stops: {err}")
        return []


st.title("🚏 Live Public Transport Timetable")

location_name = st.text_input("Enter City or Area Name to Search Stops:")

if location_name:
    stops = get_stops(location_name)

    if stops:
        selected_stop = st.selectbox("Select a Stop:", stops)

        if selected_stop:
            ext_id = timetable.get_location_id(selected_stop)

            if ext_id:
                view_option = st.radio(
                    "View:", ["Departures", "Arrivals"], horizontal=True
                )

                if view_option == "Departures":
                    df = fetch_timetable_departure(ext_id)
                    df = depart_time(df)
                else:
                    df = fetch_timetable_arrival(ext_id)
                    df = arrival_time(df)

                if not df.empty:
                    st.subheader(f"{view_option} for {selected_stop}")
                    st.dataframe(df)
                else:
                    st.warning(
                        f"No upcoming {view_option.lower()} for '{selected_stop}'."
                    )
            else:
                st.error("Could not find stop ID for the selected stop.")

    else:
        st.warning("No stops found for this location. Try a different city or area.")
