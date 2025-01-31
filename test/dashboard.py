import streamlit as st
from testing import calculate_minutes_remaining, fetch_timetable, get_location_ext_id


def main():
    st.title("Reseplanerare")

    # User input for location
    location = st.text_input("Enter a location:", "Angered Centrum")
    if location:
        ext_ids = get_location_ext_id(location)
        if ext_ids:
            st.markdown("### Available Locations")
            for ext in ext_ids:
                st.write(f"**{ext['name']}** (extId: {ext['extId']})")

            # Allow user to select an extId
            selected_ext_id = st.selectbox(
                "Select extId for timetable:", [ext["extId"] for ext in ext_ids]
            )

            if selected_ext_id:
                st.markdown(f"Selected extId: **{selected_ext_id}**")

                # Fetch and display timetable
                timetable_df = fetch_timetable(selected_ext_id)
                if not timetable_df.empty:
                    timetable_df = calculate_minutes_remaining(timetable_df)
                    st.markdown("### Timetable for BUS/TRAM departure in minutes")
                    st.table(timetable_df.style.format({"minutes_remaining": "{:.0f}"}))
                else:
                    st.error("No timetable data available.")
        else:
            st.error("No locations found for the given input.")
