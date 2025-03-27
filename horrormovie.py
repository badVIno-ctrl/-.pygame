import pygame
import random
import math
import sys
from pygame import mixer

pygame.init()
mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Темный Мир")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
DARK_RED = (150, 0, 0)

try:
    heartbeat_sound = mixer.Sound("heartbeat.wav")
    whisper_sound = mixer.Sound("whisper.wav")
    scream_sound = mixer.Sound("scream.wav")
    ambient_sound = mixer.Sound("ambient.wav")
    font_large = pygame.font.SysFont("arial", 50)
    font_small = pygame.font.SysFont("arial", 30)
except:
    print("Не все файлы звуков найдены. Игра будет без звука.")
    font_large = pygame.font.SysFont(None, 50)
    font_small = pygame.font.SysFont(None, 30)

player_pos = [WIDTH // 2, HEIGHT // 2]
player_speed = 3
player_radius = 15
sanity = 100
flashlight_on = True
flashlight_battery = 100
game_time = 0
collected_notes = 0
total_notes = 5

notes = []
for _ in range(total_notes):
    notes.append([random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)])

scare_events = [
    "figure_appear",
    "whisper",
    "blood_drip",
    "face_flash",
    "scream"
]
next_scare = random.randint(300, 600)


def trigger_figure_appear():
    global sanity
    sanity -= 15
    pygame.draw.rect(screen, BLACK, (WIDTH // 2 - 50, HEIGHT // 2 - 100, 100, 200))
    pygame.display.flip()
    pygame.time.delay(200)
    if 'scream_sound' in globals():
        scream_sound.play()


def trigger_whisper():
    global sanity
    sanity -= 10
    if 'whisper_sound' in globals():
        whisper_sound.play()


def trigger_blood_drip():
    global sanity
    sanity -= 5
    for _ in range(20):
        x = random.randint(0, WIDTH)
        y = random.randint(0, 30)
        pygame.draw.line(screen, RED, (x, y), (x, y + random.randint(5, 15)), 2)
    pygame.display.flip()
    pygame.time.delay(500)


def trigger_face_flash():
    global sanity
    sanity -= 20
    screen.fill(WHITE)
    pygame.draw.ellipse(screen, BLACK, (WIDTH // 2 - 100, HEIGHT // 2 - 150, 200, 300))
    pygame.display.flip()
    pygame.time.delay(100)
    if 'scream_sound' in globals():
        scream_sound.play()


def trigger_scream():
    global sanity
    sanity -= 25
    if 'scream_sound' in globals():
        scream_sound.play()


clock = pygame.time.Clock()
running = True
game_over = False

if 'ambient_sound' in globals():
    ambient_sound.play(-1)

while running:
    dt = clock.tick(60) / 1000.0
    game_time += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                flashlight_on = not flashlight_on
            if event.key == pygame.K_r and game_over:
                sanity = 100
                flashlight_battery = 100
                game_time = 0
                collected_notes = 0
                game_over = False
                player_pos = [WIDTH // 2, HEIGHT // 2]
                if 'ambient_sound' in globals():
                    ambient_sound.play(-1)

    if not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: player_pos[1] -= player_speed
        if keys[pygame.K_s]: player_pos[1] += player_speed
        if keys[pygame.K_a]: player_pos[0] -= player_speed
        if keys[pygame.K_d]: player_pos[0] += player_speed

        player_pos[0] = max(player_radius, min(WIDTH - player_radius, player_pos[0]))
        player_pos[1] = max(player_radius, min(HEIGHT - player_radius, player_pos[1]))

        for note in notes[:]:
            if math.dist(player_pos, note) < player_radius + 10:
                notes.remove(note)
                collected_notes += 1
                sanity = min(100, sanity + 10)

        if flashlight_on:
            flashlight_battery -= 0.1
            if flashlight_battery <= 0:
                flashlight_on = False
                flashlight_battery = 0

        if game_time * 60 >= next_scare and sanity > 0:
            event = random.choice(scare_events)
            if event == "figure_appear":
                trigger_figure_appear()
            elif event == "whisper":
                trigger_whisper()
            elif event == "blood_drip":
                trigger_blood_drip()
            elif event == "face_flash":
                trigger_face_flash()
            elif event == "scream":
                trigger_scream()
            next_scare = game_time * 60 + random.randint(300, 600)

        if random.random() < 0.01 and sanity > 0:
            sanity -= 0.5

        if sanity < 30 and 'heartbeat_sound' in globals():
            if not mixer.get_busy():
                heartbeat_sound.play()

        if sanity <= 0:
            game_over = True
            if 'ambient_sound' in globals():
                ambient_sound.stop()
            if 'scream_sound' in globals():
                scream_sound.play()
        elif collected_notes >= total_notes:
            game_over = True
            if 'ambient_sound' in globals():
                ambient_sound.stop()

    screen.fill(BLACK)

    if not game_over:
        for note in notes:
            pygame.draw.circle(screen, WHITE, note, 5)

        pygame.draw.circle(screen, WHITE, player_pos, player_radius)

        if flashlight_on:
            mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 200))
            pygame.draw.circle(mask, (0, 0, 0, 0), player_pos, 150)
            screen.blit(mask, (0, 0))

        pygame.draw.rect(screen, DARK_RED, (20, 20, 200, 20))
        pygame.draw.rect(screen, RED, (20, 20, 200 * (sanity / 100), 20))
        sanity_text = font_small.render(f"Рассудок: {int(sanity)}%", True, WHITE)
        screen.blit(sanity_text, (20, 45))

        pygame.draw.rect(screen, DARK_RED, (20, 70, 200, 20))
        pygame.draw.rect(screen, RED, (20, 70, 200 * (flashlight_battery / 100), 20))
        battery_text = font_small.render(f"Батарея: {int(flashlight_battery)}%", True, WHITE)
        screen.blit(battery_text, (20, 95))

        notes_text = font_small.render(f"Записки: {collected_notes}/{total_notes}", True, WHITE)
        screen.blit(notes_text, (20, 125))

        hint_text = font_small.render("F - фонарик, WASD - движение", True, WHITE)
        screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT - 40))
    else:
        if sanity <= 0:
            game_over_text = font_large.render("ВЫ ПОТЕРЯЛИ РАССУДОК", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
        else:
            game_over_text = font_large.render("ВЫ ВЫБРАЛИСЬ", True, WHITE)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))

        restart_text = font_small.render("Нажмите R для рестарта", True, WHITE)
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
