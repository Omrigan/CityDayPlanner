import json

from lib import *

import requests

from settings import GMAPS_TOKEN





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


all_places = []
for k in ["park", "restaurant"]:
    all_places.extend(get_data_by_keyword(k))

with open('parsed_data/small_raw.json', 'w') as f:
    f.write(pretty_json(all_places))
