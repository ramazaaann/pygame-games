import pygame

from config import BLACK, BLUE, GRAY, GREEN, RED, WHITE


def draw_text(screen, text, size, x, y, color=BLACK):
    font = pygame.font.SysFont("Verdana", size)
    surface = font.render(text, True, color)
    screen.blit(surface, surface.get_rect(center=(x, y)))


def button(screen, text, x, y, w, h, events):
    """Draws a button; returns True when it was clicked this frame.
    Uses MOUSEBUTTONDOWN events instead of polling + sleeping, so the game never freezes."""
    rect = pygame.Rect(x, y, w, h)
    hover = rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(screen, GRAY if hover else WHITE, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    draw_text(screen, text, 22, x + w // 2, y + h // 2)
    return any(e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and rect.collidepoint(e.pos)
               for e in events)


def _quit_requested(events):
    return any(e.type == pygame.QUIT for e in events)


def main_menu(screen):
    while True:
        events = pygame.event.get()
        screen.fill((230, 230, 230))
        draw_text(screen, "SNAKE GAME", 40, 300, 90, GREEN)
        if button(screen, "Play (solo)", 200, 160, 200, 50, events):
            return "solo"
        if button(screen, "Play vs AI", 200, 225, 200, 50, events):
            return "ai"
        if button(screen, "Leaderboard", 200, 290, 200, 50, events):
            return "leaderboard"
        if button(screen, "Settings", 200, 355, 200, 50, events):
            return "settings"
        if button(screen, "Quit", 200, 420, 200, 50, events) or _quit_requested(events):
            return "quit"
        pygame.display.update()


def game_over_screen(screen, headline, score, level, best, ai_score=None):
    while True:
        events = pygame.event.get()
        screen.fill((240, 240, 240))
        draw_text(screen, headline, 40, 300, 100, RED)
        draw_text(screen, f"Score: {score}", 25, 300, 180)
        if ai_score is not None:
            draw_text(screen, f"AI score: {ai_score}", 25, 300, 215)
        draw_text(screen, f"Level: {level}", 25, 300, 250)
        draw_text(screen, f"Best: {best}", 25, 300, 285)
        if button(screen, "Retry", 200, 340, 200, 50, events):
            return "retry"
        if button(screen, "Main Menu", 200, 410, 200, 50, events):
            return "menu"
        if _quit_requested(events):
            return "quit"
        pygame.display.update()


def leaderboard_screen(screen, data):
    while True:
        events = pygame.event.get()
        screen.fill((240, 240, 240))
        draw_text(screen, "LEADERBOARD", 35, 300, 60, BLUE)
        if not data:
            draw_text(screen, "No scores yet", 22, 300, 200)
        y = 120
        for i, (username, score, level, mode) in enumerate(data):
            draw_text(screen, f"{i + 1}. {username} | {score} pts | lvl {level} | {mode}", 20, 300, y)
            y += 35
        if button(screen, "Back", 200, 500, 200, 50, events):
            return None
        if _quit_requested(events):
            return "quit"
        pygame.display.update()


def settings_screen(screen, settings):
    while True:
        events = pygame.event.get()
        screen.fill((240, 240, 240))
        draw_text(screen, "SETTINGS", 35, 300, 80, BLUE)
        if button(screen, "Grid: ON" if settings["grid"] else "Grid: OFF", 200, 180, 200, 50, events):
            settings["grid"] = not settings["grid"]
        if button(screen, "Sound: ON" if settings["sound"] else "Sound: OFF", 200, 250, 200, 50, events):
            settings["sound"] = not settings["sound"]
        if button(screen, "Green Snake", 200, 320, 200, 50, events):
            settings["snake_color"] = [0, 200, 0]
        if button(screen, "Blue Snake", 200, 390, 200, 50, events):
            settings["snake_color"] = [0, 100, 255]
        if button(screen, "Save & Back", 200, 470, 200, 50, events):
            return settings
        if _quit_requested(events):
            return "quit"
        pygame.display.update()
