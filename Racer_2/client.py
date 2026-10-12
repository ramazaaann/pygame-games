import pygame
import random
import sys
import math
from protocol import WIDTH, HEIGHT, ROAD_X, ROAD_W, CAR_W, CAR_H, PLAYER_Y, MAX_LIVES
import db

WHITE, BLACK, GRAY = (255, 255, 255), (0, 0, 0), (100, 100, 100)
DARK_GRAY, GREEN = (20, 20, 25), (10, 80, 30)
FERRARI_RED = (225, 29, 42)    
PORSCHE_SILVER = (200, 210, 225) 
YELLOW, CYAN, ORANGE, BLUE = (255, 215, 0), (0, 229, 255), (255, 140, 0), (30, 144, 255)
POWER_STYLE = {"nitro": (CYAN, "N"), "shield": (BLUE, "S"), "repair": (GREEN, "R"), "oil": (ORANGE, "O")}

class App:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Ferrari vs Porsche - Local 2P")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.small = pygame.font.SysFont("Arial", 16)
        self.big = pygame.font.SysFont("Arial", 38, bold=True)
        self.huge = pygame.font.SysFont("Arial", 90, bold=True)

        self.mode = "menu"
        self.p1_name = "Ferrari"
        self.p2_name = "Porsche"
        self.active_field = 0
        self.show_leaderboard = False
        
        db.init()
        self.reset_game()

    def reset_game(self):
        self.t = 0.0
        self.entities = []
        self.road_offset = 0.0
        self.rain = [{"x": random.randint(ROAD_X, ROAD_X + ROAD_W), "y": random.randint(0, HEIGHT), "v": random.randint(14, 22)} for _ in range(60)]
        
        self.p1 = {
            "name": self.p1_name, "x": float(ROAD_X + 90), "y": float(PLAYER_Y),
            "lives": MAX_LIVES, "coins": 0, "dist": 0.0,
            "shield": False, "nitro": 0.0, "inv": 0.0, "alive": True, "spin": 0.0
        }
        self.p2 = {
            "name": self.p2_name, "x": float(ROAD_X + ROAD_W - 90 - CAR_W), "y": float(PLAYER_Y),
            "lives": MAX_LIVES, "coins": 0, "dist": 0.0,
            "shield": False, "nitro": 0.0, "inv": 0.0, "alive": True, "spin": 0.0
        }
        self.countdown_timer = 3.0

    @property
    def world_speed(self):
        return min(320 + self.t * 2.8, 680)

    def text(self, s, font, color, x, y, center=False):
        img = font.render(s, True, color)
        rect = img.get_rect(center=(x, y)) if center else img.get_rect(topleft=(x, y))
        self.screen.blit(img, rect)

    def overlap(self, a, b):
        return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]

    def spawn(self, kind):
        sizes = {"E": (48, 88), "O": (40, 40), "C": (26, 26), "P": (34, 34)}
        w, h = sizes[kind]
        for _ in range(10):
            x = random.uniform(ROAD_X + 30, ROAD_X + ROAD_W - w - 30)
            y = random.uniform(-400, -h - 50)
            zone = (x - 30, y - 30, w + 60, h + 60)
            if any(self.overlap(zone, (e["x"], e["y"], e["w"], e["h"])) for e in self.entities):
                continue
            ent = {"k": kind, "x": x, "y": y, "w": w, "h": h, "m": 1.0, "v": 0}
            if kind == "E":
                ent["m"] = random.uniform(0.7, 1.1)
                ent["v"] = random.randint(0, 2)
            elif kind == "C":
                ent["v"] = random.choice([1, 2, 3])
            elif kind == "P":
                ent["v"] = random.choice(["nitro", "shield", "repair", "oil"])
            self.entities.append(ent)
            return

    def update_simulation(self, dt):
        self.t += dt
        ws = self.world_speed

        for e in self.entities:
            e["y"] += ws * e["m"] * dt
        self.entities = [e for e in self.entities if e["y"] < 850]

        count = {"E": 0, "O": 0, "C": 0, "P": 0}
        for e in self.entities:
            count[e["k"]] += 1
        targets = {"E": min(2 + int(self.t // 25), 6), "O": 2, "C": 3}
        for kind, target in targets.items():
            if count[kind] < target:
                self.spawn(kind)
        if count["P"] == 0 and random.random() < 0.018:
            self.spawn("P")

        keys = pygame.key.get_pressed()
        p1_l = keys[pygame.K_a]
        p1_r = keys[pygame.K_d]
        p1_t = keys[pygame.K_w]

        p2_l = keys[pygame.K_LEFT]
        p2_r = keys[pygame.K_RIGHT]
        p2_t = keys[pygame.K_UP]

        for p, (l, r, turbo) in [(self.p1, (p1_l, p1_r, p1_t)), (self.p2, (p2_l, p2_r, p2_t))]:
            if not p["alive"]:
                continue
            if p["spin"] > 0:
                p["spin"] = max(0.0, p["spin"] - dt)
                l, r = r, l

            speed_mult = 1.9 if (turbo or p["nitro"] > 0) else 1.0
            speed = 420 * speed_mult
            
            p["x"] += (int(r) - int(l)) * speed * dt
            p["x"] = max(ROAD_X + 15, min(ROAD_X + ROAD_W - CAR_W - 15, p["x"]))
            p["dist"] += ws * dt * 0.02 * speed_mult
            p["nitro"] = max(0.0, p["nitro"] - dt)
            p["inv"] = max(0.0, p["inv"] - dt)

            box = (p["x"], PLAYER_Y, CAR_W, CAR_H)
            remaining = []
            for e in self.entities:
                if not self.overlap(box, (e["x"], e["y"], e["w"], e["h"])):
                    remaining.append(e)
                    continue
                if e["k"] == "C":
                    p["coins"] += e["v"]
                elif e["k"] == "P":
                    kind = e["v"]
                    if kind == "nitro": p["nitro"] = 5.0
                    elif kind == "shield": p["shield"] = True
                    elif kind == "repair": p["lives"] = min(MAX_LIVES, p["lives"] + 1)
                    elif kind == "oil": p["spin"] = 1.3
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

        if not self.p1["alive"] and not self.p2["alive"]:
            self.mode = "over"
            res = [
                {"name": self.p1["name"], "score": int(self.p1["dist"]) + self.p1["coins"] * 5, "coins": self.p1["coins"], "distance": int(self.p1["dist"])},
                {"name": self.p2["name"], "score": int(self.p2["dist"]) + self.p2["coins"] * 5, "coins": self.p2["coins"], "distance": int(self.p2["dist"])}
            ]
            winner = max(res, key=lambda x: x["score"])["name"]
            db.save_match(res, self.t, winner)
            self.over_results = res
            self.winner_name = winner

    def draw_road(self):
        self.screen.fill((10, 10, 15))
        self.road_offset = (self.road_offset + self.world_speed * 0.016) % 80
        
        pygame.draw.rect(self.screen, DARK_GRAY, (ROAD_X, 0, ROAD_W, HEIGHT))
        pygame.draw.rect(self.screen, WHITE, (ROAD_X - 10, 0, 10, HEIGHT))
        pygame.draw.rect(self.screen, WHITE, (ROAD_X + ROAD_W, 0, 10, HEIGHT))
        
        for i in range(HEIGHT // 80 + 2):
            y_pos = i * 80 + self.road_offset - 80
            pygame.draw.rect(self.screen, WHITE, (ROAD_X + ROAD_W // 2 - 5, y_pos, 10, 40))
            
        for r in self.rain:
            r["y"] += r["v"]
            if r["y"] > HEIGHT:
                r["y"] = random.randint(-50, -10)
                r["x"] = random.randint(ROAD_X, ROAD_X + ROAD_W)
            pygame.draw.line(self.screen, (130, 130, 180), (r["x"], r["y"]), (r["x"], r["y"] + 10), 1)

    def draw_car(self, x, y, color, spin):
        pygame.draw.rect(self.screen, color, (x + 5, y, CAR_W - 10, CAR_H), border_radius=14)
        pygame.draw.rect(self.screen, (20, 20, 30), (x + 10, y + 15, CAR_W - 20, 22), border_radius=6)
        pygame.draw.rect(self.screen, (20, 20, 30), (x + 10, y + 55, CAR_W - 20, 18), border_radius=6)
        pygame.draw.circle(self.screen, YELLOW, (x + 10, y + 4), 4)
        pygame.draw.circle(self.screen, YELLOW, (x + CAR_W - 10, y + 4), 4)
        if spin:
            pygame.draw.arc(self.screen, CYAN, (x - 10, y, CAR_W + 20, CAR_H), 0, math.pi, 3)

    def draw_entity(self, e):
        kind, x, y, w, h, v = e["k"], e["x"], e["y"], e["w"], e["h"], e["v"]
        if kind == "E":
            body_col = (30, 144, 255) if int(x) % 2 == 0 else (220, 220, 220)
            pygame.draw.rect(self.screen, body_col, (x + 3, y, w - 6, h), border_radius=12)
            pygame.draw.rect(self.screen, (20, 20, 20), (x + 8, y + 12, w - 16, 18), border_radius=4)
            pygame.draw.rect(self.screen, (20, 20, 20), (x + 8, y + h - 25, w - 16, 15), border_radius=4)
        elif kind == "O":
            pygame.draw.rect(self.screen, (220, 100, 10), (x, y, w, h), border_radius=8)
            pygame.draw.rect(self.screen, BLACK, (x + 5, y + 5, w - 10, h - 10), border_radius=5)
        elif kind == "C":
            c = (int(x + w // 2), int(y + h // 2))
            pygame.draw.circle(self.screen, YELLOW, c, w // 2)
            pygame.draw.circle(self.screen, (200, 160, 20), c, w // 2, 2)
            self.text(str(v), self.small, BLACK, c[0], c[1], center=True)
        elif kind == "P":
            color, letter = POWER_STYLE.get(v, (GRAY, "?"))
            c = (int(x + w // 2), int(y + h // 2))
            pygame.draw.circle(self.screen, color, c, w // 2)
            pygame.draw.circle(self.screen, WHITE, c, w // 2, 2)
            self.text(letter, self.font, WHITE, c[0], c[1], center=True)

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000.0
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.KEYDOWN:
                    if self.mode == "menu":
                        if e.key == pygame.K_l:
                            self.show_leaderboard = not self.show_leaderboard
                        elif not self.show_leaderboard:
                            if e.key == pygame.K_TAB:
                                self.active_field = 1 - self.active_field
                            elif e.key == pygame.K_RETURN:
                                self.mode = "countdown"
                                self.countdown_timer = 3.0
                                self.reset_game()
                            elif e.key == pygame.K_BACKSPACE:
                                if self.active_field == 0 and len(self.p1_name) > 0:
                                    self.p1_name = self.p1_name[:-1]
                                elif self.active_field == 1 and len(self.p2_name) > 0:
                                    self.p2_name = self.p2_name[:-1]
                            elif e.unicode and e.unicode.isprintable():
                                if self.active_field == 0 and len(self.p1_name) < 15:
                                    self.p1_name += e.unicode
                                elif self.active_field == 1 and len(self.p2_name) < 15:
                                    self.p2_name += e.unicode
                    elif self.mode == "over":
                        if e.key == pygame.K_r:
                            self.mode = "menu"
                        elif e.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()

            if self.mode == "menu":
                self.screen.fill((15, 15, 25))
                self.text("FERRARI vs PORSCHE", self.big, YELLOW, WIDTH // 2, 50, center=True)
                self.text("LOCAL 2-PLAYER STRAIGHT ROAD", self.small, CYAN, WIDTH // 2, 95, center=True)

                if self.show_leaderboard:
                    self.text("TOP 10 LEADERBOARD", self.font, YELLOW, WIDTH // 2, 140, center=True)
                    top_scores = db.top()
                    y = 180
                    for idx, row in enumerate(top_scores):
                        self.text(f"{idx+1}. {row['name']} — {row['best']} pts", self.small, WHITE, WIDTH // 2, y, center=True)
                        y += 30
                    self.text("PRESS 'L' TO BACK", self.small, GRAY, WIDTH // 2, HEIGHT - 50, center=True)
                else:
                    self.text("Player 1 Name (Ferrari - A/D + W):", self.small, FERRARI_RED, 100, 160)
                    box1 = pygame.Rect(100, 190, 500, 40)
                    pygame.draw.rect(self.screen, WHITE if self.active_field == 0 else GRAY, box1, 2, border_radius=8)
                    self.text(self.p1_name, self.font, WHITE, box1.x + 12, box1.y + 6)

                    self.text("Player 2 Name (Porsche - Arrows + Up):", self.small, PORSCHE_SILVER, 100, 260)
                    box2 = pygame.Rect(100, 290, 500, 40)
                    pygame.draw.rect(self.screen, WHITE if self.active_field == 1 else GRAY, box2, 2, border_radius=8)
                    self.text(self.p2_name, self.font, WHITE, box2.x + 12, box2.y + 6)

                    self.text("TAB - Switch Field    ENTER - Start Game    L - Leaderboard", self.small, GRAY, WIDTH // 2, 450, center=True)

            elif self.mode == "countdown":
                self.countdown_timer -= dt
                self.draw_road()
                self.draw_car(self.p1["x"], PLAYER_Y, FERRARI_RED, False)
                self.draw_car(self.p2["x"], PLAYER_Y, PORSCHE_SILVER, False)
                
                count_val = int(math.ceil(self.countdown_timer))
                txt = str(count_val) if count_val > 0 else "GO!"
                self.text(txt, self.huge, WHITE, WIDTH // 2, HEIGHT // 2 - 40, center=True)
                if self.countdown_timer <= 0:
                    self.mode = "race"

            elif self.mode == "race":
                self.update_simulation(dt)
                self.draw_road()
                for e in self.entities:
                    self.draw_entity(e)

                if self.p1["alive"]:
                    self.draw_car(self.p1["x"], PLAYER_Y, FERRARI_RED, self.p1["spin"] > 0)
                    if self.p1["shield"]: pygame.draw.rect(self.screen, CYAN, (self.p1["x"] - 4, PLAYER_Y - 4, CAR_W + 8, CAR_H + 8), 3, border_radius=16)
                if self.p2["alive"]:
                    self.draw_car(self.p2["x"], PLAYER_Y, PORSCHE_SILVER, self.p2["spin"] > 0)
                    if self.p2["shield"]: pygame.draw.rect(self.screen, CYAN, (self.p2["x"] - 4, PLAYER_Y - 4, CAR_W + 8, CAR_H + 8), 3, border_radius=16)

                self.text(self.p1_name, self.font, FERRARI_RED, 20, 10)
                self.text(f"Score: {int(self.p1['dist']) + self.p1['coins']*5}", self.small, WHITE, 20, 35)
                for k in range(MAX_LIVES):
                    col = FERRARI_RED if k < self.p1["lives"] else DARK_GRAY
                    pygame.draw.circle(self.screen, col, (30 + k * 22, 65), 10)
                    pygame.draw.circle(self.screen, BLACK, (30 + k * 22, 65), 10, 2)

                self.text(self.p2_name, self.font, PORSCHE_SILVER, WIDTH - 180, 10)
                self.text(f"Score: {int(self.p2['dist']) + self.p2['coins']*5}", self.small, WHITE, WIDTH - 180, 35)
                for k in range(MAX_LIVES):
                    col = FERRARI_RED if k < self.p2["lives"] else DARK_GRAY
                    pygame.draw.circle(self.screen, col, (WIDTH - 170 + k * 22, 65), 10)
                    pygame.draw.circle(self.screen, BLACK, (WIDTH - 170 + k * 22, 65), 10, 2)

            elif self.mode == "over":
                self.screen.fill((15, 15, 25))
                self.text("RACE OVER", self.huge, FERRARI_RED, WIDTH // 2, HEIGHT // 2 - 100, center=True)
                self.text(f"Winner: {self.winner_name}", self.big, YELLOW, WIDTH // 2, HEIGHT // 2 - 10, center=True)
                
                y = HEIGHT // 2 + 70
                for r in sorted(self.over_results, key=lambda x: -x["score"]):
                    self.text(f"{r['name']} — {r['score']} pts", self.font, WHITE, WIDTH // 2, y, center=True)
                    y += 35
                self.text("R - Menu    ESC - Quit", self.small, GRAY, WIDTH // 2, HEIGHT - 50, center=True)

            pygame.display.flip()

if __name__ == "__main__":
    App().run()