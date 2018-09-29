import argparse
from collections import defaultdict

from lib import *

parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('--fr', type=str,
                    help='From file')

parser.add_argument('--to', type=str,
                    help='to file')

parser.add_argument('--provider', type=str,
                    help='Provider of source data')

parser.add_argument('--cat', type=str,
                    help='Type of source data')

args = parser.parse_args()

categories = defaultdict(list)

if args.provider == 'google':

    raw_places = json.load(open(args.fr))
    for place in raw_places:
        place_ready = {
            "name": place["name"],
            "location": place["geometry"]["location"]
        }
        for cat in place["types"]:
            categories[cat].append(place_ready)
elif args.provider == 'mos':

    raw_places = json.load(open(args.fr, encoding='cp1251'))
    assert args.cat is not None
    for place in raw_places:
        if args.cat == 'park':
            name = place['CommonName']
            loc = place['geoData']["center"][0]
        elif args.cat == 'market':
            name = place['Name']
            loc = place['geoData']['coordinates']
        place_ready = {
            "name": name,
            "location": {
                'lat': loc[1],
                'lng': loc[0]
            }
        }
        categories[args.cat].append(place_ready)
else:
    raise NotImplementedError

with open("data/%s" % args.to, 'w') as f:
    f.write(pretty_json(categories))
