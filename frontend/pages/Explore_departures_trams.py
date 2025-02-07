import pandas as pd
import requests
import streamlit as st

# from frontend.plot_maps import TripMap
from backend.connect_to_api import ResRobot

# these method are already pushed but not merged

resa = ResRobot()


def city_select_id(start_location):
    selected_from = "None"
    if start_location != "None":
        df_from = resa.get_location(start_location)
        if df_from.shape[0] > 0:
            selected_from = st.selectbox(
                label="Select a location",  # Provide a non-empty label
                options=df_from,
                label_visibility="collapsed",
            )

    return selected_from


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


##########################

# add this to Resrobot, add self, resa -> self


def get_depatures_trams(place):
    timetable = resa.tidtabell_df(resa.get_location_id(place))
    # st.dataframe(pd)

    timetable_list = timetable.to_dict(orient="records")
    dep_name = [entry["name"] for entry in timetable_list if "Spårväg" in entry["name"]]
    dep_dir = [
        entry["direction"] for entry in timetable_list if "Spårväg" in entry["name"]
    ]
    dep_time = [entry["time"] for entry in timetable_list if "Spårväg" in entry["name"]]
    xyz = pd.DataFrame({"name": dep_name, "direction": dep_dir, "time": dep_time})

    return xyz


##################


st.markdown("# Explore Tram Departures from a location")
st.markdown(
    "This Dashboard shows departing trams from a location. It will show the destinations of the trams"
)

start_location = st.text_input("## Select start point", "None")
sel_start = resa.city_select_id(start_location)

# st.markdown(sel_start)
if sel_start != "None":
    df = get_depatures_trams(sel_start)

    st.dataframe(df)
