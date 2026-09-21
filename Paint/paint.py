import pygame
from datetime import datetime
import tools

pygame.init()

WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint TSIS2")

canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill((255, 255, 255))

font = pygame.font.SysFont("Arial", 24)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

colors = [BLACK, RED, GREEN, BLUE, YELLOW]
current_color = BLACK

tool = "pencil"
brush_size = 5

drawing = False
start_pos = None
last_pos = None

text_mode = False
text = ""
text_pos = None

clock = pygame.time.Clock()


def draw_ui():
    pygame.draw.rect(screen, (220, 220, 220), (0, 0, WIDTH, 60))

    x = 10
    for color in colors:
        pygame.draw.rect(screen, color, (x, 10, 40, 40))

        if color == current_color:
            pygame.draw.rect(screen, BLACK, (x, 10, 40, 40), 3)

        x += 50

    info = "Tool: " + tool + " | Size: " + str(brush_size)
    text_surface = font.render(info, True, BLACK)
    screen.blit(text_surface, (300, 17))


def draw_selected_tool(surface, start, end):
    if tool == "line":
        tools.draw_line(surface, current_color, start, end, brush_size)

    elif tool == "rect":
        tools.draw_rect(surface, current_color, start, end, brush_size)

    elif tool == "circle":
        tools.draw_circle(surface, current_color, start, end, brush_size)

    elif tool == "square":
        tools.draw_square(surface, current_color, start, end, brush_size)

    elif tool == "right_triangle":
        tools.draw_right_triangle(surface, current_color, start, end, brush_size)

    elif tool == "equilateral_triangle":
        tools.draw_equilateral_triangle(surface, current_color, start, end, brush_size)

    elif tool == "rhombus":
        tools.draw_rhombus(surface, current_color, start, end, brush_size)


running = True

while running:
    mouse_pos = pygame.mouse.get_pos()

    screen.blit(canvas, (0, 0))

    if drawing and start_pos and tool not in ["pencil", "eraser", "fill", "text"]:
        temp_canvas = canvas.copy()
        draw_selected_tool(temp_canvas, start_pos, mouse_pos)
        screen.blit(temp_canvas, (0, 0))

    draw_ui()

    if text_mode:
        text_surface = font.render(text, True, current_color)
        screen.blit(text_surface, text_pos)

    pygame.display.flip()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if text_mode:
                if event.key == pygame.K_RETURN:
                    text_surface = font.render(text, True, current_color)
                    canvas.blit(text_surface, text_pos)

                    text_mode = False
                    text = ""
                    text_pos = None

                elif event.key == pygame.K_ESCAPE:
                    text_mode = False
                    text = ""
                    text_pos = None

                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]

                else:
                    text += event.unicode

            else:
                if event.key == pygame.K_p:
                    tool = "pencil"

                elif event.key == pygame.K_l:
                    tool = "line"

                elif event.key == pygame.K_r:
                    tool = "rect"

                elif event.key == pygame.K_c:
                    tool = "circle"

                elif event.key == pygame.K_e:
                    tool = "eraser"

                elif event.key == pygame.K_f:
                    tool = "fill"

                elif event.key == pygame.K_t:
                    tool = "text"

                elif event.key == pygame.K_s:
                    tool = "square"

                elif event.key == pygame.K_4:
                    tool = "right_triangle"

                elif event.key == pygame.K_5:
                    tool = "equilateral_triangle"

                elif event.key == pygame.K_6:
                    tool = "rhombus"

                elif event.key == pygame.K_1:
                    brush_size = 2

                elif event.key == pygame.K_2:
                    brush_size = 5

                elif event.key == pygame.K_3:
                    brush_size = 10

                if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_META:
                    filename = "paint_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
                    pygame.image.save(canvas, filename)
                    print("Saved:", filename)

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:
                x, y = event.pos

                if y <= 60:
                    for i in range(len(colors)):
                        color_x = 10 + i * 50

                        if color_x <= x <= color_x + 40:
                            current_color = colors[i]

                else:
                    if tool == "fill":
                        tools.flood_fill(canvas, event.pos, current_color)

                    elif tool == "text":
                        text_mode = True
                        text = ""
                        text_pos = event.pos

                    else:
                        drawing = True
                        start_pos = event.pos
                        last_pos = event.pos

        if event.type == pygame.MOUSEMOTION:

            if drawing:
                if tool == "pencil":
                    tools.draw_pencil(canvas, current_color, last_pos, event.pos, brush_size)
                    last_pos = event.pos

                elif tool == "eraser":
                    tools.draw_pencil(canvas, WHITE, last_pos, event.pos, brush_size)
                    last_pos = event.pos

        if event.type == pygame.MOUSEBUTTONUP:

            if event.button == 1 and drawing:
                if tool not in ["pencil", "eraser", "fill", "text"]:
                    draw_selected_tool(canvas, start_pos, event.pos)

                drawing = False
                start_pos = None
                last_pos = None

    clock.tick(60)

pygame.quit()