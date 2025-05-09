from flask import Flask, render_template, request
from mbta_helper import get_lat_lng, get_nearest_station, sun_time, weather_check
import os
from dotenv import load_dotenv

load_dotenv()
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        place = request.form['place']
        lat, lng = get_lat_lng(place)
        if lat is None:
            return render_template('index.html', error="Location not found", mapbox_token=MAPBOX_TOKEN)

        station_name, accessible, stop_lat, stop_lng = get_nearest_station(lat, lng)
        sunrise, sunset = sun_time(lat, lng)
        weather_desc, temperature = weather_check(lat, lng)

        return render_template('index.html',
            mapbox_token=MAPBOX_TOKEN,
            user_place=place,
            user_lat=lat, user_lng=lng,
            stop_name=station_name,
            accessible="Yes" if accessible else "No",
            stop_lat=stop_lat, stop_lng=stop_lng,
            sunrise=sunrise,
            sunset=sunset,
            weather_desc=weather_desc,
            temperature=temperature
        )
    return render_template('index.html', mapbox_token=MAPBOX_TOKEN)

if __name__ == '__main__':
    app.run(debug=True)
