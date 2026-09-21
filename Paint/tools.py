import pygame
from collections import deque


def draw_pencil(surface, color, start, end, size):
    pygame.draw.line(surface, color, start, end, size)


def draw_line(surface, color, start, end, size):
    pygame.draw.line(surface, color, start, end, size)


def draw_rect(surface, color, start, end, size):
    x1, y1 = start
    x2, y2 = end
    rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
    pygame.draw.rect(surface, color, rect, size)


def draw_circle(surface, color, start, end, size):
    x1, y1 = start
    x2, y2 = end
    radius = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
    pygame.draw.circle(surface, color, start, radius, size)


def draw_square(surface, color, start, end, size):
    x1, y1 = start
    x2, y2 = end

    side = min(abs(x2 - x1), abs(y2 - y1))

    if x2 < x1:
        side = -side

    rect = pygame.Rect(x1, y1, side, side)
    rect.normalize()
    pygame.draw.rect(surface, color, rect, size)


def draw_right_triangle(surface, color, start, end, size):
    x1, y1 = start
    x2, y2 = end
    points = [(x1, y1), (x1, y2), (x2, y2)]
    pygame.draw.polygon(surface, color, points, size)


def draw_equilateral_triangle(surface, color, start, end, size):
    x1, y1 = start
    x2, y2 = end

    side = abs(x2 - x1)
    height = int(side * 0.866)

    points = [
        (x1, y2),
        (x2, y2),
        ((x1 + x2) // 2, y2 - height)
    ]

    pygame.draw.polygon(surface, color, points, size)


def draw_rhombus(surface, color, start, end, size):
    x1, y1 = start
    x2, y2 = end

    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2

    points = [
        (cx, y1),
        (x2, cy),
        (cx, y2),
        (x1, cy)
    ]

    pygame.draw.polygon(surface, color, points, size)


def flood_fill(surface, pos, new_color):
    width, height = surface.get_size()
    x, y = pos

    if x < 0 or x >= width or y < 0 or y >= height:
        return

    old_color = surface.get_at((x, y))

    if old_color == new_color:
        return

    q = deque()
    q.append((x, y))

    while q:
        x, y = q.popleft()

        if x < 0 or x >= width or y < 0 or y >= height:
            continue

        if surface.get_at((x, y)) != old_color:
            continue

        surface.set_at((x, y), new_color)

        q.append((x + 1, y))
        q.append((x - 1, y))
        q.append((x, y + 1))
        q.append((x, y - 1))