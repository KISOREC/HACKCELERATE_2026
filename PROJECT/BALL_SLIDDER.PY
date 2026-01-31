import pygame
import pandas as pd
import time
df = pd.read_csv("datasets/person01.csv")
eeg_index = 0
last_eeg_time = time.time()
EEG_INTERVAL = 1.0 

def detect_concentration(row):
    score = (
        (row["beta"] / row["baseline_beta"]) +
        (row["gamma"] * 0.5) -
        (row["alpha"] / row["baseline_alpha"])
    )
    return score > 1.2
concentration = False
pygame.init()
WIDTH, HEIGHT = 800, 500
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("EEG Dataset Ball Slider – BCI Demo")

clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 28)
paddle = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 30, 120, 15)
paddle_speed = 10

ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, 15, 15)
ball_dx = 6
ball_dy = -6

game_over = False
intent_locked = False
def reset_game():
    global ball_dx, ball_dy, game_over, intent_locked
    ball.center = (WIDTH // 2, HEIGHT // 2)
    ball_dx, ball_dy = 6, -6
    game_over = False
    intent_locked = False
running = True
while running:
    clock.tick(60)
    win.fill((20, 20, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if time.time() - last_eeg_time > EEG_INTERVAL:
        last_eeg_time = time.time()
        row = df.iloc[eeg_index]
        concentration = detect_concentration(row)
        eeg_index = (eeg_index + 1) % len(df)

    if not game_over:
        if concentration:
            paddle.x += paddle_speed
        else:
            paddle.x -= paddle_speed * 0.4

        paddle.x = max(0, min(WIDTH - paddle.width, paddle.x))

        ball.x += ball_dx
        ball.y += ball_dy
        if ball.left <= 0 or ball.right >= WIDTH:
            ball_dx *= -1
        if ball.top <= 0:
            ball_dy *= -1
        if ball.colliderect(paddle):
            ball_dy *= -1
        if ball.bottom >= HEIGHT:
            game_over = True

    else:
        text = font.render("GAME OVER – Concentrate to Restart", True, (255, 80, 80))
        win.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))

        # Concentration restart (debounced)
        if concentration and not intent_locked:
            intent_locked = True
            reset_game()

        if not concentration:
            intent_locked = False
    status = "CONCENTRATED" if concentration else "RELAXED"
    color = (0,255,0) if concentration else (120,120,120)
    status_text = font.render(f"State: {status}", True, color)
    win.blit(status_text, (10, 10))

    pygame.draw.rect(win, (0, 200, 255), paddle)
    pygame.draw.ellipse(win, (255, 50, 50), ball)

    pygame.display.update()

pygame.quit()
