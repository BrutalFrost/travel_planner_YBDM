import os
import re
from datetime import datetime, timedelta

import pandas as pd
import requests
from dotenv import load_dotenv

from backend.connect_to_api import ResRobot

load_dotenv()
API_KEY = os.getenv("API_KEY")

timetable = ResRobot()
location_name = "Angered Centrum"
ext_id = str(timetable.get_location_id(location_name))


def clean_text(text):
    """Removes anything in parentheses and extra prefixes like 'Länstrafik - '."""
    if pd.isna(text):
        return ""
    text = re.sub(r"Länstrafik - ", "", text)
    text = re.sub(r"\s*\(.*?\)", "", text)
    return text.strip()


def fetch_clean_timetable_one_hour_ahead(ext_id):
    """Fetches and cleans the timetable, showing departures exactly one hour ahead."""
    future_time = (datetime.now() + timedelta(hours=1)).strftime("%H:%M")
    url = f"https://api.resrobot.se/v2.1/departureBoard?id={ext_id}&format=json&accessId={API_KEY}&time={future_time}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "Departure" not in data:
            return pd.DataFrame()

        df = pd.DataFrame(data["Departure"])[["name", "stop", "direction", "time"]]

        df["name"] = df["name"].apply(clean_text)
        df["stop"] = df["stop"].apply(clean_text)
        df["direction"] = df["direction"].apply(clean_text)
        df["one_hour_ahead"] = pd.to_datetime(df["time"]).dt.strftime("%H:%M")

        return df.drop(columns=["time"])

    except requests.exceptions.RequestException as err:
        print(f"Network error: {err}")
        return pd.DataFrame()


if __name__ == "__main__":
    future_timetable = fetch_clean_timetable_one_hour_ahead(ext_id)
    print(future_timetable)
