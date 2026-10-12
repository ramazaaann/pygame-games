import sqlite3
import logging

log = logging.getLogger("racer.db")
DB_NAME = "racer.db"


def init():
    with sqlite3.connect(DB_NAME) as conn:
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
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO matches (duration, winner) VALUES (?, ?)", (duration, winner))
            match_id = cur.lastrowid
            for r in results:
                cur.execute(
                    "INSERT INTO scores (match_id, name, score, coins, distance) VALUES (?, ?, ?, ?, ?)",
                    (match_id, r["name"], r["score"], r["coins"], r["distance"])
                )
            conn.commit()
    except Exception as e:
        log.error(f"Failed to save match to DB: {e}")


def top():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT name, MAX(score) as best, SUM(CASE WHEN name = ? THEN 1 ELSE 0 END) as wins, COUNT(*) as games
                FROM scores GROUP BY name ORDER BY best DESC LIMIT 10
            """, ("",))
            rows = cur.fetchall()
            return [{"name": r[0], "best": r[1], "wins": r[2], "games": r[3]} for r in rows]
    except Exception:
        return []