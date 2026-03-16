import os
from main import app, RESULTS_DIR
from flask import jsonify

@app.route("/api/scores")
def scores():
    totals = {}

    for file in os.listdir(RESULTS_DIR):
        path = os.path.join(RESULTS_DIR, file)

        if os.path.isfile(path):
            with open(path) as f:
                for line in f:
                    if "=" in line:
                        team, score = line.strip().split("=")
                        score = int(score)

                        totals[team] = totals.get(team, 0) + score

    return jsonify(totals)


@app.route("/api/score-history")
def score_history():

    rounds = sorted(
        [f for f in os.listdir(RESULTS_DIR) if f.endswith(".log")],
        key=lambda x: int(x.split(".")[0])
    )

    data = {}
    round_numbers = []

    for file in rounds:

        round_number = int(file.split(".")[0])
        round_numbers.append(round_number)

        path = os.path.join(RESULTS_DIR, file)

        with open(path) as f:
            for line in f:
                if "=" in line:
                    team, score = line.strip().split("=")
                    score = int(score)

                    if team not in data:
                        data[team] = []

                    data[team].append(score)

    return jsonify({
        "rounds": round_numbers,
        "teams": data
    })
