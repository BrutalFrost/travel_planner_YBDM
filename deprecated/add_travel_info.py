import streamlit as st

from backend.connect_to_api import ResRobot

resa = ResRobot()

# method for specific starvel with detailed information


def detailed_travel_info(start, stop):
    for pos in resa.trips(start, stop)["Trip"][0]["LegList"]["Leg"]:
        if pos["name"] != "Promenad":
            st.markdown(f" {pos['name']}  Direction to {pos['direction']}")
            for put in pos["Stops"]["Stop"]:
                time = put.get("depTime") or put.get("arrTime")
                st.markdown(
                    f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {put['name']} {time[:-3]}"
                )
        else:
            st.markdown(f"Walk {pos['dist']} meters")
        st.markdown("  ")


detailed_travel_info(
    start=resa.get_location_id("tranered"), stop=resa.get_location_id("barnarp")
)
