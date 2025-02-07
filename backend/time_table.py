from datetime import datetime

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

from backend.connect_to_api import ResRobot

load_dotenv()
API_KEY = st.secrets["api"]["API_KEY"]

timetable = ResRobot()
location_name = "Angered Centrum"
ext_id = timetable.get_location_id(location_name)

if isinstance(ext_id, int):
    ext_id = str(ext_id)
else:
    raise ValueError(
        f"No valid extId found for '{location_name}'. Check the stop name and try again."
    )


def fetch_timetable_departure(ext_id):
    url = f"https://api.resrobot.se/v2.1/departureBoard?id={ext_id}&format=json&accessId={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data.get("Departure", []))
    except requests.exceptions.RequestException as err:
        print(f"Network or HTTP error: {err}")
        return pd.DataFrame()


def fetch_timetable_arrival(ext_id):
    url = f"https://api.resrobot.se/v2.1/arrivalBoard?id={ext_id}&format=json&accessId={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data.get("Arrival", []))
    except requests.exceptions.RequestException as err:
        print(f"Network or HTTP error: {err}")
        return pd.DataFrame()


def calculate_minutes_remaining_depart(df):
    if df.empty:
        return df

    current_time = datetime.now()
    df["departure_datetime"] = pd.to_datetime(
        df["date"].astype(str) + " " + df["time"].astype(str)
    )
    df["minutes_remaining"] = (
        df["departure_datetime"] - current_time
    ).dt.total_seconds() // 60
    df = df[df["minutes_remaining"] >= 0].copy()

    df["name"] = df["name"].str.replace(r"^Länstrafik - ", "", regex=True)

    df["Directed To"] = (
        df["direction"].str.replace(r"\s*\(Göteborg kn\)", "", regex=True)
        if "direction" in df
        else "Unknown"
    )

    return df[["name", "Directed To", "minutes_remaining"]]


def calculate_minutes_remaining_arrival(df):
    if df.empty:
        return df

    current_time = datetime.now()
    df["arrival_datetime"] = pd.to_datetime(
        df["date"].astype(str) + " " + df["time"].astype(str)
    )
    df["minutes_remaining"] = (
        df["arrival_datetime"] - current_time
    ).dt.total_seconds() // 60
    df = df[df["minutes_remaining"] >= 0].copy()

    df["name"] = df["name"].str.replace(r"^Länstrafik - ", "", regex=True)

    df["From"] = (
        df["direction"].str.replace(r"\s*\(Göteborg kn\)", "", regex=True)
        if "direction" in df
        else df.get("origin", df.get("destination", "Unknown"))
    )

    return df[["name", "From", "minutes_remaining"]]


df_depart = fetch_timetable_departure(ext_id)
df_arrival = fetch_timetable_arrival(ext_id)

df_processed_departure = calculate_minutes_remaining_depart(df_depart)
df_processed_arrival = calculate_minutes_remaining_arrival(df_arrival)

print(df_processed_departure.head(6))

print(df_processed_arrival.head(6))
