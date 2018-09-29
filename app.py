from flask import Flask
from flask import request, jsonify

from logic import PredictJob

app = Flask(__name__)


@app.route('/predict', methods=["POST"])
def predict():
    data = request.get_json()
    print()
    ordered_events = data.get("ordered_events")
    unordered_events = data.get("unordered_events")
    job = PredictJob(ordered_events, unordered_events)
    job.predict()
    return jsonify(job.describe())
