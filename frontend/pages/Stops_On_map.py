import streamlit as st
from backend.stop_on_map import get_trip_stops, get_location_id
from frontend.plot_maps import TripMap

st.title("🚆 Travel Planner")

departure = st.text_input("Enter Departure City", placeholder="Göteborg Centralstation")
destination = st.text_input("Enter Destination City", placeholder="Stockholm Centralstation")

if st.button("Find Trip Stops"):
    departure_id = get_location_id(departure)
    destination_id = get_location_id(destination)

    if not departure_id or not destination_id:
        st.error("Invalid departure or destination.")
    else:
        result = get_trip_stops(departure, destination)

        if not result:
            st.error("No trip found.")
        else:
            st.success(f"Trip from **{departure}** to **{destination}**")
            st.write("### Stops on the route:")
            for stop in result:
                st.write(f"- {stop}")

            st.write(f"### Total Number of Stops: {len(result)}")

            trip_map = TripMap(departure_id, destination_id)
            st.write("### Route Map:")
            trip_map.display_map()
