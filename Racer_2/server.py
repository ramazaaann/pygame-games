import socket
import threading
import time
from protocol import PORT, encode, decode
from simulation import World
import db

class GameServer:
    def __init__(self):
        self.lock = threading.Lock()
        self.client_sock = None
        self.names = {0: "Ferrari", 1: "Porsche"}
        self.world = None
        self.mode = "lobby"

    def handle_client(self, sock, addr):
        self.client_sock = sock
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        try:
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                for line in data.split(b"\n"):
                    if not line:
                        continue
                    msg = decode(line + b"\n")
                    kind = msg.get("t")

                    with self.lock:
                        if kind == "join":
                            self.names[0] = msg.get("p1_name", "Ferrari")
                            self.names[1] = msg.get("p2_name", "Porsche")
                            sock.sendall(encode({"t": "lobby", "status": "ready"}))

                        elif kind == "start":
                            if self.mode == "lobby":
                                self.start_game()

                        elif kind == "input":
                            if self.mode == "race" and self.world:
                                self.current_inputs = {
                                    0: {"l": msg.get("p1_l", False), "r": msg.get("p1_r", False), "turbo": msg.get("p1_t", False)},
                                    1: {"l": msg.get("p2_l", False), "r": msg.get("p2_r", False), "turbo": msg.get("p2_t", False)}
                                }
        except Exception:
            pass
        finally:
            sock.close()
            self.mode = "over"

    def start_game(self):
        self.world = World(self.names)
        self.current_inputs = {}
        self.mode = "countdown"
        threading.Thread(target=self.run_game_loop, daemon=True).start()

    def run_game_loop(self):
        for i in range(3, 0, -1):
            if self.client_sock:
                try:
                    self.client_sock.sendall(encode({"t": "countdown", "n": i}))
                except:
                    pass
            time.sleep(1.0)
        
        self.mode = "race"
        last_time = time.time()
        
        while self.mode == "race":
            now = time.time()
            dt = now - last_time
            last_time = now
            if dt < 0.005:
                time.sleep(0.005 - dt)
                continue
            dt = min(dt, 0.1)

            with self.lock:
                inputs = getattr(self, "current_inputs", {})
                self.world.step(dt, inputs)
                snapshot = self.world.snapshot()
                if self.client_sock:
                    try:
                        self.client_sock.sendall(encode(snapshot))
                    except:
                        break

                if self.world.finished():
                    self.mode = "over"
                    results = self.world.results()
                    winner = max(results, key=lambda x: x["score"])["name"] if results else None
                    db.save_match(results, self.world.t, winner)
                    if self.client_sock:
                        try:
                            self.client_sock.sendall(encode({"t": "over", "results": results, "winner": winner}))
                        except:
                            pass
                    break

def main():
    db.init()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", PORT))
    s.listen(1)
    server = GameServer()
    while True:
        sock, addr = s.accept()
        threading.Thread(target=server.handle_client, args=(sock, addr), daemon=True).start()

if __name__ == "__main__":
    main()