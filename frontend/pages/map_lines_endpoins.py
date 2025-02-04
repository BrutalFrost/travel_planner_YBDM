from backend.connect_to_api import ResRobot
from frontend.plot_maps import TripMap
import streamlit as st
import pandas as pd
import requests

resa=ResRobot()


# get location with maxNo=50 -- needed?
def get_location(location):
    url = f"https://api.resrobot.se/v2.1/location.name?input={location}&format=json&accessId={resa.API_KEY}&maxNo=50"
    response = requests.get(url)
    result = response.json()
    res = result.get("stopLocationOrCoordLocation")
    extracted_data=[]

    for stop in res:
        stop_location = stop.get("StopLocation")
        if stop_location:
            extracted_data.append({"name": stop["StopLocation"]["name"], "stopid": stop["StopLocation"]["extId"]})
    return pd.DataFrame(extracted_data)

def city_select_id(start_location):
    selected_from = None
    if start_location != "None":
        df_from = get_location(start_location)
        if df_from.shape[0] > 0:
            selected_from = st.selectbox(
                label="Select a location",  
                options=df_from,
                label_visibility="collapsed",
            )

    return selected_from

# ---------------------------------------------------------------------

def df_timetable_explore(place_from, place_to):
    resa = ResRobot()
    fr_p = resa.get_location_id(place_from)
    to_p = resa.get_location_id(place_to)
    url = f"https://api.resrobot.se/v2.1/trip?format=json&originId={fr_p}&destId={to_p}&passlist=true&showPassingPoints=true&accessId={resa.API_KEY}"

    response = requests.get(url).json()
    ex_trip = response["Trip"]
    resexp = []
    for timerow in ex_trip:
        st_time = timerow["Origin"]["time"]
        end_time = timerow["Destination"]["time"]
        numstops = timerow.get("transferCount", 0)
        resexp.append([st_time[:-3], end_time[:-3], numstops])

    return pd.DataFrame(resexp, columns=[place_from, place_to, "Changes"])

# here is the actual map method

# fixing the map

start_location = st.text_input("## Select start point", "None")
sel_start = city_select_id(start_location)

stop_location = st.text_input("## Select destination", "None")

sel_stop = city_select_id(stop_location)

if (
    start_location != "None"
    and stop_location != "None"
    and sel_start is not None
    and sel_stop is not None
):
    st.markdown("## Time table")

    df = df_timetable_explore(
        resa.get_location_id(sel_start), resa.get_location_id(sel_stop)
    )

    st.dataframe(df)

    trip_map = TripMap(
        origin_id=resa.get_location_id(sel_start),
        destination_id=resa.get_location_id(sel_stop),
    )
    trip_map.display_map_lines()

    st.sidebar.success("Your travel")
