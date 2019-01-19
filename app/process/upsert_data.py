import argparse
import os
from collections import defaultdict, Counter
import re
from lib import *
from process import connector
import pymongo

from pymongo import MongoClient

parser = argparse.ArgumentParser(description='Import process.')

parser.add_argument('--fr', type=str,
                    help='From file', required=True)

parser.add_argument('--provider', type=str,
                    help='Provider of source process', required=True)

args = parser.parse_args()

expr = re.compile("(\s+|-)")

def get_brand(name):
    if not name:
        return None
    return re.sub(expr, " ", name.lower())

def insert_all(places):
    client = MongoClient('localhost', 27017)
    db = client.cityday
    collection = db.places
    collection.insert_many(places)




all_places = []

if args.provider == 'google':
    raw_places = json.load(open(args.fr))
    for place in raw_places:
        place_ready = {
            "name": place["name"],
            "location": place["geometry"]["location"],
            "brand": get_brand(place["name"]),
            "categories": place["types"]
        }
        all_places.append(place_ready)

