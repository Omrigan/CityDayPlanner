import json

from flask import Flask, render_template
from flask import request, jsonify

from logic import PredictJob, database
from lib import pretty_json

app = Flask(__name__)


@app.route('/predict', methods=["POST"])
def predict():
    data = request.get_json()

    ordered_events = data.get("ordered_events")
    unordered_events = data.get("unordered_events")
    job = PredictJob(ordered_events, unordered_events)
    job.predict()
    return jsonify(job.describe())


@app.route('/get_params', methods=["GET"])
def get_params():
    additional = json.load(open('process/additional.json'))
    brands = json.load(open('process/brands.json'))
    filtered_brands = {}
    for type in brands:
        for value, cnt in brands[type].items():
            if cnt > 1:
                if type not in filtered_brands:
                    filtered_brands[type] = [value]
                else:
                    filtered_brands[type].append(value)
    for type in filtered_brands:
        filtered_brands[type] = [x.title() for x in sorted(filtered_brands[type],
                                                           key=lambda x: brands[type][x], reverse=True)]
    del filtered_brands['other']
    return jsonify({
        "options": additional,
        "brands": filtered_brands,
        "types": list(database.keys())
    })


from gapi import main


@app.route("/")
def predict_gcal():
    task = main()

    ordered_events = task.get("ordered_events")
    unordered_events = task.get("unordered_events")
    job = PredictJob(ordered_events, unordered_events)
    job.predict()
    #job.describe()
    print("Describe", pretty_json(job.describe()))
    return render_template('predict_gcal.html', params=job.describe())
