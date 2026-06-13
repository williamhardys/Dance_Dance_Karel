import pygame
import asyncio 
import random
import time
import math

# INIT
pygame.init()

# SCREEN SETUP
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dance Dance Karel - Start Screen")

# COLOR
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
RICH_DEEP_BLUE = (11, 34, 117)

# GAME CONSTANTS
ARROW_SIZE = 64
ARROW_Y_START = SCREEN_HEIGHT
TARGET_Y = 50
SPEED = 5
LANE_X = [150, 250, 350, 450]
DIRECTIONS = ['left', 'down', 'up', 'right']

# LOADING RESOURCES
try:
    images = {
        'left': pygame.transform.scale(pygame.image.load('assets/images/arrow_left.png'), (ARROW_SIZE, ARROW_SIZE)),
        'down': pygame.transform.scale(pygame.image.load('assets/images/arrow_down.png'), (ARROW_SIZE, ARROW_SIZE)),
        'up': pygame.transform.scale(pygame.image.load('assets/images/arrow_up.png'), (ARROW_SIZE, ARROW_SIZE)),
        'right': pygame.transform.scale(pygame.image.load('assets/images/arrow_right.png'), (ARROW_SIZE, ARROW_SIZE))
    }
    target_images = {}
    for dir_name, img in images.items():
        target_img = img.copy()
        target_img.set_alpha(100)
        target_images[dir_name] = target_img


    

except Exception as e:
    print("Error loading images: {}".format(e))
    images = None

class Arrow:
    def __init__(self, direction, lane_idx):
        self.direction = direction
        self.x = LANE_X[lane_idx]
        self.y = ARROW_Y_START
        self.hit = False

async def main():
    clock = pygame.time.Clock()
    arrows = []
    score = 0
    combo = 0
    max_combo = 0
    feedback = ""
    feedback_time = 0
    
    # 音樂設定
    music_file = 'assets/sounds/bgm.mp3'
    game_duration = 60
    try:
        pygame.mixer.music.load(music_file)
    except Exception as e:
        print(f"Error loading music: {e}")

    start_time = 0
    spawn_timer = 0
    spawn_interval = 0.46
    

    
    # GAME STATES
    game_state = "START_SCREEN"

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        screen.fill(RICH_DEEP_BLUE)

        # EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if game_state == "START_SCREEN":
                    if event.key == pygame.K_SPACE:
                        game_state = "PLAYING"
                        start_time = time.time()
                        pygame.mixer.music.play()
                elif game_state == "PLAYING":
                    key_dir = None
                    if event.key == pygame.K_LEFT: key_dir = 'left'
                    elif event.key == pygame.K_DOWN: key_dir = 'down'
                    elif event.key == pygame.K_UP: key_dir = 'up'
                    elif event.key == pygame.K_RIGHT: key_dir = 'right'
                    
                    if key_dir:
                        hit_found = False
                        for arrow in arrows:
                            if not arrow.hit and arrow.direction == key_dir:
                                dist = abs(arrow.y - TARGET_Y)
                                if dist < 30:
                                    feedback = "PERFECT!"
                                    score += 100
                                    combo += 1
                                    max_combo = max(max_combo, combo)
                                    arrow.hit = True
                                    hit_found = True
                                    feedback_time = time.time()
                                    break
                                elif dist < 60:
                                    feedback = "GREAT"
                                    score += 50
                                    combo += 1
                                    max_combo = max(max_combo, combo)
                                    arrow.hit = True
                                    hit_found = True
                                    feedback_time = time.time()
                                    break
                        if not hit_found:
                            combo = 0
                            feedback = "MISS"
                            feedback_time = time.time()
                elif game_state == "FINISHED":
                    if event.key == pygame.K_SPACE:
                        game_state = "START_SCREEN"
                        score = 0
                        combo = 0
                        max_combo = 0
                        arrows = []

        if game_state == "START_SCREEN":
            # 
            font_title = pygame.font.SysFont(None, 60)
            font_hint = pygame.font.SysFont(None, 40)
            font_instr = pygame.font.SysFont(None, 30)

            title_text = font_title.render("Dance Dance Karel", True, CYAN)
            hint_text = font_hint.render("Press SPACE to Start", True, WHITE)
            instr_text = font_instr.render("Use Arrow Keys to play. Follow the rhythm!", True, GRAY)
            # 
            
            try:
                # 
                cartoon_img = pygame.image.load('assets/images/karel_image.png')
                # 
                cartoon_img = pygame.transform.scale(cartoon_img, (300, 160))
            except pygame.error:
                # 
                cartoon_img = pygame.Surface((300, 160))
                cartoon_img.fill((50, 205, 50))

            
            # * 15 controls the HEIGHT of the bounce (15 pixels up and down)
            bounce_offset = math.sin(time.time() * 5) * 15
            img_y = 160 + bounce_offset
            img_x = SCREEN_WIDTH // 2 - cartoon_img.get_width() // 2
            
            # 
            screen.blit(cartoon_img, (img_x, img_y))

            
            # 
            if int(time.time() * 2) % 2 == 0:
                screen.blit(hint_text, (SCREEN_WIDTH // 2 - 140, 300))

            screen.blit(title_text, (SCREEN_WIDTH // 2 - 180, 150))
            screen.blit(instr_text, (SCREEN_WIDTH // 2 - 200, 400))

        elif game_state == "PLAYING":
            current_time = time.time()
            elapsed_time = current_time - start_time
            remaining_time = max(0, game_duration - elapsed_time)

            if remaining_time <= 0:
                game_state = "FINISHED"
                pygame.mixer.music.stop()

            # ARROW SPAWNING
            spawn_timer += dt
            if spawn_timer >= spawn_interval:
                if random.random() > 0.3:
                    lane = random.randint(0, 3)
                    arrows.append(Arrow(DIRECTIONS[lane], lane))
                spawn_timer = 0

            # 
            for i, dir_name in enumerate(DIRECTIONS):
                if images:
                    screen.blit(target_images[dir_name], (LANE_X[i], TARGET_Y))
                else:
                    pygame.draw.rect(screen, GRAY, (LANE_X[i], TARGET_Y, ARROW_SIZE, ARROW_SIZE), 2)

            # UPDATE ARROWS
            for arrow in arrows[:]:
                if not arrow.hit:
                    arrow.y -= SPEED
                    if images:
                        screen.blit(images[arrow.direction], (arrow.x, arrow.y))
                    else:
                        pygame.draw.rect(screen, WHITE, (arrow.x, arrow.y, ARROW_SIZE, ARROW_SIZE))
                    
                    if arrow.y < -ARROW_SIZE:
                        arrows.remove(arrow)
                        combo = 0
                        feedback = "MISS"
                        feedback_time = time.time()
                else:
                    arrows.remove(arrow)

            #  UI
            font = pygame.font.SysFont(None, 36)
            score_text = font.render(f"Score: {score}", True, WHITE)
            combo_text = font.render(f"Combo: {combo}", True, YELLOW)
            time_text = font.render(f"Time: {int(remaining_time)}s", True, GREEN if remaining_time > 10 else RED)
            
            screen.blit(score_text, (10, 10))
            screen.blit(combo_text, (10, 50))
            screen.blit(time_text, (SCREEN_WIDTH - 150, 10))

            if time.time() - feedback_time < 0.5:
                fb_font = pygame.font.SysFont(None, 48)
                fb_text = fb_font.render(feedback, True, WHITE)
                screen.blit(fb_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2))

        elif game_state == "FINISHED":
            # 
            font_title = pygame.font.SysFont(None, 64)
            font_info = pygame.font.SysFont(None, 48)
            font_hint = pygame.font.SysFont(None, 32)

            res_text = font_title.render("GAME OVER", True, RED)
            score_res = font_info.render(f"Final Score: {score}", True, WHITE)
            combo_res = font_info.render(f"Max Combo: {max_combo}", True, WHITE)
            hint_text = font_hint.render("Press SPACE to Play Again", True, GRAY)

            screen.blit(res_text, (SCREEN_WIDTH // 2 - 130, 100))
            screen.blit(score_res, (SCREEN_WIDTH // 2 - 120, 200))
            screen.blit(combo_res, (SCREEN_WIDTH // 2 - 120, 260))
            screen.blit(hint_text, (SCREEN_WIDTH // 2 - 160, 380))

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
