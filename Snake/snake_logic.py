"""Pure Snake game logic - no pygame, so it can be unit-tested and simulated headlessly.

Concepts used:
  * deque + set for the snake body: O(1) move and O(1) self-collision lookup
    (the old version scanned a list on every tick)
  * BFS shortest-path search for the AI opponent
  * flood fill as a "will I trap myself?" safety check
  * free-cell spawning, so food/obstacles never appear on top of a snake
"""
import random
from collections import deque

UP, RIGHT, DOWN, LEFT = (0, -1), (1, 0), (0, 1), (-1, 0)
DIRECTIONS = (UP, RIGHT, DOWN, LEFT)


def in_bounds(cell, cols, rows):
    return 0 <= cell[0] < cols and 0 <= cell[1] < rows


def random_free_cell(cols, rows, occupied, rng=random):
    free = [(x, y) for x in range(cols) for y in range(rows) if (x, y) not in occupied]
    return rng.choice(free) if free else None


class Snake:
    def __init__(self, head, direction=RIGHT, length=3):
        self.direction = direction
        self._next = direction
        self.body = deque((head[0] - i * direction[0], head[1] - i * direction[1])
                          for i in range(length))
        self.cells = set(self.body)   # same cells as body, for O(1) membership tests
        self.growth = 0
        self.shield = False

    def __len__(self):
        return len(self.body)

    @property
    def head(self):
        return self.body[0]

    @property
    def tail(self):
        return self.body[-1]

    def turn(self, direction):
        # validated against the last *moved* direction, so two quick key presses
        # inside one tick can never reverse the snake into itself
        if direction != (-self.direction[0], -self.direction[1]):
            self._next = direction

    def next_head(self):
        return (self.head[0] + self._next[0], self.head[1] + self._next[1])

    def hits_self(self):
        nxt = self.next_head()
        if nxt == self.tail and self.growth == 0 and len(self.body) > 1:
            return False  # the tail moves away this tick
        return nxt in self.cells

    def move(self):
        self.direction = self._next
        new = (self.head[0] + self.direction[0], self.head[1] + self.direction[1])
        if self.growth > 0:
            self.growth -= 1
        else:
            self.cells.discard(self.body.pop())
        self.body.appendleft(new)
        self.cells.add(new)

    def grow(self, n=1):
        self.growth += n

    def shrink(self, n=2):
        for _ in range(n):
            if len(self.body) > 1:
                self.cells.discard(self.body.pop())


def bfs_path(start, goal, blocked, cols, rows):
    """Shortest path from start to goal as a list of cells (start excluded), or None."""
    if start == goal:
        return []
    prev = {start: None}
    queue = deque([start])
    while queue:
        cur = queue.popleft()
        for dx, dy in DIRECTIONS:
            nxt = (cur[0] + dx, cur[1] + dy)
            if nxt in prev or not in_bounds(nxt, cols, rows) or nxt in blocked:
                continue
            prev[nxt] = cur
            if nxt == goal:
                path = [nxt]
                while prev[path[-1]] != start:
                    path.append(prev[path[-1]])
                return path[::-1]
            queue.append(nxt)
    return None


def flood_size(start, blocked, cols, rows, limit=10 ** 6):
    """How many cells are reachable from start (stops counting at `limit`)."""
    seen = {start}
    queue = deque([start])
    while queue and len(seen) < limit:
        cur = queue.popleft()
        for dx, dy in DIRECTIONS:
            nxt = (cur[0] + dx, cur[1] + dy)
            if nxt in seen or nxt in blocked or not in_bounds(nxt, cols, rows):
                continue
            seen.add(nxt)
            queue.append(nxt)
    return len(seen)


def ai_choose_direction(snake, food, blocked, cols, rows):
    """BFS towards the food, but only if the move leaves enough room (flood fill)
    for the whole snake; otherwise pick the neighbouring cell with the most free space."""
    head = snake.head
    opposite = (-snake.direction[0], -snake.direction[1])
    options = []
    for d in DIRECTIONS:
        cell = (head[0] + d[0], head[1] + d[1])
        if d != opposite and in_bounds(cell, cols, rows) and cell not in blocked:
            options.append((d, cell))
    if not options:
        return snake.direction

    path = bfs_path(head, food, blocked, cols, rows) if food else None
    if path:
        step = path[0]
        if flood_size(step, blocked, cols, rows, limit=len(snake) + 1) >= len(snake):
            return (step[0] - head[0], step[1] - head[1])

    return max(options, key=lambda o: flood_size(o[1], blocked, cols, rows))[0]


class GameState:
    """All rules of one game. mode = "solo" or "ai" (player vs BFS-driven snake)."""

    POWER_LIFETIME_MS = 8000
    POWER_DURATION_MS = 5000

    def __init__(self, cols, rows, base_fps=10, mode="solo", rng=None):
        self.cols, self.rows, self.base_fps, self.mode = cols, rows, base_fps, mode
        self.rng = rng or random.Random()
        self.player = Snake((cols // 3, rows // 2), RIGHT)
        self.ai = Snake((cols // 3, rows // 2 - 5), RIGHT) if mode == "ai" else None
        self.walls = set()
        self.score = 0
        self.ai_score = 0
        self.level = 1
        self.food = None
        self.poison = None
        self.power = None    # {"kind", "cell", "expires"}
        self.active = None   # {"kind", "start"}  speed / slow
        self.status = "running"
        self.winner = None   # "player" | "ai" | "draw" | None
        self.food = self._spawn()
        self.poison = self._spawn()

    # ---- helpers -------------------------------------------------------
    def snakes(self):
        out = [("player", self.player)]
        if self.ai:
            out.append(("ai", self.ai))
        return out

    def _occupied(self):
        occ = set(self.walls)
        for _, s in self.snakes():
            occ |= s.cells
        for item in (self.food, self.poison, self.power and self.power["cell"]):
            if item:
                occ.add(item)
        return occ

    def _spawn(self):
        return random_free_cell(self.cols, self.rows, self._occupied(), self.rng)

    def _blocked_for(self, snake):
        blocked = set(self.walls)
        for _, s in self.snakes():
            blocked |= s.cells
        if self.poison:
            blocked.add(self.poison)
        if snake.growth == 0 and len(snake) > 1:
            blocked.discard(snake.tail)  # tail will have moved by the time we get there
        return blocked

    def current_fps(self):
        fps = self.base_fps + (self.level - 1)
        if self.active:
            if self.active["kind"] == "speed":
                fps += 5
            elif self.active["kind"] == "slow":
                fps = max(5, fps - 5)
        return fps

    def _regenerate_walls(self):
        self.walls = set()
        if self.level < 3:
            return
        occupied = set()
        for _, s in self.snakes():
            occupied |= s.cells
            for k in range(1, 5):  # keep the path ahead of every head clear
                occupied.add((s.head[0] + s.direction[0] * k, s.head[1] + s.direction[1] * k))
        for item in (self.food, self.poison, self.power and self.power["cell"]):
            if item:
                occupied.add(item)
        for _ in range(self.level + 2):
            cell = random_free_cell(self.cols, self.rows, occupied | self.walls, self.rng)
            if cell is None:
                break
            self.walls.add(cell)

    # ---- one tick ------------------------------------------------------
    def step(self, now_ms):
        if self.status != "running":
            return

        if self.ai:
            self.ai.turn(ai_choose_direction(self.ai, self.food, self._blocked_for(self.ai),
                                             self.cols, self.rows))

        nxt = {name: s.next_head() for name, s in self.snakes()}
        dead, skipped = set(), set()
        for name, s in self.snakes():
            other = self.ai if (name == "player" and self.ai) else (self.player if self.ai else None)
            other_name = "ai" if name == "player" else "player"
            cell = nxt[name]
            reason = None
            if not in_bounds(cell, self.cols, self.rows):
                reason = "wall"
            elif cell in self.walls:
                reason = "obstacle"
            elif s.hits_self():
                reason = "self"
            elif other and cell in other.cells and not (cell == other.tail and other.growth == 0):
                reason = "other"
            elif other and cell == nxt[other_name]:
                reason = "head-on"
            if reason:
                if s.shield and reason in ("obstacle", "self", "other"):
                    s.shield = False       # shield absorbs one hit: the snake stays put this tick
                    skipped.add(name)
                else:
                    dead.add(name)

        for name, s in self.snakes():
            if name not in dead and name not in skipped:
                s.move()

        for name, s in self.snakes():
            if name in dead or name in skipped:
                continue
            if self.food and s.head == self.food:
                s.grow(1)
                if name == "player":
                    self.score += 1
                    if self.score % 5 == 0:
                        self.level += 1
                        self._regenerate_walls()
                else:
                    self.ai_score += 1
                self.food = self._spawn()
            if self.poison and s.head == self.poison:
                s.shrink(2)
                self.poison = self._spawn()
                if len(s) <= 1:
                    dead.add(name)

        self._update_powerups(now_ms, dead)

        if dead:
            self.status = "over"
            if dead == {"player"}:
                self.winner = "ai" if self.ai else None
            elif dead == {"ai"}:
                self.winner = "player"
            else:
                self.winner = "draw" if self.ai else None

    def _update_powerups(self, now_ms, dead):
        if self.power is None:
            if self.rng.random() < 0.01:
                cell = self._spawn()
                if cell:
                    self.power = {"kind": self.rng.choice(("speed", "slow", "shield")),
                                  "cell": cell, "expires": now_ms + self.POWER_LIFETIME_MS}
        elif now_ms > self.power["expires"]:
            self.power = None
        elif "player" not in dead and self.player.head == self.power["cell"]:
            kind = self.power["kind"]
            if kind == "shield":
                self.player.shield = True
            else:
                self.active = {"kind": kind, "start": now_ms}
            self.power = None
        if self.active and now_ms - self.active["start"] > self.POWER_DURATION_MS:
            self.active = None
