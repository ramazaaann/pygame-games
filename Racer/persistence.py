import json
import os

SETTINGS_FILE = "settings.json"
LEADERBOARD_FILE = "leaderboard.json"


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {
            "sound": True,
            "car_color": "blue",
            "difficulty": "normal"
        }

    with open(SETTINGS_FILE, "r") as file:
        return json.load(file)


def save_settings(settings):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file, indent=4)


def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []

    with open(LEADERBOARD_FILE, "r") as file:
        return json.load(file)


def save_score(name, score, coins, distance):
    leaderboard = load_leaderboard()

    leaderboard.append({
        "name": name,
        "score": score,
        "coins": coins,
        "distance": distance
    })

    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    leaderboard = leaderboard[:10]

    with open(LEADERBOARD_FILE, "w") as file:
        json.dump(leaderboard, file, indent=4)