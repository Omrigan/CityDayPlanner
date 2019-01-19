import requests

from lib import pretty_json, moscow_location
import os
GMAPS_TOKEN = os.getenv("GMAPS_MAIN_TOKEN")
# gmaps = googlemaps.Client(key=GMAPS_TOKEN)

def make_request(method, params):
    params.update({"key": GMAPS_TOKEN, 'language': 'ru'})
    res = requests.get("https://maps.googleapis.com/maps/api/%s/json" % method, params)
    return res.json()


def get_data_by_keyword(keyword):
    places = make_request('place/nearbysearch', {
        "location": moscow_location,
        "radius": 1000,
        "keyword": keyword
    })
    return places["results"]


if __name__=="__main__":
    all_places = []
    for k in ["park", "restaurant"]:
        all_places.extend(get_data_by_keyword(k))

    with open('google_data/small_raw.json', 'w') as f:
        f.write(pretty_json(all_places))
