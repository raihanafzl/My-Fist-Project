import pygame
import sys
import random
import math

pygame.init()

WIDTH = 808
HEIGHT = 600

bg = pygame.image.load("background game.jpg")
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("THATS MY COIN! - Player vs BOT")

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)

def reset_game():
    p1 = Player1(800, 0)
    p2 = Bot(0, 0)
    coin = Coin(random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50))
    start_time = pygame.time.get_ticks() 
    return p1, p2, coin, 0, 0, False, start_time

def draw_button(surface, text, x, y, w, h, color=(0, 200, 0)):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, BLACK, rect, 3)

    font = pygame.font.Font(None, 40)
    txt = font.render(text, True, WHITE)
    text_rect = txt.get_rect(center=rect.center)
    surface.blit(txt, text_rect)

    return rect

# ================== WALL ==================
class Wall:
    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)

    def draw(self, surface):
        pygame.draw.rect(surface, BLACK, self.rect)

walls = []
TILE = 5

# ================== MAP ==================
for x in range(700, 808, TILE):  # Tembok vertikal kanan (atas)
    walls.append(Wall(x, 40, TILE))

for x in range(0, 108, TILE):    # Tembok vertikal kiri (atas)
    walls.append(Wall(x, 40, TILE))

# Tembok vertikal tengah
for y in range(20, 50, TILE):
    walls.append(Wall(400, y, TILE))
for y in range(200, 250, TILE):
    walls.append(Wall(400, y, TILE))
for y in range(400, 450, TILE):
    walls.append(Wall(400, y, TILE))
for y in range(550, 600, TILE):
    walls.append(Wall(400, y, TILE))

# Tembok vertikal kiri
for y in range(200, 300, TILE):
    walls.append(Wall(200, y, TILE))
for y in range(400, 450, TILE):
    walls.append(Wall(200, y, TILE))

# Tembok vertikal kanan
for y in range(200, 300, TILE):
    walls.append(Wall(600, y, TILE))
for y in range(400, 450, TILE):
    walls.append(Wall(600, y, TILE))

# ================== CHARACTER ==================
class Character:
    def __init__(self, x, y, color, speed=5):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.speed = speed
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color,
                         (self.x, self.y, self.width, self.height))

    def batasan(self):
        if self.x < 0:
            self.x = 0
        if self.x + self.width > WIDTH:
            self.x = WIDTH - self.width
        if self.y < 0:
            self.y = 0
        if self.y + self.height > HEIGHT:
            self.y = HEIGHT - self.height

    def collision(self, walls, old_x, old_y):
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for wall in walls:
            if player_rect.colliderect(wall.rect):
                self.x = old_x
                self.y = old_y
                return True  # Mengembalikan True jika tabrakan
        return False

    def will_collide(self, walls, new_x, new_y):
        """Cek apakah posisi baru akan bertabrakan dengan tembok"""
        test_rect = pygame.Rect(new_x, new_y, self.width, self.height)
        for wall in walls:
            if test_rect.colliderect(wall.rect):
                return True
        return False

# ================== PLAYER 1 (MANUAL) ==================
class Player1(Character):
    def __init__(self, x, y):
        super().__init__(x, y, BLUE, speed=5)

    def gerakan(self, keys, walls):
        old_x = self.x
        old_y = self.y

        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        if keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.y += self.speed

        self.collision(walls, old_x, old_y)

# ================== BOT (Player 2) ==================
class Bot(Character):
    def __init__(self, x, y):
        super().__init__(x, y, RED, speed=4)
        self.last_direction_change = 0
        self.avoid_timer = 0  # Timer untuk menghindar
        self.avoid_dx = 0
        self.avoid_dy = 0
        
    def gerakan_bot(self, coin, walls):
        old_x = self.x
        old_y = self.y
        
        if self.avoid_timer > 0:
            self.avoid_timer -= 1
            # Gerak ke arah avoid
            self.x += self.avoid_dx
            self.y += self.avoid_dy
            
            if self.collision(walls, old_x, old_y):
                self.avoid_timer = 0
            else:
                self.batasan()
                return
        
        coin_center_x = coin.rect.x + coin.rect.width // 2
        coin_center_y = coin.rect.y + coin.rect.height // 2
        bot_center_x = self.x + self.width // 2
        bot_center_y = self.y + self.height // 2
        
        # Vektor arah ke koin
        dx = coin_center_x - bot_center_x
        dy = coin_center_y - bot_center_y
        
        # Normalisasi
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            dx = dx / distance
            dy = dy / distance
            
            # Gerak ke arah koin
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
            if self.will_collide(walls, new_x, new_y):
                if not self.will_collide(walls, new_x, self.y):
                    new_y = self.y
                elif not self.will_collide(walls, self.x, new_y):
                    new_x = self.x
                else:
                    new_x, new_y = self.x, self.y
            
            self.x = new_x
            self.y = new_y
            
            # Cek collision/tabrakan
            if self.collision(walls, old_x, old_y):
                self.avoid_timer = 10
                # Cari arah untuk menghindar
                for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
                    rad = math.radians(angle)
                    self.avoid_dx = math.cos(rad) * self.speed
                    self.avoid_dy = math.sin(rad) * self.speed
                    test_x = self.x + self.avoid_dx
                    test_y = self.y + self.avoid_dy
                    if not self.will_collide(walls, test_x, test_y):
                        break
        
        self.batasan()

# ================== COIN ==================
class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)

    def draw(self, surface):
        pygame.draw.rect(surface, GOLD, self.rect)

# ================== INIT ==================
player1, bot, coin, score1, score2, game_over, game_start_time = reset_game()

GAME_DURATION = 30
clock = pygame.time.Clock()
running = True

MENU = 0
PLAYING = 1
GAME_OVER = 2

game_state = MENU

# ================== GAME LOOP ==================
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if game_state == MENU:
                if start_button.collidepoint(mouse_pos):
                    game_state = PLAYING
                    player1, bot, coin, score1, score2, game_over, game_start_time = reset_game()
                    game_over = False
                    
            elif game_state == GAME_OVER:
                if replay_button.collidepoint(mouse_pos):
                    game_state = MENU

    if game_state == PLAYING and not game_over:
        keys = pygame.key.get_pressed()
        
        # Player 1 gerakan manual
        player1.gerakan(keys, walls)
        
        # Bot gerakan otomatis dengan deteksi tembok
        bot.gerakan_bot(coin, walls)

        player1.batasan()
        bot.batasan()

        rect1 = pygame.Rect(player1.x, player1.y, player1.width, player1.height)
        rect2 = pygame.Rect(bot.x, bot.y, bot.width, bot.height)

        # Player 1 ambil coin
        if rect1.colliderect(coin.rect):
            score1 += 1
            coin = Coin(random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50))

        # Bot ambil coin
        if rect2.colliderect(coin.rect):
            score2 += 1
            coin = Coin(random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50))

        # TIMER
        elapsed_time = (pygame.time.get_ticks() - game_start_time) // 1000
        remaining_time = max(0, GAME_DURATION - elapsed_time)

        if remaining_time == 0:
            game_over = True
            game_state = GAME_OVER

    # ================== DRAW ==================
    screen.blit(bg, (0, 0))

    if game_state == MENU:
        font_title = pygame.font.Font(None, 80)
        title_text = font_title.render("THATS MY COIN!", True, GOLD)
        title_rect = title_text.get_rect(center=(WIDTH//2, 100))
        screen.blit(title_text, title_rect)
        
        start_button = draw_button(screen, "MULAI", WIDTH//2 - 100, 250, 200, 60, (0, 150, 0))
        
        font_info = pygame.font.Font(None, 32)
        info1 = font_info.render("PLAYER (BLUE): Tanda Panah", True, BLACK)
        info2 = font_info.render("BOT (RED): Computer", True, BLACK)
        info3 = font_info.render("Kumpulkan koin sebanyak-banyaknya dalam 30 detik!", True, BLACK)
        
        screen.blit(info1, (WIDTH//2 - info1.get_width()//2, 360))
        screen.blit(info2, (WIDTH//2 - info2.get_width()//2, 400))
        screen.blit(info3, (WIDTH//2 - info3.get_width()//2, 440))
        
    elif game_state == PLAYING:
        for wall in walls:
            wall.draw(screen)

        coin.draw(screen)
        player1.draw(screen)
        bot.draw(screen)
        
        font = pygame.font.Font(None, 24)
        player_label = font.render("PLAYER", True, BLUE)
        bot_label = font.render("BOT", True, RED)
        screen.blit(player_label, (player1.x, player1.y - 20))
        screen.blit(bot_label, (bot.x, bot.y - 20))

        font_score = pygame.font.Font(None, 36)
        score_text = font_score.render(f"BOT: {score2}  |  PLAYER: {score1}", True, BLACK)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 10))

        elapsed_time = (pygame.time.get_ticks() - game_start_time) // 1000
        remaining_time = max(0, GAME_DURATION - elapsed_time)
        timer_text = font_score.render(f"Time: {remaining_time}", True, BLACK)
        screen.blit(timer_text, (10, 10))
        
    elif game_state == GAME_OVER:
        for wall in walls:
            wall.draw(screen)
        coin.draw(screen)
        player1.draw(screen)
        bot.draw(screen)
        
        font_score = pygame.font.Font(None, 36)
        score_text = font_score.render(f"BOT: {score2}  |  PLAYER: {score1}", True, BLACK)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 10))
        
        font_big = pygame.font.Font(None, 60)
        
        if score1 > score2:
            result = "KAMU MENANG!"
            result_color = (0, 200, 0)
        elif score2 > score1:
            result = "BOT MENANG!"
            result_color = RED
        else:
            result = "DRAW!"
            result_color = GOLD

        result_text = font_big.render(result, True, result_color)
        screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, 200))
        
        replay_button = draw_button(screen, "BACK TO MENU", WIDTH//2 - 100, 300, 200, 50, (0, 150, 0))

    pygame.display.flip()

pygame.quit()
sys.exit()