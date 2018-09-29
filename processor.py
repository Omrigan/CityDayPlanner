from collections import defaultdict

from lib import *

raw_places = json.load(open('parsed_data/small_raw.json'))
categories = defaultdict(list)

for place in raw_places:
    place_ready = {
        "name": place["name"],
        "location": place["geometry"]["location"]
    }
    for cat in place["types"]:
        categories[cat].append(place_ready)
with open('data/small.json', 'w') as f:
    f.write(pretty_json(categories))
