import streamlit as st
import pandas as pd
from backend.connect_to_api import ResRobot
from backend.time_table import (
    fetch_timetable_departure,
    fetch_timetable_arrival,
    calculate_minutes_remaining_depart,
    calculate_minutes_remaining_arrival,
)
from backend.one_hour_ahead import fetch_departures_one_hour_ahead, fetch_arrivals_one_hour_ahead

# Streamlit App
st.sidebar.success("Your Timetable")
st.title("📅 Public Transport Timetable")
st.markdown("Get live departure and arrival information for any stop.")

# Input for location
location_name = st.text_input("🔍 Enter Stop Name:", "")

if location_name:
    timetable = ResRobot()
    ext_id = timetable.get_location_id(location_name)

    if ext_id:
        # Toggle Button to switch between Departures & Arrivals
        view_option = st.radio("Select Timetable View:", ["Departures", "Arrivals"], horizontal=True)

        if view_option == "Departures":
            st.subheader(f"🛫 Departures from {location_name}")
            df_depart = fetch_timetable_departure(ext_id)
            df_processed_depart = calculate_minutes_remaining_depart(df_depart)

            if not df_processed_depart.empty:
                st.dataframe(df_processed_depart)
            else:
                st.warning(f"No upcoming departures for '{location_name}'.")

        else:  # Arrival View
            st.subheader(f"🛬 Arrivals at {location_name}")
            df_arrival = fetch_timetable_arrival(ext_id)
            df_processed_arrival = calculate_minutes_remaining_arrival(df_arrival)

            if not df_processed_arrival.empty:
                st.dataframe(df_processed_arrival)
            else:
                st.warning(f"No upcoming arrivals for '{location_name}'.")

    else:
        st.error(f"Could not find stop ID for '{location_name}'. Please check the name.")
else:
    st.info("Please enter a stop name to fetch the timetable.")

# One Hour Ahead Section
st.markdown("## ⏳ One Hour Ahead Timetable")
location_name_one_hour = st.text_input("🔍 Enter Stop Name for One-Hour-Ahead Timetable:", "")

if location_name_one_hour:
    timetable = ResRobot()
    ext_id_one_hour = timetable.get_location_id(location_name_one_hour)

    if ext_id_one_hour:
        view_option_one_hour = st.radio("Select One-Hour-Ahead View:", ["Departures", "Arrivals"], horizontal=True)

        if view_option_one_hour == "Departures":
            st.subheader(f"🚋 Departures in One Hour from {location_name_one_hour}")
            df_one_hour_departures = fetch_departures_one_hour_ahead(ext_id_one_hour)

            if not df_one_hour_departures.empty:
                st.dataframe(df_one_hour_departures)
            else:
                st.warning(f"No departures scheduled one hour ahead for '{location_name_one_hour}'.")

        else:  # Arrival View
            st.subheader(f"🚋 Arrivals in One Hour at {location_name_one_hour}")
            df_one_hour_arrivals = fetch_arrivals_one_hour_ahead(ext_id_one_hour)

            if not df_one_hour_arrivals.empty:
                st.dataframe(df_one_hour_arrivals)
            else:
                st.warning(f"No arrivals scheduled one hour ahead for '{location_name_one_hour}'.")

    else:
        st.error(f"Could not find stop ID for '{location_name_one_hour}'. Please check the name.")
else:
    st.info("Please enter a stop name to fetch the one-hour-ahead timetable.")
