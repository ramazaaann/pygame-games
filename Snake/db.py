"""PostgreSQL storage: connection pool, one transaction per saved game.
The game keeps working (without saving) if the database is unavailable."""
import logging
from contextlib import contextmanager

try:
    import psycopg2
    from psycopg2 import pool
except ImportError:
    psycopg2 = None

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

log = logging.getLogger("snake.db")
_pool = None


def init():
    """Open the pool and create tables. Returns True when the database is usable."""
    global _pool
    if psycopg2 is None:
        log.warning("psycopg2 is not installed - scores will not be saved")
        return False
    try:
        _pool = pool.ThreadedConnectionPool(
            1, 5, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        _create_tables()
        return True
    except Exception as exc:
        log.warning("PostgreSQL unavailable (%s) - scores will not be saved", exc)
        _pool = None
        return False


@contextmanager
def _cursor():
    conn = _pool.getconn()
    try:
        with conn.cursor() as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _pool.putconn(conn)


def _create_tables():
    with _cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL
            );
            CREATE TABLE IF NOT EXISTS game_sessions (
                id SERIAL PRIMARY KEY,
                player_id INTEGER NOT NULL REFERENCES players(id),
                score INTEGER NOT NULL,
                level_reached INTEGER NOT NULL,
                played_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
            ALTER TABLE game_sessions ADD COLUMN IF NOT EXISTS mode VARCHAR(10) NOT NULL DEFAULT 'solo';
            ALTER TABLE game_sessions ADD COLUMN IF NOT EXISTS won BOOLEAN;
            CREATE INDEX IF NOT EXISTS idx_sessions_score ON game_sessions (score DESC);
            CREATE INDEX IF NOT EXISTS idx_sessions_player ON game_sessions (player_id);
        """)


def save_result(username, score, level, mode="solo", won=None):
    """Upsert the player and insert the session in a single transaction."""
    if _pool is None:
        return
    try:
        with _cursor() as cur:
            cur.execute(
                """INSERT INTO players (username) VALUES (%s)
                   ON CONFLICT (username) DO UPDATE SET username = EXCLUDED.username
                   RETURNING id""", (username,))
            player_id = cur.fetchone()[0]
            cur.execute(
                """INSERT INTO game_sessions (player_id, score, level_reached, mode, won)
                   VALUES (%s, %s, %s, %s, %s)""", (player_id, score, level, mode, won))
    except Exception as exc:
        log.error("Could not save result: %s", exc)


def get_leaderboard(limit=10):
    """Top scores as (username, score, level, mode) rows."""
    if _pool is None:
        return []
    try:
        with _cursor() as cur:
            cur.execute(
                """SELECT p.username, s.score, s.level_reached, s.mode
                   FROM game_sessions s JOIN players p ON p.id = s.player_id
                   ORDER BY s.score DESC, s.played_at ASC
                   LIMIT %s""", (limit,))
            return cur.fetchall()
    except Exception as exc:
        log.error("Could not load leaderboard: %s", exc)
        return []


def get_personal_best(username):
    if _pool is None:
        return 0
    try:
        with _cursor() as cur:
            cur.execute(
                """SELECT COALESCE(MAX(s.score), 0)
                   FROM game_sessions s JOIN players p ON p.id = s.player_id
                   WHERE p.username = %s""", (username,))
            return cur.fetchone()[0]
    except Exception as exc:
        log.error("Could not load personal best: %s", exc)
        return 0
