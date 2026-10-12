# Pygame Games

A collection of small Python projects, mixing pygame games with a database-backed phonebook app.

## Projects Included

- **Snake**: Classic snake game — eat food to grow longer while avoiding the walls and your own tail.
- **Racer**: Single-player fast-paced racing game — dodge oncoming obstacles and survive as long as you can without crashing. Includes a leaderboard to track high scores.
- **Racer_2 (NEW)**: Local 2-Player Arcade Edition (Ferrari vs Porsche) — dual controls on a single screen (P1: W/A/D, P2: Arrows/Up), straight road, power-ups, coins, and local SQLite leaderboard support.
- **Paint**: A drawing app — pick a tool and draw on the screen with your mouse.
- **phonebook**: A Python application connected to a database for managing contact records.

## Requirements

- Python 3.x
- Pygame
- psycopg2-binary (for the phonebook's database connection)

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

    # Run NEW Racer_2 (2-Player Mode)
    python Racer_2/client.py

    # Run Paint
    python Paint/paint.py

    # Run Phonebook App
    python phonebook/phonebook.py

## Project Structure

    pygame-games/
    ├── Snake/
    ├── Racer/
    ├── Racer_2/
    ├── Paint/
    └── phonebook/

## Author

Made by Ramazan — a set of projects to practice Pygame and database integration.
