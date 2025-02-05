from abc import ABC, abstractmethod

import folium
import streamlit as st

from backend.trips import TripPlanner


class Maps(ABC):
    """
    Abstract base class for map-related operations.

    Methods:
    --------
    display_map():
        Abstract method to display a map. Must be implemented by subclasses.
    """

    @abstractmethod
    def display_map(self):
        """
        Abstract method to display a map.

        Subclasses must provide an implementation for this method.
        """
        raise NotImplementedError


class TripMap(Maps):
    def __init__(self, origin_id, destination_id):
        trip_planner = TripPlanner(origin_id, destination_id)
        self.next_trip = trip_planner.next_available_trip()

    def _create_map(self):
        geographical_map = folium.Map(
            location=[self.next_trip["lat"].mean(), self.next_trip["lon"].mean()],
            zoom_start=5,
        )

        for _, row in self.next_trip.iterrows():
            folium.Marker(
                location=[row["lat"], row["lon"]],
                popup=f"{row['name']}<br>{row['time']}<br>{row['date']}",
            ).add_to(geographical_map)

        return geographical_map

    def _create_map2(self):
        # Sim as abve but diff folium markers
        geographical_map = folium.Map(
            location=[self.next_trip["lat"].mean(), self.next_trip["lon"].mean()],
            zoom_start=5,
        )

        coordinates = list(zip(self.next_trip["lat"], self.next_trip["lon"]))

        # Add a polyline to connect the
        folium.PolyLine(
            coordinates,
            color="blue",  # Line color
            weight=5,  # Line thickness
            opacity=0.7,  # Transparency
        ).add_to(geographical_map)

        first_stop = self.next_trip.iloc[0]
        folium.Marker(
            location=[first_stop["lat"], first_stop["lon"]],
            popup=f"Start: {first_stop['name']}<br>{first_stop['time']}<br>{first_stop['date']}",
            icon=folium.Icon(color="green", icon="play"),  # Green marker for start
        ).add_to(geographical_map)

        # Add marker for the last stop (destination)
        last_stop = self.next_trip.iloc[-1]
        folium.Marker(
            location=[last_stop["lat"], last_stop["lon"]],
            popup=f"Destination: {last_stop['name']}<br>{last_stop['time']}<br>{last_stop['date']}",
            icon=folium.Icon(color="red", icon="flag"),  # Red marker for destination
        ).add_to(geographical_map)

        for _, row in self.next_trip.iloc[1:-1].iterrows():  # Exclude first and last
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=5,  # Small size
                color="blue",  # Border color
                fill=True,
                fill_color="white",
                fill_opacity=0.6,
                popup=f"{row['name']}<br>{row['time']}<br>{row['date']}",
            ).add_to(geographical_map)

        return geographical_map

    def display_map(self):
        st.markdown("## Karta över stationerna i din resa")
        st.markdown(
            "Klicka på varje station för mer information. Detta är en exempelresa mellan Malmö och Umeå"
        )
        st.components.v1.html(self._create_map()._repr_html_(), height=500)

    def display_map_lines(self):
        st.markdown("## Karta över stationerna i din resa")
        st.markdown(
            "Klicka på varje station för mer information. Detta är en exempelresa mellan Malmö och Umeå"
        )
        st.components.v1.html(self._create_map2()._repr_html_(), height=500)
