import os
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timedelta

import geopy.distance
import numpy as np

import osm_connector
import json


def dist(x, y):
    return geopy.distance.vincenty((x['lat'], x['lng']), (y['lat'], y['lng'])).meters


CLIPPING = int(os.getenv('CLIPPING'))
DISTS = os.getenv('DISTS')


def calculate_distances(src_list, target_list):
    # print(DISTS, len(src_list), len(target_list))

    if DISTS == 'dummy':
        result = [[dist(s['location'], t['location']) for t in target_list] for s in src_list]
    elif DISTS == 'osm':
        result = osm_connector.calcualte_distances("car", src_list, target_list)

    return np.asarray(result)


def squash_distances(matrix1, matrix2):
    # print("Squashing", matrix1.shape, matrix2.shape)
    dists = np.zeros((matrix1.shape[0], matrix2.shape[1]), dtype=float)
    answers = np.zeros((matrix1.shape[0], matrix2.shape[1]), dtype=int)
    for i in range(dists.shape[0]):
        for j in range(dists.shape[1]):
            vector = matrix1[i] + matrix2[:, j]
            answers[i, j] = vector.argmin()
            dists[i, j] = vector[answers[i, j]]
    return dists, answers


DATABASE_FILES = [
    "../data/google-small.json",
    "../data/mos-markets.json",
    "../data/mos-parks.json",
    "../data/osm-all.json",
]
database = defaultdict(list)
for file in DATABASE_FILES:
    data = json.load(open(file))
    for key, value in data.items():
        database[key].extend(value)


# print(database['cafe'])
# print(database['park'])


class PredictJob():

    def get_free_time(self, duration, start_time):
        return {'type': 'free_time',
                'delay': duration,
                'start_time': start_time,
                'finish_time': start_time + duration}

    def normalize_dates(self, place):

        if 'start_time' in place:
            place['start_time'] = self.ptime(place['start_time'])

        if 'finish_time' in place:
            place['finish_time'] = self.ptime(place['finish_time'])

        if 'delay' in place:
            place['delay'] = self.pdelay(place['delay'])
        else:
            place['delay'] = timedelta(minutes=0)
        if 'start_time' in place and 'finish_time' in place:
            place['delay'] = place['finish_time'] - place['start_time']
        elif 'start_time' in place:
            place['finish_time'] = place['start_time'] + place['delay']
        elif 'finish_time' in place:
            place['start_time'] = place['finish_time'] - place['delay']
        return place

    def __init__(self, ordered_events, unordered_events):
        self.ordered_events = ordered_events
        self.unordered_events = unordered_events
        self.route = [{'event': x} for x in self.ordered_events]
        self.warnings = []

    def get_canidates(self, event):
        type = event.get('type')
        if type == 'fixed_place':
            return [event]
        brand = event.get('brand')
        result = []
        for data in database[type]:
            conds = [True]
            if brand is not None:
                conds.append(data.get('brand') == brand)
            if all(conds):
                result.append(data)
        if len(result) == 0:
            raise Exception("No places with this type %s" % event)
        return deepcopy(result[:CLIPPING])

    def predict(self):
        self.answers = []
        self.all_dists = []
        self.stage_candidates = [self.get_canidates(self.ordered_events[0])]
        self.current_dists = None
        for event in self.ordered_events[1:]:
            self.stage_candidates.append(self.get_canidates(event))
            dists = calculate_distances(self.stage_candidates[-2], self.stage_candidates[-1])
            self.all_dists.append(dists)
            if self.current_dists is not None:
                self.current_dists, answer = squash_distances(self.current_dists, dists)
                self.answers.append(answer)
            else:
                self.current_dists = dists
        self.recover_route()

    def preprocess_item(self, item, event):
        item.update(event)
        data = self.normalize_dates(item)
        return data

    def recover_route(self):
        # print(self.answers)

        def myargmin(x):
            return np.unravel_index(np.argmin(x, axis=None), x.shape)

        start, end = myargmin(self.current_dists)
        self.resulting_distance = np.min(self.current_dists)
        rev_route = [end]
        current_point = end
        rev_dists = []
        for dists, answer in reversed(list(zip(self.all_dists[1:], self.answers))):
            next_point = current_point
            current_point = answer[start, current_point]
            rev_route.append(current_point)
            rev_dists.append(dists[current_point, next_point])
        rev_route.append(start)
        rev_dists.append(float(self.all_dists[-1][start, current_point]))
        self.route_dists = list(reversed(rev_dists))
        # print("Dists", self.route_dists)
        for (i, point_id) in enumerate(reversed(rev_route)):
            self.route[i] = self.preprocess_item(self.stage_candidates[i][point_id], self.ordered_events[i])
        self.enrich_route()

    def ptime(self, st):

        return datetime.strptime(st, "%H:%M")

    def ftime(self, dt):
        if type(dt) == str:
            return dt
        return dt.strftime("%H:%M")

    @staticmethod
    def pdelay(mins):
        return timedelta(minutes=int(mins or 0))

    @staticmethod
    def fdelay(delay):
        return delay.seconds / 60

    def get_time(self, start_idx):
        if DISTS == 'dummy1':
            return timedelta(minutes=40)
        else:
            # print(self.route_dists[start_idx])
            return timedelta(minutes=self.route_dists[start_idx])

    def get_move(self, ind, cuurent_time):
        delay = self.get_time(ind - 1)

        return {'location_from': self.route[ind - 1]['location'],
                'location_to': self.route[ind]['location'],
                'start_time': cuurent_time,
                'finish_time': cuurent_time + delay,
                'type': 'move',
                'delay': delay}

    def enrich_route(self):
        current_time = self.route[0].get('finish_time')
        if not current_time:
            self.warnings.append("Starttime was not specified!")
            current_time = datetime.now()
        new_route = [self.route[0]]
        for i in range(1, len(self.route)):
            new_route.append(self.get_move(i, current_time))
            current_time += new_route[-1]['delay']
            cur_item = self.route[i]
            # print(cur_item)
            if cur_item.get('start_time'):
                if current_time < cur_item['start_time']:
                    new_route.append(self.get_free_time(cur_item['start_time'] -
                                                        current_time, current_time))
                elif current_time > cur_item['start_time']:
                    self.warnings.append("For place '%s' you will late %s miuntes" % (
                        cur_item['name'],
                        ((cur_item['start_time'] - current_time).seconds / 60) % 1440
                    ))
            else:
                cur_item['start_time'] = current_time
            current_time += cur_item.get('delay')
            if 'finish_time' not in cur_item:
                cur_item['finish_time'] = current_time
            new_route.append(cur_item)
        self.route = new_route

    def describe_place(self, item):
        # print(item)

        item = deepcopy(item)
        item['start_time'] = self.ftime(item['start_time'])
        item['finish_time'] = self.ftime(item['finish_time'])
        item['delay'] = item['delay'].seconds / 60
        return item

    def describe(self):

        return {
            "route": [self.describe_place(place) for place in self.route],
            "resulting_dist": self.resulting_distance,
            "warnings": self.warnings
        }
