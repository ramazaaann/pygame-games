import pygame
import sys
from config import WIDTH, HEIGHT
from db import create_tables, save_result, get_leaderboard, get_personal_best
from game import run_game, load_settings, save_settings
from ui import main_menu, game_over_screen, leaderboard_screen, settings_screen


def get_username(screen):
    font = pygame.font.SysFont("Verdana", 25)
    username = ""

    while True:
        screen.fill((240, 240, 240))

        title = font.render("Enter username:", True, (0, 0, 0))
        text = font.render(username, True, (0, 0, 255))
        hint = font.render("Press ENTER to continue", True, (100, 100, 100))

        screen.blit(title, (180, 180))
        screen.blit(text, (180, 230))
        screen.blit(hint, (140, 300))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if username.strip() != "":
                        return username

                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]

                else:
                    if len(username) < 15:
                        username += event.unicode

        pygame.display.update()


def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Game TSIS4")

    create_tables()

    username = get_username(screen)

    while True:
        choice = main_menu(screen)

        if choice == "play":
            best = get_personal_best(username)
            score, level, status = run_game(screen, username, best)

            if status == "quit":
                break

            save_result(username, score, level)
            best = get_personal_best(username)

            result = game_over_screen(screen, score, level, best)

            if result == "quit":
                break

        elif choice == "leaderboard":
            data = get_leaderboard()
            result = leaderboard_screen(screen, data)

            if result == "quit":
                break

        elif choice == "settings":
            settings = load_settings()
            result = settings_screen(screen, settings)

            if result != "quit":
                save_settings(result)
            else:
                break

        elif choice == "quit":
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()