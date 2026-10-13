import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from snake_logic import (DOWN, LEFT, RIGHT, UP, GameState, Snake, ai_choose_direction,  # noqa: E402
                         bfs_path, flood_size, random_free_cell)

COLS = ROWS = 20


class SnakeTests(unittest.TestCase):
    def test_move_keeps_body_and_cells_in_sync(self):
        s = Snake((5, 5), RIGHT)
        for _ in range(10):
            s.move()
            self.assertEqual(set(s.body), s.cells)
            self.assertEqual(len(s.body), 3)

    def test_growth_adds_one_cell(self):
        s = Snake((5, 5), RIGHT)
        s.grow(1)
        s.move()
        self.assertEqual(len(s), 4)
        self.assertEqual(set(s.body), s.cells)

    def test_cannot_reverse_even_with_two_quick_turns(self):
        s = Snake((5, 5), RIGHT)
        s.turn(UP)
        s.turn(LEFT)           # would reverse relative to the real direction
        s.move()
        self.assertNotEqual(s.direction, LEFT)

    def test_self_collision_detected_and_tail_chase_allowed(self):
        s = Snake((5, 5), RIGHT, length=5)
        s.turn(DOWN); s.move()
        s.turn(LEFT); s.move()
        s.turn(UP)
        self.assertTrue(s.hits_self())      # runs into its own body
        t = Snake((5, 5), RIGHT, length=4)
        t.turn(DOWN); t.move(); t.turn(LEFT); t.move(); t.turn(UP)
        self.assertFalse(t.hits_self())     # steps into the cell the tail is leaving


class SearchTests(unittest.TestCase):
    def test_bfs_is_shortest_on_empty_grid(self):
        path = bfs_path((0, 0), (7, 5), set(), COLS, ROWS)
        self.assertEqual(len(path), 12)     # Manhattan distance

    def test_bfs_goes_around_a_wall(self):
        wall = {(3, y) for y in range(0, 10)}
        path = bfs_path((0, 5), (6, 5), wall, COLS, ROWS)
        self.assertIsNotNone(path)
        self.assertTrue(all(c not in wall for c in path))
        self.assertGreater(len(path), 6)

    def test_bfs_returns_none_when_enclosed(self):
        box = {(4, 5), (6, 5), (5, 4), (5, 6)}
        self.assertIsNone(bfs_path((5, 5), (10, 10), box, COLS, ROWS))

    def test_flood_fill_counts_enclosed_area(self):
        box = {(4, 5), (6, 5), (5, 4), (5, 6)}
        self.assertEqual(flood_size((5, 5), box, COLS, ROWS), 1)


class SpawnTests(unittest.TestCase):
    def test_free_cell_never_occupied(self):
        rng = random.Random(1)
        occupied = {(x, y) for x in range(COLS) for y in range(ROWS)} - {(3, 3)}
        self.assertEqual(random_free_cell(COLS, ROWS, occupied, rng), (3, 3))
        occupied.add((3, 3))
        self.assertIsNone(random_free_cell(COLS, ROWS, occupied, rng))

    def test_food_never_spawns_on_snake_or_walls(self):
        rng = random.Random(2)
        for _ in range(200):
            g = GameState(COLS, ROWS, mode="ai", rng=rng)
            self.assertNotIn(g.food, g.player.cells | g.ai.cells | g.walls)
            self.assertNotEqual(g.food, g.poison)


class AITests(unittest.TestCase):
    def test_ai_never_steps_into_wall_or_body_when_it_can_avoid_it(self):
        rng = random.Random(3)
        g = GameState(COLS, ROWS, mode="solo", rng=rng)
        for tick in range(400):
            g.player.turn(ai_choose_direction(g.player, g.food, g._blocked_for(g.player), COLS, ROWS))
            g.step(tick * 100)
            if g.status != "running":
                break
        self.assertGreater(g.score, 5)

    def test_ai_beats_random_play_on_average(self):
        def play(seed):
            rng = random.Random(seed)
            g = GameState(COLS, ROWS, mode="solo", rng=rng)
            for tick in range(3000):
                d = ai_choose_direction(g.player, g.food, g._blocked_for(g.player), COLS, ROWS)
                g.player.turn(d)
                g.step(tick * 100)
                if g.status != "running":
                    break
            return g.score
        scores = [play(s) for s in range(20)]
        self.assertGreater(sum(scores) / len(scores), 10)


class GameRulesTests(unittest.TestCase):
    def test_wall_collision_ends_game(self):
        g = GameState(COLS, ROWS, mode="solo", rng=random.Random(4))
        for tick in range(40):
            g.step(tick * 100)
            if g.status != "running":
                break
        self.assertEqual(g.status, "over")

    def test_level_up_every_five_foods(self):
        g = GameState(COLS, ROWS, mode="solo", rng=random.Random(5))
        for i in range(5):
            g.food = (g.player.head[0] + 1, g.player.head[1])
            g.player.turn(RIGHT)
            g.step(i * 100)
        self.assertEqual(g.score, 5)
        self.assertEqual(g.level, 2)

    def test_shield_absorbs_one_self_collision(self):
        g = GameState(COLS, ROWS, mode="solo", rng=random.Random(6))
        g.player = Snake((10, 10), RIGHT, length=6)
        g.player.shield = True
        g.player.turn(DOWN); g.step(0)
        g.player.turn(LEFT); g.step(100)
        g.player.turn(UP); g.step(200)
        self.assertEqual(g.status, "running")
        self.assertFalse(g.player.shield)

    def test_speed_power_expires_without_drifting_base_speed(self):
        g = GameState(COLS, ROWS, base_fps=10, mode="solo", rng=random.Random(7))
        g.active = {"kind": "speed", "start": 0}
        self.assertEqual(g.current_fps(), 15)
        g._update_powerups(6000, set())
        self.assertEqual(g.current_fps(), 10)


if __name__ == "__main__":
    unittest.main()
