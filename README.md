# Pygame Games

A collection of Python projects, mixing pygame games with a database-backed phonebook app.

## Projects Included

- **Snake**: Snake game with level progression, procedural walls, poison and power-ups. Eat food to grow, avoid walls and your own tail. Results and a top-10 leaderboard are stored in PostgreSQL.
- **Racer**: Single-player fast-paced racing game — dodge oncoming obstacles and survive as long as you can without crashing. Includes a leaderboard to track high scores.
- **Racer_2 (NEW)**: Online 2-Player Racer (Ferrari vs Porsche) — each player runs their own client and connects to a TCP socket server. The server simulates the race (authoritative), with lobby, countdown, rematch, power-ups (nitro, shield, repair, oil), coins, and a SQLite leaderboard. See [Racer_2/README.md](Racer_2/README.md) for details.
- **Paint**: A drawing app — pick a tool and draw on the screen with your mouse.
- **phonebook**: A Python application connected to a database for managing contact records.

## Requirements

- Python 3.9+
- Pygame
- psycopg2-binary (for Snake and phonebook, which use PostgreSQL)
- A running PostgreSQL server for Snake and phonebook (Racer, Racer_2 and Paint need no database setup)

### Install dependencies

    pip install pygame psycopg2-binary

## How to Run

Clone the repository:

    git clone https://github.com/ramazaaann/pygame-games.git
    cd pygame-games

Then run whichever project you want:

    # Run Snake
    python Snake/main.py

    # Run Classic Racer
    python Racer/main.py

    # Run Paint
    python Paint/paint.py

    # Run Phonebook App
    python phonebook/phonebook.py

### Racer_2 (online multiplayer)

Open three terminals in the `Racer_2` folder (`cd Racer_2`):

    # Terminal 1 - server
    python3 server.py

    # Terminal 2 - player 1
    python3 client.py localhost Ferrari

    # Terminal 3 - player 2
    python3 client.py localhost Porsche

Press `SPACE` in the lobby when both players are ready. To play from two computers on the same Wi-Fi, run the server on one of them and start the clients with the server's IP address instead of `localhost`.

Controls: `A`/`D` or `←`/`→` to steer, `W` or `↑` for turbo.

## Project Structure

    pygame-games/
    ├── Snake/
    ├── Racer/
    ├── Racer_2/        # online 2-player racer (server.py + client.py)
    ├── Paint/
    └── phonebook/

## Author

Made by Ramazan — projects to practice Pygame, networking and database integration.
