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

    # Print the entire response for debugging
    print("Response JSON:", result)

    # Extract the relevant data
    res = result.get("stopLocationOrCoordLocation")
    if res is None:
        raise ValueError("No stopLocationOrCoordLocation found in the response")

    # Extract data if 'StopLocation' key exists
    extracted_data = [
        {"name": stop["StopLocation"]["name"], "stopid": stop["StopLocation"]["extId"]}
        for stop in res
        if "StopLocation" in stop
    ]
    return pd.DataFrame(extracted_data)
    # ['stopLocationOrCoordLocation']


def df_timetable_explore(place_from, place_to, fr_name, to_name):
    resa = ResRobot()
    fr_p = resa.get_location_id(place_from)
    to_p = resa.get_location_id(place_to)
    url = f"https://api.resrobot.se/v2.1/trip?format=json&originId={fr_p}&destId={to_p}&passlist=true&showPassingPoints=true&accessId={resa.API_KEY}"

    response = requests.get(url).json()
    ex_trip = response["Trip"]
    resexp = []
    for trip in ex_trip:
        for leg in trip["LegList"]["Leg"]:
            st_time = leg["Origin"]["time"]
            end_time = leg["Destination"]["time"]

            print(f"Leg: {leg}")
            print(f"Leg Product: {leg['Product']}")

            if isinstance(leg["Product"], list):
                print(f"Leg Product is a list: {leg['Product']}")
                product_name = leg["Product"][0][
                    "name"
                ]  # Assuming you want the first product
            else:
                product_name = leg["Product"]["name"]
                numstops = trip.get("transferCount", 0)
                resexp.append([st_time[:-3], end_time[:-3], product_name, numstops])

    return pd.DataFrame(resexp, columns=[fr_name, to_name, "Line", "Changes"])


def city_select_id(start_location):
    selected_from = None
    if start_location != "None" and start_location != "" and start_location is not None:
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

start_location = st.text_input("## Select start point", placeholder="Göteborg")
sel_start = city_select_id(start_location)

stop_location = st.text_input("## Select destination", placeholder="Angered")

sel_stop = city_select_id(stop_location)

if (
    start_location != "None"
    and stop_location != "None"
    and sel_start is not None
    and sel_stop is not None
):
    st.markdown("## Time table")

    df = df_timetable_explore(
        resa.get_location_id(sel_start),
        resa.get_location_id(sel_stop),
        sel_start,
        sel_stop,
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
