import argparse
import os
from collections import defaultdict, Counter

from lib import *
from process import connector

parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('--fr', type=str,
                    help='From file')

parser.add_argument('--to', type=str,
                    help='to file')


parser.add_argument('--mongo', action='store_true', default=False,
                    help='Output to mongo')

parser.add_argument('--provider', type=str,
                    help='Provider of source process')

parser.add_argument('--cat', type=str,
                    help='Type of source process')
parser.add_argument('--upsert_brands', action='store_true', default=False)

args = parser.parse_args()

categories = defaultdict(list)

BRANDS_PATH = 'process/brands.json'
brands = defaultdict(Counter)
if args.upsert_brands and os.path.isfile(BRANDS_PATH):
    brands_old = json.load(open(BRANDS_PATH))
    for cat, items in brands_old.items():
        for key, value in items.items():
            brands[cat][key] = value

ADDITIONAL_PATH = 'process/additional.json'

additional_fields = defaultdict(lambda: defaultdict(set))

if os.path.isfile(ADDITIONAL_PATH):
    additional_fields_old = json.load(open(ADDITIONAL_PATH))
    for cat in additional_fields_old:
        for option in additional_fields_old[cat]:
            additional_fields[cat][option] = set(additional_fields_old[cat][option])

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
            "brand": get_brand(place["name"])
        }
        for cat in place["types"]:
            categories[cat].append(place_ready)
elif args.provider == 'mos':

    raw_places = json.load(open(args.fr, encoding='cp1251'))
    assert args.cat is not None
    cat = args.cat
    for place in raw_places:
        if args.cat == 'park':
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
                "brand": get_brand(name)
            }
            for field in fields_list:
                additional_fields[cat][field].add(place.get(field))
                place_ready[field] = place.get(field)

            # print(pretty_json(place))

        elif args.cat == 'market':
            name = place.get('Name')
            loc = place['geoData']['coordinates']

            market_type = place.get("MarketType")
            additional_fields[args.cat]["market_type"].add(market_type)

            place_ready = {
                "name": name,
                "market_type": market_type,
                "location": {
                    'lng': loc[0],
                    'lat': loc[1]
                },
                "brand": get_brand(name)
            }
        categories[args.cat].append(place_ready)
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
            place_ready = dict(tags)
            place_ready.update({
                "location": loc,
                "brand": get_brand(tags["name"])
            })
            if 'brand' in tags:
                place_ready["original_brand"] = tags['brand']
            added = False
            for predicate, cat in mapping.items():

                if tags.get(predicate[0]) == predicate[1]:
                    # if predicate[1] == 'cafe':
                    #     print(place_ready)
                    categories[cat].append(place_ready)
                    added = True
            if not added:
                categories["other"].append(place_ready)

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

for cat, items in categories.items():
    for item in items:
        brands[cat][item['brand']] += 1
with open(BRANDS_PATH, 'w') as f:
    f.write(pretty_json(brands))
if args.mongo:
    collection = connector.get_db().places
    collection.insert_many([categories])
else:
    with open("process/%s" % args.to, 'w') as f:
        f.write(pretty_json(categories))

for cat in additional_fields:
    for option in additional_fields[cat]:
        additional_fields[cat][option] = list(additional_fields[cat][option])
with open(ADDITIONAL_PATH, 'w') as f:
    f.write(pretty_json(additional_fields))
