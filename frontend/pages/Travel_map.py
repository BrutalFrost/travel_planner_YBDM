import streamlit as st

from backend.connect_to_api import ResRobot
from frontend.plot_maps import TripMap

# Keep this if other style file should be loaded special a page
# from frontend.styleutil import cssstyle
resa = ResRobot()

trip_map = TripMap(
    origin_id=resa.get_location_id("Tranered"),
    destination_id=resa.get_location_id("Barnarp"),
)


st.sidebar.success("Your travel")
trip_map.display_map()

# cssstyle()
