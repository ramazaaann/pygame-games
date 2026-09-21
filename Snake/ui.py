import pygame
from config import WHITE, BLACK, GRAY, GREEN, RED, BLUE


def draw_text(screen, text, size, x, y, color=BLACK):
    font = pygame.font.SysFont("Verdana", size)
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)


def button(screen, text, x, y, w, h):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    rect = pygame.Rect(x, y, w, h)

    if rect.collidepoint(mouse):
        pygame.draw.rect(screen, GRAY, rect)
        if click[0]:
            pygame.time.delay(200)
            return True
    else:
        pygame.draw.rect(screen, WHITE, rect)

    pygame.draw.rect(screen, BLACK, rect, 2)
    draw_text(screen, text, 22, x + w // 2, y + h // 2)

    return False


def main_menu(screen):
    while True:
        screen.fill((230, 230, 230))

        draw_text(screen, "SNAKE GAME", 40, 300, 100, GREEN)

        if button(screen, "Play", 200, 180, 200, 50):
            return "play"

        if button(screen, "Leaderboard", 200, 250, 200, 50):
            return "leaderboard"

        if button(screen, "Settings", 200, 320, 200, 50):
            return "settings"

        if button(screen, "Quit", 200, 390, 200, 50):
            return "quit"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

        pygame.display.update()


def game_over_screen(screen, score, level, best):
    while True:
        screen.fill((240, 240, 240))

        draw_text(screen, "GAME OVER", 40, 300, 100, RED)
        draw_text(screen, f"Score: {score}", 25, 300, 180)
        draw_text(screen, f"Level: {level}", 25, 300, 220)
        draw_text(screen, f"Best: {best}", 25, 300, 260)

        if button(screen, "Retry", 200, 330, 200, 50):
            return "retry"

        if button(screen, "Main Menu", 200, 400, 200, 50):
            return "menu"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

        pygame.display.update()


def leaderboard_screen(screen, data):
    while True:
        screen.fill((240, 240, 240))

        draw_text(screen, "LEADERBOARD", 35, 300, 60, BLUE)

        y = 120
        for i, row in enumerate(data):
            username, score, level = row
            text = f"{i + 1}. {username} | Score: {score} | Level: {level}"
            draw_text(screen, text, 20, 300, y)
            y += 35

        if button(screen, "Back", 200, 500, 200, 50):
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

        pygame.display.update()


def settings_screen(screen, settings):
    while True:
        screen.fill((240, 240, 240))

        draw_text(screen, "SETTINGS", 35, 300, 80, BLUE)

        grid_text = "Grid: ON" if settings["grid"] else "Grid: OFF"
        sound_text = "Sound: ON" if settings["sound"] else "Sound: OFF"

        if button(screen, grid_text, 200, 180, 200, 50):
            settings["grid"] = not settings["grid"]

        if button(screen, sound_text, 200, 250, 200, 50):
            settings["sound"] = not settings["sound"]

        if button(screen, "Green Snake", 200, 320, 200, 50):
            settings["snake_color"] = [0, 200, 0]

        if button(screen, "Blue Snake", 200, 390, 200, 50):
            settings["snake_color"] = [0, 100, 255]

        if button(screen, "Save & Back", 200, 470, 200, 50):
            return settings

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

        pygame.display.update()