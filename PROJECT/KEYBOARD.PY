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
WIDTH, HEIGHT = 900, 500
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("EEG Dataset Driven BCI Keyboard")

font = pygame.font.SysFont("consolas", 32)
big_font = pygame.font.SysFont("consolas", 42)
clock = pygame.time.Clock()
keys = [
    ["A","B","C","D","E","F"],
    ["G","H","I","J","K","L"],
    ["M","N","O","P","Q","R"],
    ["S","T","U","V","W","X"],
    ["Y","Z","_","<","OK"]
]

rows = len(keys)
row, col = 0, 0
direction = 1
typed_text = ""

SLIDE_DELAY = 0.8
last_move = time.time()

intent_locked = False
def draw():
    win.fill((10, 10, 20))
    text = big_font.render(typed_text, True, (0, 255, 200))
    win.blit(text, (20, 20))

    status = "CONCENTRATED" if concentration else "IDLE"
    status_color = (0,255,0) if concentration else (120,120,120)
    status_text = font.render(f"Intent: {status}", True, status_color)
    win.blit(status_text, (20, 70))

    start_x, start_y = 80, 120
    key_w, key_h = 100, 60

    for r in range(rows):
        for c in range(len(keys[r])):
            x = start_x + c * (key_w + 10)
            y = start_y + r * (key_h + 10)
            rect = pygame.Rect(x, y, key_w, key_h)

            if r == row and c == col:
                pygame.draw.rect(win, (0, 200, 255), rect)
            else:
                pygame.draw.rect(win, (70, 70, 70), rect)

            label = font.render(keys[r][c], True, (0,0,0))
            win.blit(label, (
                x + key_w//2 - label.get_width()//2,
                y + key_h//2 - label.get_height()//2
            ))

    pygame.display.update()
running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if time.time() - last_eeg_time > EEG_INTERVAL:
        last_eeg_time = time.time()
        row_data = df.iloc[eeg_index]
        concentration = detect_concentration(row_data)
        eeg_index = (eeg_index + 1) % len(df)

    if time.time() - last_move > SLIDE_DELAY:
        last_move = time.time()
        col += direction

        if col >= len(keys[row]) or col < 0:
            col -= direction
            row += direction

            if row >= rows or row < 0:
                direction *= -1
                row += direction

            col = 0 if direction == 1 else len(keys[row]) - 1
    if concentration and not intent_locked:
        intent_locked = True
        key = keys[row][col]

        print("Selected:", key)

        if key == "_":
            typed_text += " "
        elif key == "<":
            typed_text = typed_text[:-1]
        elif key == "OK":
            print("FINAL TEXT:", typed_text)
        else:
            typed_text += key

     if not concentration:
        intent_locked = False

    draw()

pygame.quit()
