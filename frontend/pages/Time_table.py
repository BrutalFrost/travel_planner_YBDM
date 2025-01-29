import streamlit as st 
# from frontend.plot_maps import TripMap
from backend.connect_to_api import ResRobot


st.sidebar.success("Your timetable")
resa =ResRobot()
st.markdown("## Time Table")
st.markdown("This is the tme table for Tranered to Barnarp")
df = resa.ddf_timetable2(resa.get_location_id("Tranered"),resa.get_location_id("Barnarp"))

st.dataframe(df)