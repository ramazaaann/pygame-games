import psycopg2
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


def connect():
    return psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )


def create_tables():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS game_sessions (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES players(id),
            score INTEGER NOT NULL,
            level_reached INTEGER NOT NULL,
            played_at TIMESTAMP DEFAULT NOW()
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


def get_or_create_player(username):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT id FROM players WHERE username = %s", (username,))
    player = cur.fetchone()

    if player:
        player_id = player[0]
    else:
        cur.execute(
            "INSERT INTO players (username) VALUES (%s) RETURNING id",
            (username,)
        )
        player_id = cur.fetchone()[0]
        conn.commit()

    cur.close()
    conn.close()
    return player_id


def save_result(username, score, level):
    player_id = get_or_create_player(username)

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO game_sessions (player_id, score, level_reached)
        VALUES (%s, %s, %s)
    """, (player_id, score, level))

    conn.commit()
    cur.close()
    conn.close()


def get_leaderboard():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT players.username, game_sessions.score, game_sessions.level_reached
        FROM game_sessions
        JOIN players ON players.id = game_sessions.player_id
        ORDER BY game_sessions.score DESC
        LIMIT 10
    """)

    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


def get_personal_best(username):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT MAX(game_sessions.score)
        FROM game_sessions
        JOIN players ON players.id = game_sessions.player_id
        WHERE players.username = %s
    """, (username,))

    result = cur.fetchone()[0]

    cur.close()
    conn.close()

    if result is None:
        return 0
    return result