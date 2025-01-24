import os
import requests
import pandas as pd
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")

# Function to fetch extId from location
def get_location_ext_id(location):
    url = f"https://api.resrobot.se/v2.1/location.name?input={location}&format=json&accessId={API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad HTTP responses
        result = response.json()

        ext_ids = []
        for stop in result.get("stopLocationOrCoordLocation", []):
            stop_data = next(iter(stop.values()))
            if stop_data.get("extId"):
                ext_ids.append({"name": stop_data["name"], "extId": stop_data["extId"]})

        return ext_ids
    except requests.exceptions.RequestException as err:
        st.error(f"Network or HTTP error: {err}")
        return []

# Function to fetch timetable data
def fetch_timetable(ext_id):
    url = f"https://api.resrobot.se/v2.1/departureBoard?id={ext_id}&format=json&accessId={API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "Departure" not in data:
            st.error("No departure data available for this station.")
            return pd.DataFrame()

        # Convert departure data to DataFrame
        df = pd.DataFrame(data["Departure"])
        return df
    except requests.exceptions.RequestException as err:
        st.error(f"Network or HTTP error: {err}")
        return pd.DataFrame()

# Function to calculate minutes remaining for departures
def calculate_minutes_remaining(df):
    if df.empty:
        return df

    current_time = datetime.now()
    df['departure_datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
    df['minutes_remaining'] = (df['departure_datetime'] - current_time).dt.total_seconds() // 60
    
    # Make it User friendly the interface
    df['name'] = df['name'].str.replace(r'^Länstrafik - ', '', regex=True)
    df['stop'] = df['stop'].str.replace(r'\s*\(Göteborg kn\)', '', regex=True)
    df['direction'] = df['direction'].str.replace(r'\s*\(Göteborg kn\)', '', regex=True)
    
    return df[['name', 'stop', 'direction', 'minutes_remaining']]


