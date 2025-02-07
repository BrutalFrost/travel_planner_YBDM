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


def depart_time(df):
    if df.empty:
        return df

    df["departure_datetime"] = pd.to_datetime(
        df["date"].astype(str) + " " + df["time"].astype(str)
    )
    df["minutes_remaining"] = df["departure_datetime"]

    df["name"] = df["name"].str.replace(r"^Länstrafik - ", "", regex=True)

    df["Directed To"] = (
        df["direction"].str.replace(r"\s*\(Göteborg kn\)", "", regex=True)
        if "direction" in df
        else "Unknown"
    )

    df["time"] = pd.to_datetime(df["time"], format="%H:%M:%S").dt.strftime(
        "%H:%M"
    )  # Show only HH:mm if minutes = 00
    df.loc[df["time"].str.endswith(":00"), "time"] = pd.to_datetime(
        df["time"], format="%H:%M"
    ).dt.strftime("%H:%M")

    return df[["time", "name", "Directed To"]]


def arrival_time(df):
    if df.empty:
        return df

    df["arrival_datetime"] = pd.to_datetime(
        df["date"].astype(str) + " " + df["time"].astype(str)
    )
    df["minutes_remaining"] = df["arrival_datetime"]

    df["name"] = df["name"].str.replace(r"^Länstrafik - ", "", regex=True)

    df["From"] = (
        df["direction"].str.replace(r"\s*\(Göteborg kn\)", "", regex=True)
        if "direction" in df
        else df.get("origin", df.get("destination", "Unknown"))
    )

    df["time"] = pd.to_datetime(df["time"], format="%H:%M:%S").dt.strftime(
        "%H:%M"
    )  # Show only HH:mm if minutes = 00
    df.loc[df["time"].str.endswith(":00"), "time"] = pd.to_datetime(
        df["time"], format="%H:%M"
    ).dt.strftime("%H:%M")

    return df[
        [
            "time",
            "name",
            "From",
        ]
    ]


df_depart = fetch_timetable_departure(ext_id)
df_arrival = fetch_timetable_arrival(ext_id)

df_processed_departure = depart_time(df_depart)
df_processed_arrival = arrival_time(df_arrival)


print(df_processed_departure.head(6))
print(df_processed_arrival.head(6))
