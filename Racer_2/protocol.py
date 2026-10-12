import json

PORT = 5005
WIDTH = 700
HEIGHT = 800
ROAD_X = 100
ROAD_W = 500
CAR_W = 48
CAR_H = 88
PLAYER_Y = 680
MAX_LIVES = 3


def encode(msg):
    return (json.dumps(msg) + "\n").encode("utf-8")


def decode(data):
    return json.loads(data.decode("utf-8"))