import pygame
import random
import sys
from persistence import save_score
from ui import game_over_screen

WIDTH = 400
HEIGHT = 600
FPS = 60

ROAD_X = 50
ROAD_WIDTH = 300
LINE_WIDTH = 6

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (120, 120, 120)
DARK_GRAY = (60, 60, 60)
RED = (220, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 215, 0)
GREEN = (0, 180, 0)
ORANGE = (255, 120, 0)
PURPLE = (150, 0, 255)


def get_car_color(name):
    if name == "red":
        return RED
    if name == "yellow":
        return YELLOW
    return BLUE


class Player(pygame.sprite.Sprite):
    def __init__(self, color):
        super().__init__()

        self.image = pygame.Surface((50, 90), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, (0, 0, 50, 90), border_radius=10)
        pygame.draw.rect(self.image, BLACK, (8, 10, 34, 20), border_radius=5)
        pygame.draw.rect(self.image, BLACK, (8, 60, 34, 20), border_radius=5)

        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 20

        self.speed = 6

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed

        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        if self.rect.left < ROAD_X:
            self.rect.left = ROAD_X

        if self.rect.right > ROAD_X + ROAD_WIDTH:
            self.rect.right = ROAD_X + ROAD_WIDTH


class Enemy(pygame.sprite.Sprite):
    def __init__(self, difficulty):
        super().__init__()

        self.image = pygame.Surface((50, 90), pygame.SRCALPHA)
        pygame.draw.rect(self.image, RED, (0, 0, 50, 90), border_radius=10)
        pygame.draw.rect(self.image, BLACK, (8, 10, 34, 20), border_radius=5)
        pygame.draw.rect(self.image, BLACK, (8, 60, 34, 20), border_radius=5)

        self.rect = self.image.get_rect()
        self.difficulty = difficulty
        self.speed = random.randint(5, 8)
        self.reset_position()

    def reset_position(self):
        self.rect.x = random.randint(ROAD_X, ROAD_X + ROAD_WIDTH - self.rect.width)
        self.rect.y = random.randint(-500, -100)

    def update(self):
        self.rect.y += self.speed

        if self.rect.top > HEIGHT:
            self.reset_position()
            self.speed = random.randint(5, 9)


class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        size = 26
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (size // 2, size // 2), size // 2)
        pygame.draw.circle(self.image, BLACK, (size // 2, size // 2), size // 2, 2)

        self.rect = self.image.get_rect()
        self.speed = 6
        self.value = random.choice([1, 2, 3])
        self.reset_position()

    def reset_position(self):
        self.rect.x = random.randint(ROAD_X, ROAD_X + ROAD_WIDTH - self.rect.width)
        self.rect.y = random.randint(-600, -100)
        self.value = random.choice([1, 2, 3])

    def update(self):
        self.rect.y += self.speed

        if self.rect.top > HEIGHT:
            self.reset_position()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.Surface((45, 45), pygame.SRCALPHA)
        pygame.draw.rect(self.image, ORANGE, (0, 0, 45, 45), border_radius=8)
        pygame.draw.line(self.image, BLACK, (5, 5), (40, 40), 4)
        pygame.draw.line(self.image, BLACK, (40, 5), (5, 40), 4)

        self.rect = self.image.get_rect()
        self.speed = 6
        self.reset_position()

    def reset_position(self):
        self.rect.x = random.randint(ROAD_X, ROAD_X + ROAD_WIDTH - self.rect.width)
        self.rect.y = random.randint(-800, -150)

    def update(self):
        self.rect.y += self.speed

        if self.rect.top > HEIGHT:
            self.reset_position()


class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.types = ["nitro", "shield", "repair"]
        self.type = random.choice(self.types)

        self.image = pygame.Surface((35, 35), pygame.SRCALPHA)
        self.draw_powerup()

        self.rect = self.image.get_rect()
        self.speed = 6
        self.reset_position()

    def draw_powerup(self):
        self.image.fill((0, 0, 0, 0))

        if self.type == "nitro":
            color = PURPLE
            letter = "N"
        elif self.type == "shield":
            color = BLUE
            letter = "S"
        else:
            color = GREEN
            letter = "R"

        pygame.draw.circle(self.image, color, (17, 17), 17)
        pygame.draw.circle(self.image, BLACK, (17, 17), 17, 2)

        font = pygame.font.SysFont("Arial", 20)
        text = font.render(letter, True, WHITE)
        self.image.blit(text, (17 - text.get_width() // 2, 17 - text.get_height() // 2))

    def reset_position(self):
        self.type = random.choice(self.types)
        self.draw_powerup()
        self.rect.x = random.randint(ROAD_X, ROAD_X + ROAD_WIDTH - self.rect.width)
        self.rect.y = random.randint(-1000, -300)

    def update(self):
        self.rect.y += self.speed

        if self.rect.top > HEIGHT:
            self.reset_position()


class RacerGame:
    def __init__(self, screen, settings, player_name):
        self.screen = screen
        self.settings = settings
        self.player_name = player_name

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 22)
        self.big_font = pygame.font.SysFont("Arial", 36)

        self.line_y = 0
        self.road_speed = 6

        self.score = 0
        self.coins = 0
        self.distance = 0
        self.score_timer = 0

        self.active_power = None
        self.power_timer = 0
        self.shield = False

        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.coins_group = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        color = get_car_color(settings["car_color"])
        self.player = Player(color)
        self.all_sprites.add(self.player)

        self.create_objects()

    def create_objects(self):
        enemy_count = 3

        if self.settings["difficulty"] == "easy":
            enemy_count = 2
        elif self.settings["difficulty"] == "hard":
            enemy_count = 5

        for _ in range(enemy_count):
            enemy = Enemy(self.settings["difficulty"])
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

        for _ in range(2):
            coin = Coin()
            self.coins_group.add(coin)
            self.all_sprites.add(coin)

        for _ in range(2):
            obstacle = Obstacle()
            self.obstacles.add(obstacle)
            self.all_sprites.add(obstacle)

        powerup = PowerUp()
        self.powerups.add(powerup)
        self.all_sprites.add(powerup)

    def draw_road(self):
        self.screen.fill(GREEN)

        pygame.draw.rect(self.screen, DARK_GRAY, (ROAD_X, 0, ROAD_WIDTH, HEIGHT))

        pygame.draw.line(self.screen, WHITE, (ROAD_X, 0), (ROAD_X, HEIGHT), 4)
        pygame.draw.line(self.screen, WHITE, (ROAD_X + ROAD_WIDTH, 0), (ROAD_X + ROAD_WIDTH, HEIGHT), 4)

        self.line_y += self.road_speed
        if self.line_y >= 40:
            self.line_y = 0

        for y in range(-40, HEIGHT, 40):
            pygame.draw.rect(
                self.screen,
                WHITE,
                (WIDTH // 2 - LINE_WIDTH // 2, y + self.line_y, LINE_WIDTH, 25)
            )

    def draw_hud(self):
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        coin_text = self.font.render(f"Coins: {self.coins}", True, YELLOW)
        distance_text = self.font.render(f"Dist: {self.distance}", True, WHITE)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(coin_text, (280, 10))
        self.screen.blit(distance_text, (10, 40))

        if self.active_power:
            power_text = self.font.render(f"Power: {self.active_power}", True, YELLOW)
            self.screen.blit(power_text, (10, 70))

        if self.shield:
            shield_text = self.font.render("Shield: ON", True, BLUE)
            self.screen.blit(shield_text, (250, 40))

    def update_score(self):
        self.score_timer += 1

        if self.score_timer >= FPS // 2:
            self.distance += 1
            self.score += 1
            self.score_timer = 0

        self.score = self.distance + self.coins * 5

    def apply_powerup(self, power_type):
        self.active_power = power_type
        self.power_timer = FPS * 4

        if power_type == "nitro":
            self.road_speed = 10
            for enemy in self.enemies:
                enemy.speed += 2

        elif power_type == "shield":
            self.shield = True

        elif power_type == "repair":
            for obstacle in self.obstacles:
                obstacle.reset_position()

    def update_powerup_timer(self):
        if self.active_power:
            self.power_timer -= 1

            if self.power_timer <= 0:
                if self.active_power == "nitro":
                    self.road_speed = 6

                self.active_power = None

    def increase_difficulty(self):
        if self.distance > 0 and self.distance % 50 == 0:
            for enemy in self.enemies:
                enemy.speed += 0.01

    def check_collisions(self):
        if pygame.sprite.spritecollideany(self.player, self.enemies):
            if self.shield:
                self.shield = False
                for enemy in self.enemies:
                    if self.player.rect.colliderect(enemy.rect):
                        enemy.reset_position()
                return False
            return True

        if pygame.sprite.spritecollideany(self.player, self.obstacles):
            if self.shield:
                self.shield = False
                for obstacle in self.obstacles:
                    if self.player.rect.colliderect(obstacle.rect):
                        obstacle.reset_position()
                return False
            return True

        collected_coins = pygame.sprite.spritecollide(self.player, self.coins_group, False)
        for coin in collected_coins:
            self.coins += coin.value
            coin.reset_position()

        collected_powerups = pygame.sprite.spritecollide(self.player, self.powerups, False)
        for powerup in collected_powerups:
            self.apply_powerup(powerup.type)
            powerup.reset_position()

        return False

    def run(self):
        while True:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.all_sprites.update()
            self.update_score()
            self.update_powerup_timer()
            self.increase_difficulty()

            is_dead = self.check_collisions()

            self.draw_road()
            self.all_sprites.draw(self.screen)
            self.draw_hud()

            pygame.display.flip()

            if is_dead:
                save_score(self.player_name, self.score, self.coins, self.distance)
                return game_over_screen(self.screen, self.score, self.coins, self.distance)