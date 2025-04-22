import os
import json
import urllib.request

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API keys from environment variables
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
MBTA_API_KEY = os.getenv("MBTA_API_KEY")

# Useful base URLs (you need to add the appropriate parameters for each API request)
MAPBOX_BASE_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"
MBTA_BASE_URL = "https://api-v3.mbta.com/stops"

#YOU CAN IGNORE THIS FOR NOW, IT WAS ME JUST TESTING OUT THE API HAHA
# city = "Boston"
# url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{city}.json?access_token={MAPBOX_TOKEN}"
# print(url)


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
    url = f"{MAPBOX_BASE_URL}/{formatted_place}.json?access_token={MAPBOX_TOKEN}"
    map_data = get_json(url)

    # coords = data["features"][0]["geometry"]["coordinates"]
    coords = map_data["features"][0]["center"]  # this comes from a dict


    return coords[1],coords[0] #return as a tuple

def get_nearest_station(latitude: str, longitude: str) -> tuple[str, bool]:
    """
    Given latitude and longitude strings, return a (station_name, wheelchair_accessible) tuple for the nearest MBTA station to the given coordinates.

    See https://api-v3.mbta.com/docs/swagger/index.html#/Stop/ApiWeb_StopController_index for URL formatting requirements for the 'GET /stops' API.
    """
    url = f"{MBTA_BASE_URL}?api_key={MBTA_API_KEY}&filter[latitude]={latitude}&filter[longitude]={longitude}&sort=distance"
    
    mbta_data = get_json(url)

    if not mbta_data["data"]:
        return ("No nearby stations found 😕", False)
    
    first_stop = mbta_data["data"][0]
    station_name = first_stop["attributes"]["name"]
    wheelchair_code = first_stop["attributes"]["wheelchair_boarding"]

    #this turns the wheelchair code to a boolean
    wheelchair_accessible = wheelchair_code == 1

    return station_name, wheelchair_accessible

def find_stop_near(place_name: str) -> tuple[str, bool]:
    """
    Given a place name, return the nearest MBTA stop and wheelchair accessibility.
    """
    lat, lng = get_lat_lng(place_name)
    return get_nearest_station(lat, lng)


def main():
    """
    Test the functions here.
    """
    try:
        lat, lng = get_lat_lng("Harvard University")
        print("Latitude:", lat, "Longitude:", lng)

        station_name, accessible = find_stop_near("Harvard University")
        print(f"Nearest MBTA stop: {station_name}")
        print(f"Wheelchair accessible: {'Yes' if accessible else 'No'}")
    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()