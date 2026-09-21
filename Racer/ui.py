import pygame
import sys
from persistence import load_leaderboard, save_settings

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (120, 120, 120)
RED = (220, 0, 0)
YELLOW = (255, 215, 0)


def draw_text(screen, text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def main_menu(screen, settings):
    font = pygame.font.SysFont("Arial", 32)
    small_font = pygame.font.SysFont("Arial", 24)

    while True:
        screen.fill(BLACK)

        draw_text(screen, "RACER GAME", font, YELLOW, 105, 120)
        draw_text(screen, "1 - Play", small_font, WHITE, 140, 220)
        draw_text(screen, "2 - Leaderboard", small_font, WHITE, 140, 270)
        draw_text(screen, "3 - Settings", small_font, WHITE, 140, 320)
        draw_text(screen, "4 - Quit", small_font, WHITE, 140, 370)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "play"
                if event.key == pygame.K_2:
                    return "leaderboard"
                if event.key == pygame.K_3:
                    return "settings"
                if event.key == pygame.K_4:
                    pygame.quit()
                    sys.exit()


def leaderboard_screen(screen):
    font = pygame.font.SysFont("Arial", 32)
    small_font = pygame.font.SysFont("Arial", 22)

    leaderboard = load_leaderboard()

    while True:
        screen.fill(BLACK)

        draw_text(screen, "LEADERBOARD", font, YELLOW, 90, 50)

        y = 120
        if len(leaderboard) == 0:
            draw_text(screen, "No scores yet", small_font, WHITE, 130, y)
        else:
            for i, item in enumerate(leaderboard):
                text = f"{i + 1}. {item['name']} - {item['score']}"
                draw_text(screen, text, small_font, WHITE, 60, y)
                y += 35

        draw_text(screen, "Press ESC to go back", small_font, GRAY, 90, 540)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return


def settings_screen(screen, settings):
    font = pygame.font.SysFont("Arial", 32)
    small_font = pygame.font.SysFont("Arial", 22)

    colors = ["blue", "red", "yellow"]
    difficulties = ["easy", "normal", "hard"]

    while True:
        screen.fill(BLACK)

        draw_text(screen, "SETTINGS", font, YELLOW, 125, 70)

        draw_text(screen, f"1 - Sound: {settings['sound']}", small_font, WHITE, 70, 170)
        draw_text(screen, f"2 - Car color: {settings['car_color']}", small_font, WHITE, 70, 220)
        draw_text(screen, f"3 - Difficulty: {settings['difficulty']}", small_font, WHITE, 70, 270)

        draw_text(screen, "ESC - Back", small_font, GRAY, 130, 520)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    settings["sound"] = not settings["sound"]

                if event.key == pygame.K_2:
                    index = colors.index(settings["car_color"])
                    settings["car_color"] = colors[(index + 1) % len(colors)]

                if event.key == pygame.K_3:
                    index = difficulties.index(settings["difficulty"])
                    settings["difficulty"] = difficulties[(index + 1) % len(difficulties)]

                if event.key == pygame.K_ESCAPE:
                    save_settings(settings)
                    return


def get_player_name(screen):
    font = pygame.font.SysFont("Arial", 30)
    small_font = pygame.font.SysFont("Arial", 22)

    name = ""

    while True:
        screen.fill(BLACK)

        draw_text(screen, "Enter your name:", font, WHITE, 80, 200)
        draw_text(screen, name, font, YELLOW, 160, 260)
        draw_text(screen, "Press ENTER", small_font, GRAY, 130, 330)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if name == "":
                        return "Player"
                    return name

                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]

                else:
                    if len(name) < 10:
                        name += event.unicode


def game_over_screen(screen, score, coins, distance):
    font = pygame.font.SysFont("Arial", 32)
    small_font = pygame.font.SysFont("Arial", 22)

    while True:
        screen.fill(BLACK)

        draw_text(screen, "GAME OVER", font, RED, 105, 130)
        draw_text(screen, f"Score: {score}", small_font, WHITE, 130, 220)
        draw_text(screen, f"Coins: {coins}", small_font, YELLOW, 130, 260)
        draw_text(screen, f"Distance: {distance}", small_font, WHITE, 130, 300)

        draw_text(screen, "R - Retry", small_font, WHITE, 130, 390)
        draw_text(screen, "M - Main Menu", small_font, WHITE, 130, 430)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "retry"
                if event.key == pygame.K_m:
                    return "menu"