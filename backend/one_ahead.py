from datetime import datetime

import pandas as pd
import pytz  # Handle time zones
import requests
import streamlit as st

# from connect_to_api2 import ResRobot
from dotenv import load_dotenv

from backend.connect_to_api import ResRobot

# Load environment variables
load_dotenv()
API_KEY = st.secrets["api"]["API_KEY"]

# Initialize ResRobot
timetable = ResRobot()

# Define location
location_name = "Angered centrum"
ext_id = timetable.get_location_ext_id(location_name)

if ext_id:
    ext_id = ext_id[0]["extId"]
else:
    raise ValueError("No valid extId found.")


# Function to fetch timetable data
def fetch_timetable(ext_id):
    url = f"https://api.resrobot.se/v2.1/departureBoard?id={ext_id}&format=json&accessId={API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "Departure" not in data:
            return pd.DataFrame()

        return pd.DataFrame(data["Departure"])

    except requests.exceptions.RequestException as err:
        print(f"Network or HTTP error: {err}")
        return pd.DataFrame()


# Function to calculate minutes remaining
def calculate_minutes_remaining(df):
    if df.empty:
        return df

    # Ensure time zone consistency
    local_tz = pytz.timezone("Europe/Stockholm")  # Change based on your region
    current_time = datetime.now(local_tz)  # Get current local time

    # Convert departure times to datetime objects
    df["departure_datetime"] = pd.to_datetime(df["date"] + " " + df["time"])
    df["departure_datetime"] = df["departure_datetime"].dt.tz_localize(
        "Europe/Stockholm", ambiguous="NaT", nonexistent="NaT"
    )

    # Calculate minutes remaining
    df["minutes_remaining"] = (
        df["departure_datetime"] - current_time
    ).dt.total_seconds() // 60

    # Fix SettingWithCopyWarning by using .loc[:]
    df.loc[:, "name"] = df["name"].str.replace(r"^Länstrafik - ", "", regex=True)
    df.loc[:, "stop"] = df["stop"].str.replace(r"\s*\(Göteborg kn\)", "", regex=True)
    df.loc[:, "direction"] = df["direction"].str.replace(
        r"\s*\(Göteborg kn\)", "", regex=True
    )

    return df[["name", "stop", "direction", "minutes_remaining"]]


# Function to filter departures AFTER one hour
def filter_after_one_hour(df):
    if df.empty:
        return df

    return df[df["minutes_remaining"] >= 60]  # Include departures exactly at 60 mins


# Fetch timetable data first
df = fetch_timetable(ext_id)

# Process and filter data
df_processed = calculate_minutes_remaining(df)
df_after_one_hour = filter_after_one_hour(df_processed)

# Debug: Show raw minutes_remaining before filtering
print("\nAll Departures (Raw Minutes Remaining):\n")
print(df_processed[["name", "stop", "direction", "minutes_remaining"]])

# Display results in a clean format
if df_after_one_hour.empty:
    print("\n⚠️ No departures found after one hour. Check time zone issues! ⚠️\n")
else:
    print("\n🚍 Departures After One Hour:\n")
    print(
        df_after_one_hour.to_string(index=False)
    )  # Remove default index for a cleaner output
