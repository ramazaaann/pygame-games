"""Racer online client.  Usage: python3 client.py [server_host] [name]"""
import math
import queue
import random
import socket
import sys
import threading
import time

import pygame

from protocol import (PORT, WIDTH, HEIGHT, ROAD_X, ROAD_W, CAR_W, CAR_H, PLAYER_Y,
                      MAX_LIVES, encode, decode)

WHITE, BLACK, GRAY = (255, 255, 255), (0, 0, 0), (100, 100, 100)
DARK_GRAY, GREEN = (20, 20, 25), (10, 80, 30)
FERRARI_RED = (225, 29, 42)
PORSCHE_SILVER = (200, 210, 225)
YELLOW, CYAN, ORANGE, BLUE = (255, 215, 0), (0, 229, 255), (255, 140, 0), (30, 144, 255)
POWER_STYLE = {"nitro": (CYAN, "N"), "shield": (BLUE, "S"), "repair": (GREEN, "R"), "oil": (ORANGE, "O")}
SLOT_COLOR = {0: FERRARI_RED, 1: PORSCHE_SILVER}
TRAFFIC_COLORS = [(30, 144, 255), (220, 220, 220), (90, 180, 90)]
START_X = {0: ROAD_X + 110, 1: ROAD_X + ROAD_W - 110 - CAR_W}


class Net:
    """TCP connection with a background reader thread."""

    def __init__(self):
        self.sock = None
        self.inbox = queue.Queue()

    def connect(self, host, port):
        self.sock = socket.create_connection((host, port), timeout=5)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.settimeout(None)
        threading.Thread(target=self._reader, daemon=True).start()

    def _reader(self):
        buf = b""
        try:
            while True:
                data = self.sock.recv(65536)
                if not data:
                    break
                buf += data
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    if line:
                        self.inbox.put(decode(line))
        except (OSError, ValueError):
            pass
        self.inbox.put({"t": "disconnected"})

    def send(self, msg):
        try:
            self.sock.sendall(encode(msg))
        except (OSError, AttributeError):
            pass


class App:
    def __init__(self, host, name):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Ferrari vs Porsche - Online")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.small = pygame.font.SysFont("Arial", 16)
        self.big = pygame.font.SysFont("Arial", 38, bold=True)
        self.huge = pygame.font.SysFont("Arial", 90, bold=True)

        self.net = Net()
        self.mode = "menu"          # menu | lobby | countdown | race | over
        self.fields = [name, host]  # [player name, server host]
        self.active_field = 0
        self.error = ""
        self.my_slot = None
        self.lobby = []
        self.top = []
        self.count = 3
        self.state = None
        self.state_time = 0.0
        self.show_x = {}
        self.over = {}
        self.last_input = (False, False, False)
        self.road_offset = 0.0
        self.dt = 0.016
        self.rain = [{"x": random.randint(ROAD_X, ROAD_X + ROAD_W), "y": random.randint(0, HEIGHT),
                      "v": random.randint(14, 22)} for _ in range(60)]

    # ---- helpers -------------------------------------------------------
    def text(self, s, font, color, x, y, center=False):
        img = font.render(s, True, color)
        rect = img.get_rect(center=(x, y)) if center else img.get_rect(topleft=(x, y))
        self.screen.blit(img, rect)

    def connect(self):
        name, host = (f.strip() for f in self.fields)
        try:
            self.net.connect(host or "localhost", PORT)
        except OSError as exc:
            self.error = f"Cannot connect: {exc}"
            return
        self.net.send({"t": "join", "name": name})
        self.mode = "lobby"
        self.error = ""

    # ---- network messages ----------------------------------------------
    def pump(self):
        while True:
            try:
                msg = self.net.inbox.get_nowait()
            except queue.Empty:
                return
            kind = msg.get("t")
            if kind == "welcome":
                self.my_slot = msg["id"]
            elif kind == "error":
                self.error = msg.get("msg", "Error")
                self.mode = "menu"
            elif kind == "disconnected":
                if self.mode != "menu":
                    self.error = "Disconnected from server"
                self.mode = "menu"
                self.net = Net()
            elif kind == "lobby":
                self.lobby = msg["players"]
            elif kind == "top":
                self.top = msg["top"]
            elif kind == "countdown":
                self.mode = "countdown"
                self.count = msg["n"]
                self.state = None
                self.show_x = {}
            elif kind == "state":
                self.mode = "race"
                self.state = msg
                self.state_time = time.time()
            elif kind == "over":
                self.over = msg
                self.top = msg.get("top", self.top)
                self.mode = "over"

    # ---- drawing -------------------------------------------------------
    def draw_road(self, speed):
        self.road_offset = (self.road_offset + speed * self.dt) % 80
        self.screen.fill(GREEN)
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

    def draw_car(self, x, y, color, spin=False, blink=False):
        if blink:
            return
        x, y = int(x), int(y)
        pygame.draw.rect(self.screen, color, (x + 5, y, CAR_W - 10, CAR_H), border_radius=14)
        pygame.draw.rect(self.screen, (20, 20, 30), (x + 10, y + 15, CAR_W - 20, 22), border_radius=6)
        pygame.draw.rect(self.screen, (20, 20, 30), (x + 10, y + 55, CAR_W - 20, 18), border_radius=6)
        pygame.draw.circle(self.screen, YELLOW, (x + 10, y + 4), 4)
        pygame.draw.circle(self.screen, YELLOW, (x + CAR_W - 10, y + 4), 4)
        if spin:
            pygame.draw.arc(self.screen, CYAN, (x - 10, y, CAR_W + 20, CAR_H), 0, math.pi, 3)

    def draw_entity(self, kind, x, y, w, h, v):
        x, y = int(x), int(y)
        if kind == "E":
            pygame.draw.rect(self.screen, TRAFFIC_COLORS[v % 3], (x + 3, y, w - 6, h), border_radius=12)
            pygame.draw.rect(self.screen, (20, 20, 20), (x + 8, y + 12, w - 16, 18), border_radius=4)
            pygame.draw.rect(self.screen, (20, 20, 20), (x + 8, y + h - 25, w - 16, 15), border_radius=4)
        elif kind == "O":
            pygame.draw.rect(self.screen, (220, 100, 10), (x, y, w, h), border_radius=8)
            pygame.draw.rect(self.screen, BLACK, (x + 5, y + 5, w - 10, h - 10), border_radius=5)
        elif kind == "C":
            c = (x + w // 2, y + h // 2)
            pygame.draw.circle(self.screen, YELLOW, c, w // 2)
            pygame.draw.circle(self.screen, (200, 160, 20), c, w // 2, 2)
            self.text(str(v), self.small, BLACK, c[0], c[1], center=True)
        elif kind == "P":
            color, letter = POWER_STYLE.get(v, (GRAY, "?"))
            c = (x + w // 2, y + h // 2)
            pygame.draw.circle(self.screen, color, c, w // 2)
            pygame.draw.circle(self.screen, WHITE, c, w // 2, 2)
            self.text(letter, self.font, WHITE, c[0], c[1], center=True)

    def draw_hud(self, p):
        right = p["s"] == 1
        x = WIDTH - 180 if right else 20
        color = SLOT_COLOR.get(p["s"], WHITE)
        self.text(p["n"] + (" (you)" if p["s"] == self.my_slot else ""), self.font, color, x, 10)
        self.text(f"Score: {p['sc']}", self.small, WHITE, x, 35)
        for k in range(MAX_LIVES):
            col = color if k < p["l"] else DARK_GRAY
            pygame.draw.circle(self.screen, col, (x + 10 + k * 22, 65), 10)
            pygame.draw.circle(self.screen, BLACK, (x + 10 + k * 22, 65), 10, 2)
        status = []
        if not p["a"]:
            status.append("OUT")
        else:
            if p["sh"]:
                status.append("SHIELD")
            if p["nt"] > 0:
                status.append(f"NITRO {p['nt']:.0f}s")
            if p["sp"]:
                status.append("OIL!")
        self.text(" ".join(status), self.small, CYAN, x, 85)

    def draw_race(self):
        st = self.state
        age = min(time.time() - self.state_time, 0.1)
        self.draw_road(st["ws"] if st else 0)
        if not st:
            for p in self.lobby:  # countdown: cars wait on the grid
                self.draw_car(START_X.get(p["s"], START_X[0]), PLAYER_Y, SLOT_COLOR.get(p["s"], WHITE))
            return
        for kind, x, y, w, h, v, spd in st["e"]:
            self.draw_entity(kind, x, y + spd * age, w, h, v)
        now = time.time()
        for p in st["p"]:
            slot = p["s"]
            cur = self.show_x.get(slot, p["x"])
            cur += (p["x"] - cur) * 0.5  # smooth between server updates
            self.show_x[slot] = cur
            if p["a"]:
                blink = bool(p["iv"]) and int(now * 10) % 2 == 0
                self.draw_car(cur, PLAYER_Y, SLOT_COLOR.get(slot, WHITE), bool(p["sp"]), blink)
                if p["sh"]:
                    pygame.draw.rect(self.screen, CYAN, (int(cur) - 4, PLAYER_Y - 4, CAR_W + 8, CAR_H + 8),
                                     3, border_radius=16)
            self.draw_hud(p)

    def draw_screen(self):
        self.screen.fill((15, 15, 25))
        if self.mode == "menu":
            self.text("FERRARI vs PORSCHE", self.big, YELLOW, WIDTH // 2, 50, center=True)
            self.text("ONLINE 2-PLAYER", self.small, CYAN, WIDTH // 2, 95, center=True)
            labels = ["Your name", "Server address (IP)"]
            for i, label in enumerate(labels):
                y = 170 + i * 100
                self.text(label, self.small, GRAY, 100, y)
                box = pygame.Rect(100, y + 28, 500, 40)
                pygame.draw.rect(self.screen, WHITE if i == self.active_field else GRAY, box, 2, border_radius=8)
                self.text(self.fields[i], self.font, WHITE, box.x + 12, box.y + 6)
            self.text("TAB - switch field    ENTER - connect", self.small, GRAY, WIDTH // 2, 450, center=True)
            self.text(self.error, self.small, FERRARI_RED, WIDTH // 2, 490, center=True)
        elif self.mode == "lobby":
            self.text("LOBBY", self.big, YELLOW, WIDTH // 2, 60, center=True)
            for i, p in enumerate(self.lobby):
                tag = " (you)" if p["s"] == self.my_slot else ""
                self.text(f"{p['n']}{tag}", self.font, SLOT_COLOR.get(p["s"], WHITE), 150, 140 + i * 40)
                self.text("READY" if p["r"] else "waiting", self.font, CYAN if p["r"] else GRAY, 450, 140 + i * 40)
            self.text("SPACE - ready    (race starts when everyone is ready)", self.small, WHITE,
                      WIDTH // 2, 260, center=True)
            self.draw_top(320)
            self.text("A/D or ←/→ steer   W or ↑ turbo", self.small, GRAY, WIDTH // 2, HEIGHT - 40, center=True)
        elif self.mode == "over":
            o = self.over
            self.text("RACE OVER", self.huge, FERRARI_RED, WIDTH // 2, 110, center=True)
            winner = o.get("winner")
            if winner:
                self.text(f"Winner: {winner}", self.big, YELLOW, WIDTH // 2, 200, center=True)
            elif len(o.get("results", [])) > 1:
                self.text("Draw!", self.big, YELLOW, WIDTH // 2, 200, center=True)
            y = 260
            for r in sorted(o.get("results", []), key=lambda r: -r["score"]):
                self.text(f"{r['name']} — {r['score']} pts", self.font, WHITE, WIDTH // 2, y, center=True)
                y += 35
            self.draw_top(y + 30)
            me = next((p for p in self.lobby if p["s"] == self.my_slot), None)
            hint = "Waiting for opponent..." if me and me["r"] else "R - rematch    ESC - quit"
            self.text(hint, self.small, GRAY, WIDTH // 2, HEIGHT - 40, center=True)

    def draw_top(self, y):
        if not self.top:
            return
        self.text("TOP 10", self.font, YELLOW, WIDTH // 2, y, center=True)
        for i, row in enumerate(self.top[:8]):
            self.text(f"{i + 1}. {row['name']} — {row['best']} pts  ({row['wins']} wins)", self.small,
                      WHITE, WIDTH // 2, y + 30 + i * 24, center=True)

    # ---- input ---------------------------------------------------------
    def handle_event(self, e):
        if e.type != pygame.KEYDOWN:
            return
        if self.mode == "menu":
            f = self.active_field
            if e.key == pygame.K_TAB:
                self.active_field = 1 - f
            elif e.key == pygame.K_RETURN:
                self.connect()
            elif e.key == pygame.K_BACKSPACE:
                self.fields[f] = self.fields[f][:-1]
            elif e.unicode and e.unicode.isprintable() and len(self.fields[f]) < 24:
                self.fields[f] += e.unicode
        elif self.mode == "lobby" and e.key == pygame.K_SPACE:
            self.net.send({"t": "ready"})
        elif self.mode == "over":
            if e.key == pygame.K_r:
                self.net.send({"t": "ready"})
            elif e.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    def send_input(self):
        keys = pygame.key.get_pressed()
        cur = (bool(keys[pygame.K_a] or keys[pygame.K_LEFT]),
               bool(keys[pygame.K_d] or keys[pygame.K_RIGHT]),
               bool(keys[pygame.K_w] or keys[pygame.K_UP]))
        if cur != self.last_input:
            self.last_input = cur
            self.net.send({"t": "input", "l": cur[0], "r": cur[1], "turbo": cur[2]})

    # ---- main loop -----------------------------------------------------
    def run(self):
        while True:
            self.dt = self.clock.tick(60) / 1000.0
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.handle_event(e)
            self.pump()

            if self.mode == "race":
                self.send_input()
                self.draw_race()
            elif self.mode == "countdown":
                self.draw_race()
                self.text(str(self.count) if self.count > 0 else "GO!", self.huge, WHITE,
                          WIDTH // 2, HEIGHT // 2 - 40, center=True)
            else:
                self.draw_screen()
            pygame.display.flip()


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    name = sys.argv[2] if len(sys.argv) > 2 else ""
    App(host, name).run()
