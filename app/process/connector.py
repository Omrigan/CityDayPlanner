import argparse
import os
from collections import defaultdict, Counter
import re
from lib import *
import pymongo

from pymongo import MongoClient


def get_db():
    client = MongoClient('mongo', 27017)
    db = client.cityday
    return db



if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Import process.')
    parser.add_argument("command")

    args = parser.parse_args()

    db = get_db()
    if args.command=='clear':
        db.places.delete_many({})
        db.categories.delete_many({})
        print("Cleared")
