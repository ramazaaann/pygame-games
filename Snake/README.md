# Snake with AI Opponent

Snake built with Python and pygame. Play solo or race an AI snake for the same food. Game rules are separated from rendering, so the logic can be unit-tested without a window.

## Features

- Solo mode and **Play vs AI** mode
- Levels: every 5 apples the level goes up, the game gets faster and walls appear
- Poison (shrinks the snake) and power-ups: speed, slow, shield
- Food, poison, power-ups and walls never spawn on a snake
- PostgreSQL leaderboard and personal best (the game still runs if the database is unavailable)
- Settings saved to `settings.json` (grid on/off, snake colour)

## Controls

Arrow keys or `W` `A` `S` `D` to steer. Menus use the mouse.

## How the AI works

The AI snake finds the shortest path to the food with **BFS**. Before taking a step it runs a **flood fill** to check that the move leaves enough free space for its own body; if not, it picks the neighbouring cell with the most reachable space instead of walking into a dead end.

## Data structures

The snake body is a `deque` (O(1) move) together with a `set` of occupied cells (O(1) self-collision check), instead of scanning a list on every tick.

## Run

```bash
pip install -r requirements.txt
python3 main.py
```

### Optional: PostgreSQL leaderboard

1. Create an empty database (for example `snake_db`).
2. Copy `.env.example` to `.env` and fill in your credentials (the file is git-ignored).
3. Start the game. Tables are created automatically.

Without a database the game prints a warning and scores are simply not saved.

## Tests

```bash
python3 -m unittest discover -s tests
```

The tests cover snake movement and growth, reversal protection, self-collision, BFS and flood fill, safe spawning, shield, level-ups and AI behaviour.

## Structure

| File | Purpose |
|---|---|
| `snake_logic.py` | Game rules, BFS, flood fill, AI (no pygame) |
| `game.py` | Input, rendering and the frame loop |
| `ui.py` | Menus and screens |
| `db.py` | PostgreSQL storage with a connection pool |
| `settings.py`, `config.py` | Settings and constants (DB credentials come from `.env`) |
| `tests/test_logic.py` | Unit tests |