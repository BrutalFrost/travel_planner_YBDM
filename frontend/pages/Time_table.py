import os

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

from backend.connect_to_api import ResRobot
from backend.one_hour_ahead import (
    fetch_arrivals_one_hour_ahead,
    fetch_departures_one_hour_ahead,
)
from backend.time_table import (
    calculate_minutes_remaining_arrival,
    calculate_minutes_remaining_depart,
    fetch_timetable_arrival,
    fetch_timetable_departure,
)

# Load API key
load_dotenv()
API_KEY = os.getenv("API_KEY")


# Function to fetch nearby stops based on an area name
def get_location(location):
    url = f"https://api.resrobot.se/v2.1/location.name?input={location}&format=json&accessId={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        result = response.json()
        return [
            loc["StopLocation"]["name"]
            for loc in result.get("stopLocationOrCoordLocation", [])
            if "StopLocation" in loc
        ]
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return []


# UI Layout
st.sidebar.success("Your Timetable")
st.title("🚏 Public Transport Timetable in Minutes")
st.markdown("Get live departure and arrival times for any stop.")

location_name = st.text_input("🔍 Enter Location Name (for live timetable in minutes):")

if location_name:
    stops = get_location(location_name)
    if stops:
        selected_stop = st.selectbox("Select a Stop:", stops)
        timetable = ResRobot()
        ext_id = timetable.get_location_id(selected_stop)

        if ext_id:
            view_option = st.radio("View:", ["Departures", "Arrivals"], horizontal=True)
            fetch_func = (
                fetch_timetable_departure
                if view_option == "Departures"
                else fetch_timetable_arrival
            )
            process_func = (
                calculate_minutes_remaining_depart
                if view_option == "Departures"
                else calculate_minutes_remaining_arrival
            )

            # Fetch and process the main timetable
            df = fetch_func(ext_id)
            df = df if isinstance(df, pd.DataFrame) else pd.DataFrame()
            if not df.empty:
                df = process_func(df).reset_index(drop=True).astype(str)
                st.subheader(f"{view_option} for {selected_stop}")
                st.dataframe(df)
            else:
                st.warning(f"No upcoming {view_option.lower()} for '{selected_stop}'.")

        else:
            st.error(f"Could not find stop ID for '{selected_stop}'.")
    else:
        st.warning("No stops found for this location.")

st.markdown("## ⏳ One Hour Ahead Timetable")
st.markdown("Get live departure and arrival times for any stop.")
location_name_hour_ahead = st.text_input(
    "🔍 Enter Location Name (for one-hour-ahead timetable):"
)


if location_name_hour_ahead:
    stops_hour_ahead = get_location(location_name_hour_ahead)
    if stops_hour_ahead:
        selected_stop_hour_ahead = st.selectbox(
            "Select a Stop for One Hour Ahead:", stops_hour_ahead
        )
        timetable = ResRobot()
        ext_id_hour_ahead = timetable.get_location_id(selected_stop_hour_ahead)

        if ext_id_hour_ahead:
            view_option_hour_ahead = st.radio(
                "View:",
                ["Departures", "Arrivals"],
                horizontal=True,
                key="hour_ahead_radio",
            )
            fetch_func_hour = (
                fetch_departures_one_hour_ahead
                if view_option_hour_ahead == "Departures"
                else fetch_arrivals_one_hour_ahead
            )

            # Fetch and process one-hour-ahead timetable
            df_one_hour = fetch_func_hour(ext_id_hour_ahead)
            df_one_hour = (
                df_one_hour if isinstance(df_one_hour, pd.DataFrame) else pd.DataFrame()
            )
            if not df_one_hour.empty:
                df_one_hour = df_one_hour.reset_index(drop=True).astype(str)
                st.subheader(
                    f"{view_option_hour_ahead} One Hour Ahead for {selected_stop_hour_ahead}"
                )
                st.dataframe(df_one_hour)
            else:
                st.warning(
                    f"No {view_option_hour_ahead.lower()} scheduled one hour ahead for '{selected_stop_hour_ahead}'."
                )
        else:
            st.error(f"Could not find stop ID for '{selected_stop_hour_ahead}'.")
    else:
        st.warning("No stops found for this location.")
