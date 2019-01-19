import argparse

from process import connector
from lib import *

parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('--fr', type=str,
                    help='From file')

parser.add_argument('--provider', type=str,
                    help='Provider of source process')

parser.add_argument('--type', type=str,
                    help='Type of source places')

parser.add_argument('--prune_data', action='store_true', default=False)

parser.add_argument('--upsert_brands', action='store_true', default=False)

args = parser.parse_args()

collection = connector.get_db().places
if args.prune_data:
    collection.drop()

import re

expr = re.compile("(\s+|-)")


def get_brand(name):
    if not name:
        return None
    return re.sub(expr, " ", name.lower())


if args.provider == 'google':

    raw_places = json.load(open(args.fr))
    for place in raw_places:
        place_ready = {
            "name": place["name"],
            "location": place["geometry"]["location"],
            "brand": get_brand(place["name"]),
            "types": place["types"]
        }
        collection.insert_one(place_ready)
elif args.provider == 'mos':

    raw_places = json.load(open(args.fr, encoding='cp1251'))
    assert args.type is not None
    cat = args.type
    for place in raw_places:
        if args.type == 'park':
            name = place['CommonName']
            loc = place['geoData']["center"][0]
            description = place.get("Location")
            fields_list = ["HasPlayground",
                           "HasSportground",
                           "HasWater",
                           "NeighbourhoodPark"]
            place_ready = {
                "name": name,
                "description": description,
                "location": {
                    'lng': loc[0],
                    'lat': loc[1]
                },
                "brand": get_brand(name),
                "types": [args.type]
            }
            for field in fields_list:
                place_ready[field] = place.get(field)

            # print(pretty_json(place))

        elif args.type == 'market':
            name = place.get('Name')
            loc = place['geoData']['coordinates']

            market_type = place.get("MarketType")

            place_ready = {
                "name": name,
                "market_type": market_type,
                "location": {
                    'lng': loc[0],
                    'lat': loc[1]
                },
                "brand": get_brand(name),
                "types": [args.type]
            }
        collection.insert_one(place_ready)
elif args.provider == 'osm':
    # from lxml import etree
    # et = etree.ElementTree

    import xml.etree.ElementTree as et

    mapping = {
        ('amenity', 'cafe'): 'cafe',
        ('amenity', 'fast_food'): 'fastfood',
        ('amenity', 'food_court'): 'fastfood',
        ('amenity', 'bar'): 'bar',
        ('amenity', 'pub'): 'bar',
        ('amenity', 'restaurant'): 'restaurant',
        ('amenity', 'atm'): 'atm',
        ('amenity', 'bank'): 'bank',
        ('shop', 'supermarket'): 'supermarket',
        ('shop', 'wholesale'): 'supermarket',
        ('shop', 'convenience'): 'supermarket',

    }
    e = et.parse(args.fr).getroot()
    for n in e.iter('node'):
        loc = {'lat': n.attrib['lat'], 'lng': n.attrib['lon']}
        tags = {}
        for tag in n:
            tags[tag.attrib['k']] = tag.attrib['v']

        if 'name' in tags:
            # print(tags)
            place_ready = {
                "name": tags["name"],
                "location": loc,
                "brand": get_brand(tags["name"]),
                "meta": tags,
                "types": []
            }
            if 'brand' in tags:
                place_ready["original_brand"] = tags['brand']
            added = False
            for predicate, type in mapping.items():

                if tags.get(predicate[0]) == predicate[1]:
                    place_ready["types"].append(type)
                    added = True
            if not added:
                place_ready["types"].append("other")
            collection.insert_one(place_ready)
else:
    raise NotImplementedError

# elif args.provider == 'osm-imposm':
#     def nodes_callback(nodes):
#         for idx, tags, loc in nodes:
#             cat = tags.values()[0]
#             place_ready = {
#                 "name": tags["name"],
#                 "location": {
#                     'lng': loc[0],
#                     'lat': loc[1]
#                 }
#             }
#             categories[cat].append(place_ready)

# p = OSMParser(concurrency=4, ways_callback=counter.ways)
# p.parse(args.fr)

# with open(BRANDS_PATH, 'w') as f:
#     f.write(pretty_json(brands))
