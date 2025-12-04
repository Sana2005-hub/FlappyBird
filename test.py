import pygame
import sys
import random
import os
pygame.init()
# Screen Setting
WIDTH, HEIGHT = 1200, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Adventure Game")
clock = pygame.time.Clock()
# Sound Effects
os.makedirs("data", exist_ok=True)
flap_s = pygame.mixer.Sound("flap.wav")
score_s = pygame.mixer.Sound("score.wav")
hit_s = pygame.mixer.Sound("hit.wav")
# Highscore system
hs_file = "data/highscore.txt"
if not os.path.exists(hs_file):
    with open(hs_file, "w") as f:
        f.write("0")
highscore = int(open(hs_file).read())
# Bird and Background
MENU_BG_FILE = "backgroung.png"
PIPE_FILE = "pipes.png"
THEME_MENU_FILE = "theme.jpg"
CLASSIC_BG_FILE = "classic.png"
FOREST_BG_FILE = "forest.png"
SPACE_BG_FILE = "space.png"
BIRD_FILE = "flapbird.png"
COIN_FILE = "coin.png"
SHIELD_FILE = "shield.png"
DOUBLE_COINS_FILE = "double_coin.png"
# Game Constants
GRAVITY = 0.5
JUMP_STRENGTH = -10
PIPE_WIDTH = 100
LEVELS = {
    "EASY": {"gap": 250, "speed": 5},
    "MEDIUM": {"gap": 210, "speed": 7},
    "HARD": {"gap": 170, "speed": 9},
}
THEMES = {
    "CLASSIC": {"bg": CLASSIC_BG_FILE, "pipe": PIPE_FILE},
    "FOREST": {"bg": FOREST_BG_FILE, "pipe": PIPE_FILE},
    "SPACE": {"bg": SPACE_BG_FILE, "pipe": PIPE_FILE},
}
unlocked_themes = {"CLASSIC"}
# Loading Images
menu_bg = pygame.image.load(MENU_BG_FILE)
menu_bg = pygame.transform.scale(menu_bg, (WIDTH, HEIGHT))
theme_file = pygame.image.load(THEME_MENU_FILE)
theme_file = pygame.transform.scale(theme_file, (WIDTH, HEIGHT))
bird_img = pygame.image.load(BIRD_FILE)
bird_img = pygame.transform.scale(bird_img, (70, 50))
coin_img = pygame.image.load(COIN_FILE)
coin_img = pygame.transform.scale(coin_img, (50, 50))
shield_img = pygame.image.load(SHIELD_FILE)
shield_img = pygame.transform.scale(shield_img, (50, 50))
double_coin_img = pygame.image.load(DOUBLE_COINS_FILE)
double_coin_img = pygame.transform.scale(double_coin_img, (50, 50))
POWERUP_TYPES = ["SHIELD", "DOUBLE"]
# Drawing Texts
def draw_text(text, size, color, x, y, center=True):
    font = pygame.font.SysFont("arial", size, bold=True)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(x, y)) if center else surf.get_rect(topleft=(x, y))
    screen.blit(surf, rect)
# Menu
def level_menu():
    while True:
        screen.blit(menu_bg, (0, 0))
        draw_text("FLAPPY BIRD ADVENTURE", 48, (255, 255, 255), WIDTH//2, 150)
        draw_text("Select Level", 42, (255, 255, 0), WIDTH//2, 250)
        draw_text("1. EASY", 36, (0,255,0), WIDTH//2, 360)
        draw_text("2. MEDIUM", 36, (0,0,255), WIDTH//2, 430)
        draw_text("3. HARD", 36, (255,0,0), WIDTH//2, 500)
        draw_text("Press ESC to Quit", 24, (200,200,200), 20, HEIGHT-40, center=False)
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: return "EASY"
                if e.key == pygame.K_2: return "MEDIUM"
                if e.key == pygame.K_3: return "HARD"
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
def theme_menu():
    theme_list = list(THEMES.keys())
    while True:
        screen.blit(theme_file, (0, 0))
        draw_text("Select Theme", 48, (255,255,255), WIDTH//2, 150)
        for i, t in enumerate(theme_list):
            draw_text(f"{i+1}. {t}", 38, (0,0,0), WIDTH//2, 260 + i*80)
        draw_text("Press 1/2/3 to choose theme", 22, (255,200,150), WIDTH//2, HEIGHT-60)
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                idx = e.key - pygame.K_1
                if 0 <= idx < len(theme_list):
                    return theme_list[idx]
                if e.key == pygame.K_ESCAPE:
                    return "CLASSIC"
# PIPE / COIN / POWERUP
def create_pipe(gap):
    y_center = random.randint(gap//2 + 50, HEIGHT - gap//2 - 50)
    top_height = y_center - gap//2
    bottom_height = HEIGHT - (y_center + gap//2)
    top_rect = pygame.Rect(WIDTH+50, 0, PIPE_WIDTH, top_height)
    bottom_rect = pygame.Rect(WIDTH+50, y_center + gap//2, PIPE_WIDTH, bottom_height)
    return top_rect, bottom_rect
def create_coin(pipe_x):
    y = random.randint(100, HEIGHT-100)
    return pygame.Rect(pipe_x + PIPE_WIDTH//2, y, 40, 40)
def create_powerup(pipe_x):
    if random.randint(1,5) == 1:
        y = random.randint(100, HEIGHT-100)
        ptype = random.choice(POWERUP_TYPES)
        return pygame.Rect(pipe_x + PIPE_WIDTH//2, y, 40, 40), ptype
    return None
# Main Game Loop
def game_loop(level, theme):
    global highscore
    gap = LEVELS[level]["gap"]
    speed = LEVELS[level]["speed"]
    bg = pygame.image.load(THEMES[theme]["bg"])
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
    pipe_img = pygame.image.load(THEMES[theme]["pipe"])
    pipe_img = pygame.transform.scale(pipe_img, (PIPE_WIDTH, 1))
    pipe_top = pygame.transform.flip(pipe_img, False, True)
    bird = bird_img.get_rect(center=(150, HEIGHT//2))
    bird_vel = 0
    pipes, coins, powerups = [], [], []
    shield = False
    double_coins = False
    power_timer = 0
    score = 0
    coin_score = 0
    passed = False
    SPAWN = pygame.USEREVENT
    pygame.time.set_timer(SPAWN, 1500)
    while True:
        clock.tick(60)
        screen.blit(bg, (0, 0))
        # events
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    flap_s.play()
                    bird_vel = JUMP_STRENGTH
                if e.key == pygame.K_ESCAPE:
                    return score, coin_score
            if e.type == SPAWN:
                p1, p2 = create_pipe(gap)
                pipes.extend([p1, p2])
                coins.append(create_coin(p1.x))
                power = create_powerup(p1.x)
                if power: powerups.append(power)
        # bird physics
        bird_vel += GRAVITY
        bird.centery += int(bird_vel)
        screen.blit(bird_img, bird)
        # move objects
        pipes = [p.move(-speed,0) for p in pipes if p.right > 0]
        coins = [c.move(-speed,0) for c in coins if c.right > 0]
        powerups = [(r.move(-speed,0),t) for r,t in powerups if r.right > 0]
        # draw pipes
        for i,p in enumerate(pipes):
            img = pipe_top if i%2==0 else pipe_img
            img = pygame.transform.scale(img,(PIPE_WIDTH, p.height))
            screen.blit(img, p)
        # draw coins
        for c in coins: screen.blit(coin_img, c)
        # draw powerups
        for r,t in powerups:
            img = shield_img if t=="SHIELD" else double_coin_img
            screen.blit(img, r)
        # coin collect
        for c in coins[:]:
            if bird.colliderect(c):
                coins.remove(c)
                coin_score += 2 if double_coins else 1
        # powerup collect
        for r,t in powerups[:]:
            if bird.colliderect(r):
                if t == "SHIELD":
                    shield = True
                else:
                    double_coins = True
                    power_timer = 0
                powerups.remove((r,t))
        # double coin timer
        if double_coins:
            power_timer += 1
            if power_timer > 600:
                double_coins = False
        # scoring
        for i in range(0,len(pipes),2):
            px = pipes[i].centerx
            if 140 < px < 160 and not passed:
                score += 1
                score_s.play()
                passed = True
            if px < 0:
                passed = False
        # collision
        for p in pipes:
            if bird.colliderect(p):
                if shield:
                    shield = False
                    pipes.remove(p)
                    continue
                hit_s.play()
                return score, coin_score
        if bird.top <= 0 or bird.bottom >= HEIGHT:
            hit_s.play()
            return score, coin_score
        # HUD
        draw_text(f"Score: {score}", 32, (255,255,255), WIDTH//2, 50)
        draw_text(f"Coins: {coin_score}", 32, (255,215,0), WIDTH-150, 50)
        if shield: draw_text("Shield Active", 24, (0,255,255), 20, 100, center=False)
        if double_coins: draw_text("Double Coins!", 24, (255,255,0), 20, 140, center=False)
        pygame.display.update()
# Game Over
def game_over_screen(score, coin_score):
    global highscore, unlocked_themes
    if score > highscore:
        highscore = score
        open(hs_file, "w").write(str(highscore))
    while True:
        screen.blit(menu_bg, (0,0))
        draw_text("GAME OVER!", 56, (255,0,0), WIDTH//2, 200)
        draw_text(f"Score: {score}", 44, (255,255,255), WIDTH//2, 280)
        draw_text(f"Coins: {coin_score}", 36, (255,215,0), WIDTH//2, 330)
        draw_text(f"High Score: {highscore}", 32, (200,255,200), WIDTH//2, 380)
        draw_text("R = Restart", 32, (0,255,0), WIDTH//2, 450)
        draw_text("Q = Quit", 32, (255,255,0), WIDTH//2, 500)
        draw_text("T = Themes", 24, (200,150,100), WIDTH//2, HEIGHT-60)
        # Unlock themes
        if score >= 10: unlocked_themes.add("FOREST")
        if score >= 20: unlocked_themes.add("SPACE")
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return "RESTART"
                if e.key == pygame.K_q: pygame.quit(); sys.exit()
                if e.key == pygame.K_t:
                    th = theme_menu()
                    return ("THEME_CHANGE", th)
# Game Settings
def main():
    while True:
        level = level_menu()
        theme = theme_menu()

        score, coins = game_loop(level, theme)
        result = game_over_screen(score, coins)
        if result == "RESTART":
            continue
        if isinstance(result, tuple):
            theme = result[1]
            score, coins = game_loop(level, theme)
            if game_over_screen(score, coins) == "RESTART":
                continue
if __name__ == "__main__":
    main()
