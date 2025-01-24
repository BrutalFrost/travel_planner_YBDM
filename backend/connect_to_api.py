from dotenv import load_dotenv
import os
import requests
from pprint import pprint

#######################################
# added stuff

import pandas as pd


########################################

load_dotenv()


class ResRobot:
    def __init__(self):
        self.API_KEY = os.getenv("API_KEY")

        

    def trips(self, origin_id=740000001, destination_id=740098001):
        """origing_id and destination_id can be found from Stop lookup API"""
        url = f"https://api.resrobot.se/v2.1/trip?format=json&originId={origin_id}&destId={destination_id}&passlist=true&showPassingPoints=true&accessId={self.API_KEY}"

        try:
            response = requests.get(url)
            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as err:
            print(f"Network or HTTP error: {err}")

    def access_id_from_location(self, location):
        url = f"https://api.resrobot.se/v2.1/location.name?input={location}&format=json&accessId={self.API_KEY}"
        response = requests.get(url)
        result = response.json()

        print(f"{'Name':<50} extId")

        for stop in result.get("stopLocationOrCoordLocation"):
            stop_data = next(iter(stop.values()))

            # returns None if extId doesn't exist
            if stop_data.get("extId"):
                print(f"{stop_data['name']:<50} {stop_data['extId']}")

    def timetable_departure(self, location_id=740015565):
        url = f"https://api.resrobot.se/v2.1/departureBoard?id={location_id}&format=json&accessId={self.API_KEY}"
        response = requests.get(url)
        result = response.json()
        return result

    def timetable_arrival(self, location_id=740015565):
        url = f"https://api.resrobot.se/v2.1/arrivalBoard?id={location_id}&format=json&accessId={self.API_KEY}"
        response = requests.get(url)
        result = response.json()
        return result
    
    #def station_id(self, city="Göteborg"):

    def get_location_id(self,location):
        url = f"https://api.resrobot.se/v2.1/location.name?input={location}&format=json&accessId={self.API_KEY}"

        result=requests.get(url).json()
        int_res=result.get('stopLocationOrCoordLocation')
        return int(int_res[0]['StopLocation']['extId'])
    
    def tidtabell_df(self,stopid):
        url = f"https://api.resrobot.se/v2.1/departureBoard?id={stopid}&format=json&accessId={self.API_KEY}"
        response = requests.get(url)
        result =response.json()
        return pd.DataFrame(result['Departure'])
    
    def ddf_timetable2(self,place_from, place_to):
        fr_p=self.get_location_id(place_from)
        to_p=self.get_location_id(place_to)
        url= f"https://api.resrobot.se/v2.1/trip?format=json&originId={fr_p}&destId={to_p}&passlist=true&showPassingPoints=true&accessId={self.API_KEY}"

        response=requests.get(url).json()
        ex_trip=response['Trip']
        resexp=[]
        for timerow in ex_trip:
            st_time=timerow['Origin']['time']
            end_time=timerow['Destination']['time']
            resexp.append([st_time[:-3], end_time[:-3]])

        return pd.DataFrame(resexp, columns=[place_from, place_to])


if __name__ == "__main__":
    resrobot = ResRobot()
    # pprint(resrobot.timetable_arrival()["Arrival"][0])
    pprint(resrobot.ddf_timetable2("Göteborg","STockholm"))
