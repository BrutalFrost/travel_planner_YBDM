import pandas as pd
import requests
import os
import re
from dotenv import load_dotenv
from datetime import datetime, timedelta
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

def fetch_departures_one_hour_ahead(ext_id):
    future_time = (datetime.now() + timedelta(hours=1)).strftime("%H:%M")
    url = f"https://api.resrobot.se/v2.1/departureBoard?id={ext_id}&format=json&accessId={API_KEY}&time={future_time}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if "Departure" not in data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data["Departure"])[["name", "direction", "time"]]

        df["name"] = df["name"].apply(clean_text)
        df["Directed To"] = df["direction"].apply(clean_text)
        df["one_hour_ahead"] = pd.to_datetime(df["time"]).dt.strftime("%H:%M")
        
        return df[["name", "Directed To", "one_hour_ahead"]]

    except requests.exceptions.RequestException as err:
        print(f"Network error: {err}")
        return pd.DataFrame()

def fetch_arrivals_one_hour_ahead(ext_id):
    future_time = (datetime.now() + timedelta(hours=1)).strftime("%H:%M")
    url = f"https://api.resrobot.se/v2.1/arrivalBoard?id={ext_id}&format=json&accessId={API_KEY}&time={future_time}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if "Arrival" not in data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data["Arrival"])[["name", "origin", "time"]]

        df["name"] = df["name"].apply(clean_text)
        df["From"] = df["origin"].apply(clean_text)  
        df["one_hour_ahead"] = pd.to_datetime(df["time"]).dt.strftime("%H:%M")
        
        return df[["name", "From", "one_hour_ahead"]]

    except requests.exceptions.RequestException as err:
        print(f"Network error: {err}")
        return pd.DataFrame()

if __name__ == "__main__":
    future_departures = fetch_departures_one_hour_ahead(ext_id)
    future_arrivals = fetch_arrivals_one_hour_ahead(ext_id)

    print(future_departures)

    print(future_arrivals)
