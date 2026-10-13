import logging
import sqlite3
from contextlib import closing

log = logging.getLogger("racer.db")
DB_NAME = "racer.db"


def _connect():
    return closing(sqlite3.connect(DB_NAME))


def init():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                duration REAL,
                winner TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                name TEXT,
                score INTEGER,
                coins INTEGER,
                distance INTEGER,
                FOREIGN KEY(match_id) REFERENCES matches(id)
            )
        """)
        conn.commit()


def save_match(results, duration, winner):
    """winner is None when the scores are tied."""
    try:
        with _connect() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO matches (duration, winner) VALUES (?, ?)", (duration, winner))
            match_id = cur.lastrowid
            for r in results:
                cur.execute(
                    "INSERT INTO scores (match_id, name, score, coins, distance) VALUES (?, ?, ?, ?, ?)",
                    (match_id, r["name"], r["score"], r["coins"], r["distance"]),
                )
            conn.commit()
    except sqlite3.Error as exc:
        log.error("Failed to save match: %s", exc)


def top(limit=10):
    """Best score, number of wins and games played per player name."""
    try:
        with _connect() as conn:
            rows = conn.execute("""
                SELECT s.name,
                       MAX(s.score) AS best,
                       (SELECT COUNT(*) FROM matches m WHERE m.winner = s.name) AS wins,
                       COUNT(*) AS games
                FROM scores s
                GROUP BY s.name
                ORDER BY best DESC
                LIMIT ?
            """, (limit,)).fetchall()
        return [{"name": n, "best": b, "wins": w, "games": g} for n, b, w, g in rows]
    except sqlite3.Error:
        return []