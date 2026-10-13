import sys

import pygame

import db
from config import HEIGHT, WIDTH
from game import run_game
from settings import load_settings, save_settings
from ui import game_over_screen, leaderboard_screen, main_menu, settings_screen


def get_username(screen):
    font = pygame.font.SysFont("Verdana", 25)
    username = ""
    while True:
        screen.fill((240, 240, 240))
        screen.blit(font.render("Enter username:", True, (0, 0, 0)), (180, 180))
        screen.blit(font.render(username, True, (0, 0, 255)), (180, 230))
        screen.blit(font.render("Press ENTER to continue", True, (100, 100, 100)), (140, 300))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username.strip():
                    return username.strip()
                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.unicode.isprintable() and len(username) < 15:
                    username += event.unicode
        pygame.display.update()


def headline_for(state):
    if state.mode == "solo":
        return "GAME OVER"
    return {"player": "YOU WIN!", "ai": "AI WINS", "draw": "DRAW"}.get(state.winner, "GAME OVER")


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake")

    db.init()  # the game still runs if PostgreSQL is not available
    username = get_username(screen)

    while True:
        choice = main_menu(screen)
        if choice == "quit":
            break

        if choice in ("solo", "ai"):
            while True:
                best = db.get_personal_best(username)
                state, status = run_game(screen, username, best, choice)
                if status == "quit":
                    pygame.quit()
                    sys.exit()
                won = None if choice == "solo" or state.winner == "draw" else state.winner == "player"
                db.save_result(username, state.score, state.level, choice, won)
                result = game_over_screen(screen, headline_for(state), state.score, state.level,
                                          max(best, state.score),
                                          state.ai_score if choice == "ai" else None)
                if result == "quit":
                    pygame.quit()
                    sys.exit()
                if result == "menu":
                    break

        elif choice == "leaderboard":
            if leaderboard_screen(screen, db.get_leaderboard()) == "quit":
                break

        elif choice == "settings":
            result = settings_screen(screen, load_settings())
            if result == "quit":
                break
            save_settings(result)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
