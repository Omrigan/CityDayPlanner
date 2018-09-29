import json
from collections import defaultdict

import geopy.distance
import numpy as np


def dist(x, y):
    return geopy.distance.vincenty((x['lat'], x['lng']), (y['lat'], y['lng'])).meters


fake = True


def calculate_distances(src_list, target_list):
    result = [[dist(s['location'], t['location']) for t in target_list] for s in src_list]
    return np.asarray(result)


def squash_distances(matrix1, matrix2):
    dists = np.zeros((matrix1.shape[0], matrix2.shape[1]), dtype=float)
    answers = np.zeros((matrix1.shape[0], matrix2.shape[1]), dtype=int)
    for i in range(dists.shape[0]):
        for j in range(dists.shape[1]):
            vector = matrix1[i] + matrix2[:, j]
            answers[i, j] = vector.argmin()
            dists[i, j] = vector[answers[i, j]]
    return dists, answers


DATABASE_FILES = [
    "data/google-small.json",
    "data/mos-markets.json",
    "data/mos-parks.json",
]
database = defaultdict(list)
for file in DATABASE_FILES:
    data = json.load(open(file))
    for key, value in data.items():
        database[key].extend(value)


def get_canidates(event):
    type = event.get('type')
    if type == 'fixed_place':
        return [event]
    brand = event.get('brand')
    result = []
    for data in database[type]:
        conds = []
        if brand:
            conds.append(data.get('brand') == brand)
        if all(conds):
            result.append(data)
    return result


class PredictJob():

    def __init__(self, ordered_events, unordered_events):
        self.ordered_events = ordered_events
        self.unordered_events = unordered_events

    def predict(self):
        self.answers = []
        self.stages = [get_canidates(self.ordered_events[0])]
        self.current_dists = None
        for event in self.ordered_events[1:]:
            self.stages.append(get_canidates(event))
            dists = calculate_distances(self.stages[-2], self.stages[-1])
            if self.current_dists is not None:
                self.current_dists, answer = squash_distances(self.current_dists, dists)
                self.answers.append(answer)
            else:
                self.current_dists = dists
        self.recover_route()

    def recover_route(self):
        # print(self.answers)

        def myargmin(x):
            return np.unravel_index(np.argmin(x, axis=None), x.shape)

        start, end = myargmin(self.current_dists)
        self.resulting_distance = np.min(self.current_dists)
        rev_route = [end]
        current_point = end
        for answer in reversed(self.answers):
            current_point = answer[start, current_point]
            rev_route.append(current_point)
        rev_route.append(start)
        self.route = []
        for (i, point_id) in enumerate(reversed(rev_route)):
            self.route.append(self.stages[i][point_id])

    def describe(self):
        return {
            "route": self.route,
            "resulting_dist": self.resulting_distance
        }
