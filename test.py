from unittest import TestCase
from requests import post, get

from lib import pretty_json

URI = "http://127.0.0.1:5000/predict"
sample_request = {
            "ordered_events": [
                {"type": "fixed_place",
                 "location": {'lat': 55.7494539, 'lng': 37.62160470000001, },
                 "finish_time": "15:00"},
                {"type": "cafe",
                 "brand": "даблби",
                 "delay": 15},
                {"type": "park",
                 "delay": 60},
                {"type": "restaurant",
                 "delay": 20},
                {"type": "fixed_place",
                 "start_time": "23:00",
                 "location": {'lat': 55.7494539, 'lng': 37.62160470000001, },
                 }
            ],
            "unordered_events": []
        }
class TC(TestCase):
    def test(self):

        resp = post(URI, json=sample_request)
        #print(resp)
        #print(pretty_json(resp.json()))

    def test_params(self):
        pass
        resp = get("http://127.0.0.1:5000/get_params")
        #print(resp.json())


