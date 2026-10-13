# Pygame Games

A collection of Python projects: pygame games with PostgreSQL / SQLite storage, a networked multiplayer racer, and a database-backed phonebook app.

## Projects

| Project | What it is |
|---|---|
| [**Racer_2**](Racer_2) | Online 2-player racer (Ferrari vs Porsche). Each player runs a pygame client and connects to a multithreaded TCP server that runs the race simulation. SQLite leaderboard. |
| [**Snake**](Snake) | Snake with levels, walls, poison and power-ups, a **BFS-driven AI opponent**, unit-tested game logic and a PostgreSQL leaderboard. |
| **Racer** | Single-player racing game: dodge obstacles and survive as long as you can. JSON leaderboard. |
| **Paint** | Drawing app: pick a tool and draw with the mouse. |
| **phonebook** | Python application connected to a PostgreSQL database for managing contacts. |

## Requirements

- Python 3.9+
- `pygame`
- `psycopg2-binary` and a running PostgreSQL server (only for **Snake**'s leaderboard and **phonebook**; Snake still runs without a database)

```bash
pip install pygame psycopg2-binary
```

## Run

```bash
git clone https://github.com/ramazaaann/pygame-games.git
cd pygame-games
```

```bash
# Snake (see Snake/README.md for database setup and tests)
cd Snake && python3 main.py

# Classic Racer
cd Racer && python3 main.py

# Paint
cd Paint && python3 paint.py

# Phonebook
cd phonebook && python3 phonebook.py
```

### Racer_2 (online multiplayer)

Open three terminals in `Racer_2`:

```bash
python3 server.py                          # terminal 1: server
python3 client.py localhost Ferrari        # terminal 2: player 1
python3 client.py localhost Porsche        # terminal 3: player 2
```

Press `SPACE` in the lobby when both players are ready. To play from two computers, run the server on one of them and start the other client with the server's IP address instead of `localhost` (TCP port 5005). Details: [Racer_2/README.md](Racer_2/README.md).

## Structure

```
pygame-games/
├── Racer_2/     # online 2-player racer (server.py + client.py)
├── Snake/       # snake with AI opponent, tests, PostgreSQL
├── Racer/
├── Paint/
└── phonebook/
```

## Author

Made by Ramazan Serikbay — projects for practising Python, networking, algorithms and databases.
