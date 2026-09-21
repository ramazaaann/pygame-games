import pygame
import random
import json
from config import *


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Snake:
    def __init__(self):
        self.body = [
            Point(10, 10),
            Point(9, 10),
            Point(8, 10)
        ]
        self.dx = 1
        self.dy = 0
        self.shield = False

    def move(self):
        head = self.body[0]
        new_head = Point(head.x + self.dx, head.y + self.dy)
        self.body.insert(0, new_head)
        self.body.pop()

    def grow(self):
        tail = self.body[-1]
        self.body.append(Point(tail.x, tail.y))

    def shrink(self):
        if len(self.body) > 1:
            self.body.pop()
        if len(self.body) > 1:
            self.body.pop()

    def change_direction(self, dx, dy):
        if self.dx != -dx or self.dy != -dy:
            self.dx = dx
            self.dy = dy

    def check_self_collision(self):
        head = self.body[0]
        for part in self.body[1:]:
            if head.x == part.x and head.y == part.y:
                return True
        return False


class Food:
    def __init__(self, walls):
        self.spawn(walls)

    def spawn(self, walls):
        while True:
            self.x = random.randint(0, WIDTH // CELL - 1)
            self.y = random.randint(0, HEIGHT // CELL - 1)

            blocked = False
            for wall in walls:
                if self.x == wall.x and self.y == wall.y:
                    blocked = True

            if not blocked:
                break


class PowerUp:
    def __init__(self, walls):
        self.types = ["speed", "slow", "shield"]
        self.type = random.choice(self.types)
        self.spawn_time = pygame.time.get_ticks()
        self.spawn(walls)

    def spawn(self, walls):
        while True:
            self.x = random.randint(0, WIDTH // CELL - 1)
            self.y = random.randint(0, HEIGHT // CELL - 1)

            blocked = False
            for wall in walls:
                if self.x == wall.x and self.y == wall.y:
                    blocked = True

            if not blocked:
                break


def load_settings():
    try:
        with open("settings.json", "r") as file:
            return json.load(file)
    except:
        return {
            "snake_color": [0, 200, 0],
            "grid": True,
            "sound": True
        }


def save_settings(settings):
    with open("settings.json", "w") as file:
        json.dump(settings, file, indent=4)


def draw_grid(screen):
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))


def draw_snake(screen, snake, color):
    for part in snake.body:
        pygame.draw.rect(
            screen,
            color,
            (part.x * CELL, part.y * CELL, CELL, CELL)
        )


def draw_food(screen, food):
    pygame.draw.rect(
        screen,
        RED,
        (food.x * CELL, food.y * CELL, CELL, CELL)
    )


def draw_poison(screen, poison):
    pygame.draw.rect(
        screen,
        DARK_RED,
        (poison.x * CELL, poison.y * CELL, CELL, CELL)
    )


def draw_power(screen, power):
    color = YELLOW

    if power.type == "speed":
        color = BLUE
    elif power.type == "slow":
        color = PURPLE
    elif power.type == "shield":
        color = YELLOW

    pygame.draw.rect(
        screen,
        color,
        (power.x * CELL, power.y * CELL, CELL, CELL)
    )


def draw_walls(screen, walls):
    for wall in walls:
        pygame.draw.rect(
            screen,
            BLACK,
            (wall.x * CELL, wall.y * CELL, CELL, CELL)
        )


def create_walls(level, snake):
    walls = []

    if level < 3:
        return walls

    count = level + 2

    while len(walls) < count:
        x = random.randint(0, WIDTH // CELL - 1)
        y = random.randint(0, HEIGHT // CELL - 1)

        bad = False

        for part in snake.body:
            if x == part.x and y == part.y:
                bad = True

        if not bad:
            walls.append(Point(x, y))

    return walls


def run_game(screen, username, best):
    settings = load_settings()

    snake = Snake()
    walls = []
    food = Food(walls)
    poison = Food(walls)
    power = None

    score = 0
    level = 1
    speed = FPS
    power_start = 0
    active_power = None

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Verdana", 20)

    running = True

    while running:
        clock.tick(speed)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return score, level, "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.change_direction(0, -1)
                elif event.key == pygame.K_DOWN:
                    snake.change_direction(0, 1)
                elif event.key == pygame.K_LEFT:
                    snake.change_direction(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction(1, 0)

        snake.move()
        head = snake.body[0]

        if head.x < 0 or head.x >= WIDTH // CELL or head.y < 0 or head.y >= HEIGHT // CELL:
            running = False

        if snake.check_self_collision():
            if snake.shield:
                snake.shield = False
            else:
                running = False

        for wall in walls:
            if head.x == wall.x and head.y == wall.y:
                running = False

        if head.x == food.x and head.y == food.y:
            score += 1
            snake.grow()
            food.spawn(walls)

            if score % 5 == 0:
                level += 1
                speed += 1
                walls = create_walls(level, snake)

        if head.x == poison.x and head.y == poison.y:
            snake.shrink()
            poison.spawn(walls)

            if len(snake.body) <= 1:
                running = False

        if power is None:
            if random.randint(1, 100) == 1:
                power = PowerUp(walls)

        if power is not None:
            now = pygame.time.get_ticks()

            if now - power.spawn_time > 8000:
                power = None

            elif head.x == power.x and head.y == power.y:
                active_power = power.type
                power_start = pygame.time.get_ticks()

                if active_power == "speed":
                    speed += 5
                elif active_power == "slow":
                    speed = max(5, speed - 5)
                elif active_power == "shield":
                    snake.shield = True

                power = None

        if active_power is not None:
            now = pygame.time.get_ticks()

            if now - power_start > 5000:
                if active_power == "speed":
                    speed = max(FPS, speed - 5)
                elif active_power == "slow":
                    speed += 5

                active_power = None

        screen.fill(WHITE)

        if settings["grid"]:
            draw_grid(screen)

        draw_snake(screen, snake, settings["snake_color"])
        draw_food(screen, food)
        draw_poison(screen, poison)

        if power is not None:
            draw_power(screen, power)

        draw_walls(screen, walls)

        info = f"Player: {username}  Score: {score}  Level: {level}  Best: {best}"
        text = font.render(info, True, BLACK)
        screen.blit(text, (10, 10))

        if snake.shield:
            shield_text = font.render("SHIELD", True, BLUE)
            screen.blit(shield_text, (10, 35))

        pygame.display.update()

    return score, level, "game_over"