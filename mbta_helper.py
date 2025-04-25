import os
import json, requests
import urllib.request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API keys from environment variables
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
MBTA_API_KEY = os.getenv("MBTA_API_KEY")
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Useful base URLs (you need to add the appropriate parameters for each API request)
# MAPBOX_BASE_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"
MAPBOX_BASE_URL = "https://api.mapbox.com/search/searchbox/v1/forward?"
MBTA_BASE_URL = "https://api-v3.mbta.com/stops"
SUN_API = "https://api.sunrise-sunset.org"


# A little bit of scaffolding if you want to use it


def get_json(url: str) -> dict:
    """
    Given a properly formatted URL for a JSON web API request, return a Python JSON object containing the response to that request.

    Both get_lat_lng() and get_nearest_station() might need to use this function.
    """

    with urllib.request.urlopen(url) as response:
        response_text = response.read().decode("utf-8")

        return json.loads(response_text)


def get_lat_lng(place_name: str) -> tuple[str, str]:
    """
    Given a place name or address, return a (latitude, longitude) tuple with the coordinates of the given place.

    See https://docs.mapbox.com/api/search/geocoding/ for Mapbox Geocoding API URL formatting requirements.
    """

    formatted_place = place_name.replace(" ", "%20")
    # https://api.mapbox.com/search/searchbox/v1/suggest?q=harvard%2520university&session_token=07fd63ff-37a4-43f8-8196-686b1b08029f&access_token=YOUR_MAPBOX_ACCESS_TOKEN
    url = f"{MAPBOX_BASE_URL}q={formatted_place}&access_token={MAPBOX_TOKEN}"
    # print(url)
    map_data = get_json(url)

    # coords = data["features"][0]["geometry"]["coordinates"]
    # print(map_data["features"][0].keys())
    coords = map_data["features"][0]["properties"][
        "coordinates"
    ]  # this comes from a dict

    return coords["latitude"], coords["longitude"]  # return as a tuple


def get_nearest_station(latitude: str, longitude: str) -> tuple[str, bool]:
    """
    Given latitude and longitude strings, return a (station_name, wheelchair_accessible) tuple for the nearest MBTA station to the given coordinates.

    See https://api-v3.mbta.com/docs/swagger/index.html#/Stop/ApiWeb_StopController_index for URL formatting requirements for the 'GET /stops' API.
    """
    url = f"{MBTA_BASE_URL}?api_key={MBTA_API_KEY}&filter[latitude]={latitude}&filter[longitude]={longitude}&filter[radius]=0.02&filter[route_type]=0,1,2&sort=distance"
    mbta_data = get_json(url)

    if not mbta_data["data"]:
        return "No nearby stations found 😕", False, None, None
    first_stop = mbta_data["data"][0]
    station_name = first_stop["attributes"]["name"]
    wheelchair_code = first_stop["attributes"]["wheelchair_boarding"]
    wheelchair_accessible = wheelchair_code == 1

    # grab the stop's actual coords
    stop_lat = first_stop["attributes"]["latitude"]
    stop_lng = first_stop["attributes"]["longitude"]

    return station_name, wheelchair_accessible, stop_lat, stop_lng


def find_stop_near(place_name: str) -> tuple[str, bool]:
    """
    Given a place name, return the nearest MBTA stop and wheelchair accessibility.
    """
    lat, lng = get_lat_lng(place_name)
    return get_nearest_station(lat, lng)

def sun_time(latitude: str, longitude: str) -> tuple[str, str]:
    '''
    Given latitude and longitude strings, return the sunrise and sunset time for the location.
    '''
    import requests

def sun_time(latitude: str, longitude: str) -> tuple[str, str]:
    '''
    Given latitude and longitude strings, return the sunrise and sunset time for the location.
    '''
    url = f"{SUN_API}/json?lat={latitude}&lng={longitude}"
    response = requests.get(url)  
    data = response.json()      
    
    sunrise = data["results"]["sunrise"]
    sunset = data["results"]["sunset"]
    return sunrise, sunset

def weather_check(latitude: str, longitude: str) -> tuple:
    """
    Fetch current weather for the given coords.
    """
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={latitude}&lon={longitude}&appid={WEATHER_API_KEY}&units=metric"
    )
    weather_data = get_json(url)

    desc = weather_data["weather"][0]["description"].capitalize()
    temp = weather_data["main"]["temp"]

    return desc, temp

 
def main():
    """
    Test the functions here.
    """
    try:

        lat, lng = get_lat_lng("Harvard University, ma")
        print("Latitude:", lat, "Longitude:", lng)

        station_name, accessible, stop_lat, stop_lng = find_stop_near(
            "Harvard University"
        )

        sunrise, sunset = sun_time(lat, lng)

        desc, temp = weather_check(lat, lng)

        print(f"Nearest MBTA stop: {station_name}")
        print(f"Wheelchair accessible: {'Yes' if accessible else 'No'}")
        print(f"Station Coordinates: {stop_lat}, {stop_lng}")
        print(f"Sun Can Be Seen From: {sunrise} to {sunset}")
        print(f"Weather Today: {desc}, {temp}°C")


    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()
