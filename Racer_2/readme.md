# Ferrari vs Porsche — Online 2-Player Racer

A top-down arcade racing game for two players over the network, built with Python, pygame and TCP sockets.
Dodge traffic and obstacles, collect coins and power-ups, and outscore your opponent.
Results are stored in SQLite and shown in a built-in leaderboard.


## Features

- **Online multiplayer:** each player runs their own client and connects to one server (LAN or internet)
- **Authoritative server:** the server simulates the whole race; clients only send key presses and render snapshots
- Lobby with ready-check, 3-second countdown, rematch
- 3 lives per player, power-ups: **Nitro**, **Shield**, **Repair**, **Oil** (reverses controls for a moment), turbo key
- Difficulty ramps up with time: faster road, more traffic
- Rain effect, smooth rendering between server updates
- SQLite leaderboard (best score and wins per player)

## Controls

| Action | Keys |
|---|---|
| Steer | `A` / `D` or `←` / `→` |
| Turbo | `W` or `↑` |
| Ready (lobby) | `SPACE` |
| Rematch | `R` |

## Run

```bash
pip install -r requirements.txt
```

1. Start the server (one computer):
   ```bash
   python3 server.py
   ```
2. Start a client on each player's computer:
   ```bash
   python3 client.py <server-ip> <your-name>
   ```
   On the same computer use `localhost`. Open two terminals for two players.
3. Press `SPACE` in the lobby. The race starts when everyone is ready.

The server listens on TCP port **5005**. For play over the internet, open or forward this port on the server's router/firewall.

Requires Python 3.9+.

## Architecture

```
client A ─┐                         ┌─ World simulation (simulation.py)
          ├── TCP, JSON lines ──►   server.py ── SQLite (db.py)
client B ─┘   input ▲ │ snapshots   └─ lobby / countdown / race / over
```

| File | Purpose |
|---|---|
| `server.py` | Accepts clients, runs lobby and the 30 Hz game loop, broadcasts state |
| `simulation.py` | Game rules: movement, collisions, power-ups, spawning, scoring |
| `client.py` | Window, input, rendering, network reader thread |
| `protocol.py` | Constants and message encoding (newline-delimited JSON) |
| `db.py` | SQLite storage for matches and the leaderboard |

## Roadmap

- [ ] Sound effects
- [ ] Rooms with codes (more than one match at a time)
- [ ] Unit tests for the simulation

## License

MIT — see [LICENSE](LICENSE).