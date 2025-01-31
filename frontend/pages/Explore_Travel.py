import pandas as pd
import requests
import streamlit as st

# from frontend.plot_maps import TripMap
from backend.connect_to_api import ResRobot
from frontend.plot_maps import TripMap

# Move to resBot


# def get_locations(self, location):
def get_location(location):
    url = f"https://api.resrobot.se/v2.1/location.name?input={location}&format=json&accessId={resa.API_KEY}"
    response = requests.get(url)
    result = response.json()
    res = result.get("stopLocationOrCoordLocation")

    extracted_data = [
        {"name": stop["StopLocation"]["name"], "stopid": stop["StopLocation"]["extId"]}
        for stop in res
    ]
    return pd.DataFrame(extracted_data)
    # ['stopLocationOrCoordLocation']


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
        numstops = timerow["transferCount"]
        resexp.append([st_time[:-3], end_time[:-3], numstops])

    return pd.DataFrame(resexp, columns=[place_from, place_to, "Changes"])


def city_select_id(start_location):
    selected_from = None
    if start_location != "None":
        df_from = get_location(start_location)
        if df_from.shape[0] > 0:
            selected_from = st.selectbox(
                label="Select a location",  # Provide a non-empty label
                options=df_from,
                label_visibility="collapsed",
            )

    return selected_from


resa = ResRobot()
st.markdown("# Reseplanerare")
st.markdown(
    "Den här dashboarden syftar till att både utforska data för olika platser, men ska även fungera som en reseplanerare där du får välja och planera din resa."
)

start_location = st.text_input("## Select start point", "None")
sel_start = city_select_id(start_location)

stop_location = st.text_input("## Select destination", "None")

sel_stop = city_select_id(stop_location)

if start_location != "None" and stop_location != "None":
    st.markdown("## Time table")

    df = df_timetable_explore(
        resa.get_location_id(sel_start), resa.get_location_id(sel_stop)
    )

    st.dataframe(df)

    trip_map = TripMap(
        origin_id=resa.get_location_id(sel_start),
        destination_id=resa.get_location_id(sel_stop),
    )
    trip_map.display_map()

    st.markdown(resa.trips)
    st.sidebar.success("Your travel")


# selected = st.selectbox("Where from", options=df_from)
