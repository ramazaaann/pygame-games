"""Racer online server.  Usage: python3 server.py [port]

The server owns the game state (authoritative). Clients only send key presses
and render the snapshots they receive.
"""
import logging
import socket
import sys
import threading
import time

import db
from protocol import PORT, TICK_RATE, encode, decode
from simulation import World

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("racer.server")

TICK = 1.0 / TICK_RATE
MAX_PLAYERS = 2
COUNTDOWN = 3


class Client:
    def __init__(self, sock, addr):
        self.sock, self.addr = sock, addr
        self.slot = None
        self.name = None
        self.ready = False
        self.controls = {"l": False, "r": False, "turbo": False}
        self._send_lock = threading.Lock()

    def send(self, msg):
        try:
            with self._send_lock:
                self.sock.sendall(encode(msg))
        except OSError:
            pass  # the reader thread notices the dead socket and drops the client


class GameServer:
    def __init__(self, port):
        self.lock = threading.RLock()
        self.clients = {}        # slot -> Client
        self.state = "lobby"     # lobby | countdown | running | over
        self.world = None
        self.countdown_start = 0.0
        self.last_count = None
        self.started_at = 0.0

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", port))
        self.sock.listen()
        log.info("Listening on port %s", port)

    # ---- connections ---------------------------------------------------
    def accept_loop(self):
        threading.Thread(target=self.game_loop, daemon=True).start()
        while True:
            sock, addr = self.sock.accept()
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.settimeout(5)
            c = Client(sock, addr)
            with self.lock:
                free = [s for s in range(MAX_PLAYERS) if s not in self.clients]
                if not free or self.state in ("countdown", "running"):
                    c.send({"t": "error", "msg": "Server is full or a race is in progress"})
                    sock.close()
                    continue
                c.slot = free[0]
                self.clients[c.slot] = c
            log.info("%s connected as slot %s", addr, c.slot)
            c.send({"t": "welcome", "id": c.slot})
            threading.Thread(target=self.serve_client, args=(c,), daemon=True).start()

    def serve_client(self, c):
        buf = b""
        try:
            while True:
                try:
                    data = c.sock.recv(4096)
                except socket.timeout:
                    continue
                if not data:
                    break
                buf += data
                if len(buf) > 65536:
                    break
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    try:
                        self.on_message(c, decode(line))
                    except (ValueError, AttributeError):
                        continue
        except OSError:
            pass
        finally:
            self.drop(c)

    def drop(self, c):
        with self.lock:
            if self.clients.get(c.slot) is not c:
                return
            del self.clients[c.slot]
            try:
                c.sock.close()
            except OSError:
                pass
            log.info("%s (%s) left", c.addr, c.name)
            if self.state == "running" and self.world:
                self.world.kill(c.slot)
            elif self.state == "countdown":
                self.state = "lobby"
                for other in self.clients.values():
                    other.ready = False
            self.broadcast_lobby()

    def on_message(self, c, msg):
        kind = msg.get("t")
        with self.lock:
            if kind == "join":
                c.name = str(msg.get("name", "")).strip()[:15] or ("Ferrari" if c.slot == 0 else "Porsche")
                c.send({"t": "top", "top": db.top()})
                self.broadcast_lobby()
            elif kind == "ready" and self.state in ("lobby", "over") and c.name:
                c.ready = True
                self.broadcast_lobby()
            elif kind == "input":
                c.controls = {"l": bool(msg.get("l")), "r": bool(msg.get("r")),
                              "turbo": bool(msg.get("turbo"))}

    # ---- broadcasting --------------------------------------------------
    def broadcast(self, msg):
        for c in list(self.clients.values()):
            c.send(msg)

    def broadcast_lobby(self):
        players = [{"s": s, "n": c.name or "...", "r": int(c.ready)}
                   for s, c in sorted(self.clients.items())]
        self.broadcast({"t": "lobby", "players": players})

    # ---- game loop -----------------------------------------------------
    def game_loop(self):
        prev = time.time()
        while True:
            time.sleep(TICK)
            now = time.time()
            dt, prev = min(now - prev, 0.1), now
            with self.lock:
                if self.state in ("lobby", "over"):
                    if self.clients and all(c.ready for c in self.clients.values()):
                        self.state = "countdown"
                        self.countdown_start = now
                        self.last_count = None
                elif self.state == "countdown":
                    n = COUNTDOWN - int(now - self.countdown_start)
                    if n != self.last_count:
                        self.last_count = n
                        self.broadcast({"t": "countdown", "n": max(n, 0)})
                    if n <= 0:
                        self.start_race(now)
                elif self.state == "running":
                    self.tick(dt)

    def start_race(self, now):
        names = {s: c.name for s, c in self.clients.items()}
        self.world = World(names)
        self.started_at = now
        self.state = "running"
        log.info("Race started: %s", list(names.values()))

    def tick(self, dt):
        if not self.clients:
            self.state = "lobby"
            return
        inputs = {s: c.controls for s, c in self.clients.items()}
        self.world.step(dt, inputs)
        self.broadcast(self.world.snapshot())
        if self.world.finished():
            self.finish_race()

    def finish_race(self):
        self.state = "over"
        results = self.world.results()
        duration = self.world.t
        for c in self.clients.values():
            c.ready = False
        winner = None
        if len(results) > 1:
            best = max(results, key=lambda r: r["score"])
            if sum(r["score"] == best["score"] for r in results) == 1:
                winner = best["name"]
        log.info("Race over: %s winner=%s", results, winner)
        threading.Thread(target=self.save_and_announce,
                         args=(results, duration, winner), daemon=True).start()

    def save_and_announce(self, results, duration, winner):
        db.save_match(results, duration, winner)
        top = db.top()
        with self.lock:
            self.broadcast({"t": "over", "results": results, "winner": winner, "top": top})


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    db.init()
    GameServer(port).accept_loop()