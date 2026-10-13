"""Reproduces the AI numbers: average apples per game for the BFS+flood-fill AI
versus a greedy baseline (always step towards the food, avoid immediate death).

Usage:  python3 benchmark.py [games]     (default 300 games, takes about 2-3 minutes)
"""
import random
import statistics
import sys

from snake_logic import DIRECTIONS, GameState, ai_choose_direction

COLS = ROWS = 20
MAX_TICKS = 4000


def greedy_direction(state):
    snake, food = state.player, state.food
    blocked = state._blocked_for(snake)
    opposite = (-snake.direction[0], -snake.direction[1])
    best = None
    for d in DIRECTIONS:
        cell = (snake.head[0] + d[0], snake.head[1] + d[1])
        if d == opposite or not (0 <= cell[0] < COLS and 0 <= cell[1] < ROWS) or cell in blocked:
            continue
        dist = abs(cell[0] - food[0]) + abs(cell[1] - food[1])
        if best is None or dist < best[0]:
            best = (dist, d)
    return best[1] if best else snake.direction


def play(seed, chooser):
    state = GameState(COLS, ROWS, mode="solo", rng=random.Random(seed))
    for tick in range(MAX_TICKS):
        state.player.turn(chooser(state))
        state.step(tick * 100)
        if state.status != "running":
            break
    return state.score


def ai_direction(state):
    return ai_choose_direction(state.player, state.food, state._blocked_for(state.player), COLS, ROWS)


if __name__ == "__main__":
    games = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    ai = [play(s, ai_direction) for s in range(games)]
    greedy = [play(s, greedy_direction) for s in range(games)]
    print(f"games: {games}")
    print(f"BFS + flood fill AI : mean {statistics.mean(ai):.1f} apples (max {max(ai)})")
    print(f"greedy baseline     : mean {statistics.mean(greedy):.1f} apples (max {max(greedy)})")
    print(f"improvement         : {statistics.mean(ai) / statistics.mean(greedy):.1f}x")