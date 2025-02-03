# import os
# import re
from pprint import pprint
import requests
import pandas as pd

import folium

# import pandas as pd
# import requests
import streamlit as st

# from dotenv import load_dotenv
from streamlit.components.v1 import html

from backend.connect_to_api import ResRobot

# from backend.trips import TripPlanner
# from frontend.plot_maps import TripMap

# API_KEY= os.getenv("API_KEY")


mytravel = ResRobot()

# 0
# a) Make a function for doing get request for time tables API in resrobot
#
# x = mytravel.ddf_timetable2("Tranred","Göteborg")

# ----------------
# b) Find the number of transports arriving to Göteborg centralstationen
#
# x=mytravel.timetable_arrival(location_id=mytravel.get_location_id("Göteborg Centralstation"))
# print(len(x['Arrival']))

# ----------------
# c) Find the number of transports departuring from Göteborg centralstationen
#
# x=mytravel.timetable_departure(location_id = mytravel.get_location_id("Göteborg Centralstation"))
# print(len(x['Departure']))
# ----------------

# d) Find the trams departuring from Göteborg centralstationen, their destinations
#    and time. Note that trams in Swedish is "spårvagn" or in the dataset denoted
#    as "Spårväg".

# timetable = mytravel.tidtabell_df(mytravel.get_location_id("Tranered"))
# pattern = "Spårväg"
# x = timetable[timetable["name"].str.contains(pattern, na=False)]
# spec_trav = x[["direction", "time", "lon", "lat", "date"]]

# ----------------


# e) See if you can plot in a map points corresponding to directions of each departuring tram.
#
# start_pos = mytravel.get_location_id("Tranered")

# end_pos = spec_trav[["direction", "lon", "lat"]].drop_duplicates()
# # mytravel.trips()


# geographical_map = folium.Map(
#     location=[end_pos["lat"].mean(), end_pos["lon"].mean()],
#     zoom_start=12,
# )

# for row in end_pos.itertuples(index=True, name="Row"):
#     pprint()
#     folium.Marker(
#         location=[row.lat, row.lon],
#         popup=f"{row.direction}<br>",
#     ).add_to(geographical_map)


# html_map = geographical_map._repr_html_()  # Get the map's HTML representation
# st.markdown("## Karta över stationerna i din resa")
# st.markdown("Klicka på varje station för mer information.")
# html(html_map, height=500)

def trips(origin_id=740000001, destination_id=740098001):
        """origing_id and destination_id can be found from Stop lookup API"""
        url = f"https://api.resrobot.se/v2.1/trip?format=json&originId={origin_id}&destId={destination_id}&passlist=true&showPassingPoints=true&accessId={mytravel.API_KEY}"

        try:
            response = requests.get(url)
            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as err:
            print(f"Network or HTTP error: {err}")


start=mytravel.get_location_id("tranered")
stop=mytravel.get_location_id("barnarp")
#pprint(trips(start,stop)['Trip'][2]['LegList']['Leg'][7]['name'])
for pos in trips(start,stop)['Trip'][0]['LegList']['Leg']:
     pprint(pos['name']) 
     
     if pos['name'] != 'Promenad':
        pprint(pos['direction'])
        for put in pos['Stops']['Stop']:
            pprint(put['name'])
     else:
          pprint(pos['dist'])
     pprint('------------------------------------------------------')







