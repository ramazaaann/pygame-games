import pygame
import sys

from persistence import load_settings
from ui import main_menu, leaderboard_screen, settings_screen, get_player_name
from racer import RacerGame

pygame.init()

WIDTH = 400
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer Game")

settings = load_settings()

while True:
    action = main_menu(screen, settings)

    if action == "play":
        player_name = get_player_name(screen)

        while True:
            game = RacerGame(screen, settings, player_name)
            result = game.run()

            if result == "retry":
                continue

            if result == "menu":
                break

    elif action == "leaderboard":
        leaderboard_screen(screen)

    elif action == "settings":
        settings_screen(screen, settings)