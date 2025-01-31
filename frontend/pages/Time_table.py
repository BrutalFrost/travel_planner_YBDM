import streamlit as st

# from frontend.plot_maps import TripMap
from backend.connect_to_api import ResRobot
from backend.one_hour_ahead import fetch_clean_timetable_one_hour_ahead
from backend.time_table import calculate_minutes_remaining, fetch_timetable

st.sidebar.success("Your timetable")
resa = ResRobot()
st.markdown("## Time Table")
st.markdown("This is the tme table for Tranered to Barnarp")
df = resa.ddf_timetable2(
    resa.get_location_id("Tranered"), resa.get_location_id("Barnarp")
)
st.dataframe(df)


st.markdown("### Time table for Train/Buss/Tram in miuntes ")
location_name = st.text_input("Enter Stop Name:")

if location_name:
    timetable = ResRobot()
    ext_id = timetable.get_location_id(location_name)

    if ext_id is not None:
        df = fetch_timetable(ext_id)
        df_processed = calculate_minutes_remaining(df)
        st.dataframe(df_processed)
    else:
        st.error(
            f"Could not find stop ID for '{location_name}'. Please check the name."
        )
else:
    st.warning("Please enter a stop name to see the timetable.")


st.markdown("### Time Table for Train/Buss/Tram One Hour Ahead")
location_name_one_hour = st.text_input("Enter Stop Name for One-Hour-Ahead Timetable:")

if location_name_one_hour:
    timetable = ResRobot()
    ext_id_one_hour = timetable.get_location_id(location_name_one_hour)

    if ext_id_one_hour is not None:
        df_one_hour = fetch_clean_timetable_one_hour_ahead(ext_id_one_hour)

        if df_one_hour.empty:
            st.warning(
                f"No departures scheduled one hour ahead for '{location_name_one_hour}'. Try another stop."
            )
        else:
            st.dataframe(df_one_hour)
    else:
        st.error(
            f"Could not find stop ID for '{location_name_one_hour}'. Please check the name."
        )
else:
    st.warning("Please enter a stop name to see the one-hour-ahead timetable.")
