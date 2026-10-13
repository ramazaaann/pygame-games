"""pygame layer: input, rendering and the frame loop. All rules live in snake_logic.py."""
import pygame

from config import (BLACK, BLUE, CELL, COLS, DARK_RED, FPS, GRAY, HEIGHT, ORANGE, PURPLE, RED,
                    ROWS, WHITE, WIDTH, YELLOW)
from settings import load_settings
from snake_logic import DOWN, LEFT, RIGHT, UP, GameState

KEYS = {
    pygame.K_UP: UP, pygame.K_DOWN: DOWN, pygame.K_LEFT: LEFT, pygame.K_RIGHT: RIGHT,
    pygame.K_w: UP, pygame.K_s: DOWN, pygame.K_a: LEFT, pygame.K_d: RIGHT,
}
POWER_COLORS = {"speed": BLUE, "slow": PURPLE, "shield": YELLOW}


def cell_rect(cell):
    return (cell[0] * CELL, cell[1] * CELL, CELL, CELL)


def draw_grid(screen):
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))


def draw_snake(screen, snake, color):
    for cell in snake.body:
        pygame.draw.rect(screen, color, cell_rect(cell))
    pygame.draw.rect(screen, BLACK, cell_rect(snake.head), 2)  # mark the head


def draw(screen, state, settings, font, username, best):
    screen.fill(WHITE)
    if settings["grid"]:
        draw_grid(screen)
    for wall in state.walls:
        pygame.draw.rect(screen, BLACK, cell_rect(wall))
    if state.food:
        pygame.draw.rect(screen, RED, cell_rect(state.food))
    if state.poison:
        pygame.draw.rect(screen, DARK_RED, cell_rect(state.poison))
    if state.power:
        pygame.draw.rect(screen, POWER_COLORS[state.power["kind"]], cell_rect(state.power["cell"]))
    draw_snake(screen, state.player, settings["snake_color"])
    if state.ai:
        draw_snake(screen, state.ai, ORANGE)

    info = f"{username}: {state.score}"
    if state.ai:
        info += f"   AI: {state.ai_score}"
    info += f"   Level: {state.level}   Best: {best}"
    screen.blit(font.render(info, True, BLACK), (10, 10))
    if state.player.shield:
        screen.blit(font.render("SHIELD", True, BLUE), (10, 35))
    if state.active:
        screen.blit(font.render(state.active["kind"].upper(), True, PURPLE), (120, 35))
    pygame.display.update()


def run_game(screen, username, best, mode="solo"):
    """Returns (state, status) where status is "quit" or "game_over"."""
    settings = load_settings()
    state = GameState(COLS, ROWS, FPS, mode)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Verdana", 18)

    while state.status == "running":
        clock.tick(state.current_fps())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return state, "quit"
            if event.type == pygame.KEYDOWN and event.key in KEYS:
                state.player.turn(KEYS[event.key])
        state.step(pygame.time.get_ticks())
        draw(screen, state, settings, font, username, best)
    return state, "game_over"
