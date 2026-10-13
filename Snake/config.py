import os

WIDTH = 600
HEIGHT = 600
CELL = 30
COLS = WIDTH // CELL
ROWS = HEIGHT // CELL
FPS = 10

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
GREEN = (0, 200, 0)
RED = (220, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 220, 0)
PURPLE = (160, 0, 200)
DARK_RED = (120, 0, 0)
ORANGE = (255, 140, 0)


def _load_env(path=".env"):
    """Tiny .env reader so no password ever lives in the source code."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


_load_env()

DB_NAME = os.getenv("DB_NAME", "snake_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
