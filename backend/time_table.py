import os
from datetime import datetime

import pandas as pd
import requests

# import streamlit as st
from dotenv import load_dotenv

from backend.connect_to_api import ResRobot

# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")

# Initialize ResRobot
timetable = ResRobot()

# Define location
location_name = "Angered Centrum"
ext_id = timetable.get_location_id(location_name)

if isinstance(ext_id, int):
    ext_id = str(ext_id)
else:
    raise ValueError(
        f"No valid extId found for '{location_name}'. Check the stop name and try again."
    )


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

    current_time = datetime.now()
    df["departure_datetime"] = pd.to_datetime(df["date"] + " " + df["time"])
    df["minutes_remaining"] = (
        df["departure_datetime"] - current_time
    ).dt.total_seconds() // 60

    df = df[df["minutes_remaining"] >= 0]

    # Clean up column values for better readability
    df.loc[:, "name"] = df["name"].str.replace(r"^Länstrafik - ", "", regex=True)
    df.loc[:, "stop"] = df["stop"].str.replace(r"\s*\(Göteborg kn\)", "", regex=True)
    df.loc[:, "direction"] = df["direction"].str.replace(
        r"\s*\(Göteborg kn\)", "", regex=True
    )

    return df[["name", "stop", "direction", "minutes_remaining"]]


# Fetch and process timetable data
df = fetch_timetable(ext_id)
df_processed = calculate_minutes_remaining(df)

# Display the first 6 rows
print(df_processed.head(6))
