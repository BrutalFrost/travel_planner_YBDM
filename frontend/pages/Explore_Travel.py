import sys
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

# from frontend.plot_maps import TripMap
from backend.connect_to_api import ResRobot
from frontend.plot_maps import TripMap

sys.path.append(str(Path(__file__).parents[2]))
# def get_locations(self, location):
resa = ResRobot()
# ['stopLocationOrCoordLocation']


def df_timetable_explore(place_from, place_to):
    resa = ResRobot()
    url = f"https://api.resrobot.se/v2.1/trip?format=json&originId={place_from}&destId={place_to}&destWalk=1,0,700,125&passlist=true&showPassingPoints=true&accessId={resa.API_KEY}"

    response = requests.get(url).json()
    ex_trip = response["Trip"]
    resexp = []
    it = 0
    for timerow in ex_trip:
        st_time = timerow["Origin"]["time"]
        end_time = timerow["Destination"]["time"]

        numstops = timerow.get("transferCount", 0)

        legs = ex_trip[it].get("LegList", {}).get("Leg", [])
        product_name = ""
        for leg in legs:
            product = leg.get("Product")

            product_name = product[0].get("name", "Unknown Product")
            if product_name == "Promenad":
                continue
            resexp.append([product_name, st_time[:-3], end_time[:-3], numstops])

        it += 1

    return (
        pd.DataFrame(
            resexp, columns=["Line", "Departure Time", "Arrival Time", "Changes"]
        ),
        ex_trip,
    )


def extract_origins(data):
    origins = []
    if "LegList" in data and "Leg" in data["LegList"]:
        for leg in data["LegList"]["Leg"]:
            if "Origin" in leg:
                origins.append(leg["Origin"]["name"])
    return origins


def city_select_id(start_location):
    selected_from = None
    if start_location != "None" and start_location != "" and start_location is not None:
        df_from = resa.get_location(start_location)
        if df_from.shape[0] > 0:
            selected_from = st.selectbox(
                label="Select a location",
                options=df_from,
                label_visibility="collapsed",
            )

    return selected_from


def detailed_travel_info(start, stop, it):
    for pos in resa.trips(start, stop)["Trip"][it]["LegList"]["Leg"]:
        if pos["name"] != "Promenad":
            st.markdown(f" {pos['name']}  Direction to {pos['direction']}")
            for put in pos["Stops"]["Stop"]:
                time = put.get("depTime") or put.get("arrTime")
                st.markdown(
                    f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {put['name']} {time[:-3]}"
                )
        else:
            st.markdown(f"Walk {pos['dist']} meters.")
        st.markdown("  ")


st.markdown("# Reseplanerare")
st.markdown(
    "Den här dashboarden syftar till att både utforska data för olika platser, men ska även fungera som en reseplanerare där du får välja och planera din resa."
)


start_location = st.text_input("## Select start point", placeholder="Göteborg")
sel_start = resa.city_select_id(start_location)

stop_location = st.text_input("## Select destination", placeholder="Angered")

sel_stop = resa.city_select_id(stop_location)

if (
    start_location != "None"
    and stop_location != "None"
    and sel_start is not None
    and sel_stop is not None
):
    st.markdown("## Time table")
    st.markdown("Line, Departure Time, Arrival Time, Amount of Changes")
    st.markdown("Click to expand to get information on changes")

    df, ex_trip = df_timetable_explore(
        resa.get_location_id(sel_start),
        resa.get_location_id(sel_stop),
    )
    skip_bool = False
    a = 0
    for index, row in df.iterrows():
        # To stop a bug from creating more expanders than 5 since that breaks the code. Do not remove.
        if a >= 5:
            break

        # To skip the next row if the current row has a change, ensuring it doesn't treat each change as an idividual trip.
        if skip_bool:
            skip_bool = False
            continue
        if int(row["Changes"]) > 0:
            skip_bool = True
        else:
            skip_bool = False

        if row["Line"] != "Promenad":
            with st.expander(
                f"{row['Line']}, {row['Departure Time']}, {row['Arrival Time']}, {row['Changes']}"
            ):
                st.markdown("")

                # pass

                detailed_travel_info(
                    start=resa.get_location_id(sel_start),
                    stop=resa.get_location_id(sel_stop),
                    it=a,
                )
        a += 1

    trip_map = TripMap(
        origin_id=resa.get_location_id(sel_start),
        destination_id=resa.get_location_id(sel_stop),
    )
    # Rendering map
    trip_map.display_map_lines()

    st.sidebar.success("Your travel")
