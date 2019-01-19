import argparse
import os
from collections import defaultdict, Counter
import re
from lib import *
import pymongo
from process import connector

from pymongo import MongoClient

parser = argparse.ArgumentParser(description='tbd')

db = connector.get_db()


def insert_all(cats):
    collection = db.categories
    collection.insert_many(cats)


categories = defaultdict(lambda: {
    "brands": [],
    "additional_fields": defaultdict(list)
})

places = db.places

for place in places.find():
    for cat in place["categories"]:
        categories[cat]["brands"].append(place['brand'])
        for field_name, value in place["additional_fields"].items():
            categories[cat]["additional_fields"][field_name].append(value)

for cat, value in categories.items():
    value["name"] = cat

insert_all(categories.values())