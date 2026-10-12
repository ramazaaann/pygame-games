import math
import random
from protocol import (ROAD_X, ROAD_W, CAR_W, CAR_H, PLAYER_Y, MAX_LIVES)

SIZES = {"E": (48, 88), "O": (40, 40), "C": (26, 26), "P": (34, 34)}
POWERUPS = ["nitro", "shield", "repair", "oil"]
LATERAL_SPEED = 420

def overlap(a, b):
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]

class World:
    def __init__(self, names):
        self.t = 0.0
        self.entities = []
        self.players = {}
        for slot, name in sorted(names.items()):
            x = ROAD_X + 110 if slot == 0 else ROAD_X + ROAD_W - 110 - CAR_W
            self.players[slot] = {
                "name": name, "x": float(x), "lives": MAX_LIVES, "coins": 0, "dist": 0.0,
                "shield": False, "nitro": 0.0, "inv": 0.0, "alive": True, "spin": 0.0,
            }

    @property
    def world_speed(self):
        return min(320 + self.t * 2.8, 680)

    def score(self, p):
        return int(p["dist"]) + p["coins"] * 5

    def _spawn(self, kind):
        w, h = SIZES[kind]
        for _ in range(10):
            x = random.uniform(ROAD_X + 30, ROAD_X + ROAD_W - w - 30)
            y = random.uniform(-400, -h - 50)
            zone = (x - 30, y - 30, w + 60, h + 60)
            if any(overlap(zone, (e["x"], e["y"], e["w"], e["h"])) for e in self.entities):
                continue
            ent = {"k": kind, "x": x, "y": y, "w": w, "h": h, "m": 1.0, "v": 0}
            if kind == "E":
                ent["m"] = random.uniform(0.7, 1.1)
                ent["v"] = random.randint(0, 2)
            elif kind == "C":
                ent["v"] = random.choice([1, 2, 3])
            elif kind == "P":
                ent["v"] = random.choice(POWERUPS)
            self.entities.append(ent)
            return

    def _top_up(self):
        count = {"E": 0, "O": 0, "C": 0, "P": 0}
        for e in self.entities:
            count[e["k"]] += 1
        targets = {"E": min(2 + int(self.t // 25), 6), "O": 2, "C": 3}
        for kind, target in targets.items():
            if count[kind] < target:
                self._spawn(kind)
        if count["P"] == 0 and random.random() < 0.018:
            self._spawn("P")

    def _apply_powerup(self, p, kind):
        if kind == "nitro":
            p["nitro"] = 5.0
        elif kind == "shield":
            p["shield"] = True
        elif kind == "repair":
            p["lives"] = min(MAX_LIVES, p["lives"] + 1)
        elif kind == "oil":
            p["spin"] = 1.3

    def step(self, dt, inputs):
        self.t += dt
        ws = self.world_speed

        for e in self.entities:
            e["y"] += ws * e["m"] * dt
        self.entities = [e for e in self.entities if e["y"] < 850]
        self._top_up()

        for slot, p in self.players.items():
            if not p["alive"]:
                continue
            controls = inputs.get(slot, {"l": False, "r": False, "turbo": False})
            left, right, turbo = controls.get("l"), controls.get("r"), controls.get("turbo")
            
            if p["spin"] > 0:
                p["spin"] = max(0.0, p["spin"] - dt)
                left, right = right, left

            speed_multiplier = 1.9 if (turbo or p["nitro"] > 0) else 1.0
            speed = LATERAL_SPEED * speed_multiplier
            
            p["x"] += (int(right) - int(left)) * speed * dt
            p["x"] = max(ROAD_X + 15, min(ROAD_X + ROAD_W - CAR_W - 15, p["x"]))
            p["dist"] += ws * dt * 0.02 * speed_multiplier
            p["nitro"] = max(0.0, p["nitro"] - dt)
            p["inv"] = max(0.0, p["inv"] - dt)

            box = (p["x"], PLAYER_Y, CAR_W, CAR_H)
            remaining = []
            for e in self.entities:
                if not overlap(box, (e["x"], e["y"], e["w"], e["h"])):
                    remaining.append(e)
                    continue
                if e["k"] == "C":
                    p["coins"] += e["v"]
                elif e["k"] == "P":
                    self._apply_powerup(p, e["v"])
                elif p["inv"] > 0:
                    remaining.append(e)  
                elif p["shield"]:
                    p["shield"] = False
                    p["inv"] = 1.0
                else:
                    p["lives"] -= 1
                    p["inv"] = 1.5
                    if p["lives"] <= 0:
                        p["alive"] = False
            self.entities = remaining

    def kill(self, slot):
        if slot in self.players:
            self.players[slot]["alive"] = False

    def finished(self):
        alive = [p for p in self.players.values() if p["alive"]]
        return len(alive) == 0

    def snapshot(self):
        return {
            "t": "state",
            "ws": round(self.world_speed),
            "curve": 0.0,
            "e": [[e["k"], int(e["x"]), int(e["y"]), e["w"], e["h"], e["v"], round(self.world_speed * e["m"])]
                  for e in self.entities],
            "p": [{"s": s, "n": p["name"], "x": int(p["x"]), "l": p["lives"], "sc": self.score(p),
                   "c": p["coins"], "sh": int(p["shield"]), "nt": round(p["nitro"], 1),
                   "iv": int(p["inv"] > 0), "a": int(p["alive"]), "sp": int(p["spin"] > 0)}
                  for s, p in sorted(self.players.items())],
        }

    def results(self):
        out = []
        for s, p in sorted(self.players.items()):
            out.append({"slot": s, "name": p["name"], "score": self.score(p),
                        "coins": p["coins"], "distance": int(p["dist"])})
        return out