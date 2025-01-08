import pygame
import sys
import random

pygame.init()
screen_width = 400
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
white = (255, 255, 255)
black = (0, 0, 0)
bird_x = 50
bird_y = screen_height / 2
bird_speed = 0
bird_size = 50
gravity = 0.5
pipe_width = 80
pipe_height = 600
pipe_gap = 150
pipe_x = screen_width
pipe_y = random.randint(0, screen_height - pipe_gap)
score = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird_speed = -10

    bird_speed += gravity
    bird_y += bird_speed
    pipe_x -= 5
    if pipe_x < -pipe_width:
        pipe_x = screen_width
        pipe_y = random.randint(0, screen_height - pipe_gap)
    if (bird_x + bird_size > pipe_x and bird_x < pipe_x + pipe_width) and (
            bird_y < pipe_y or bird_y + bird_size > pipe_y + pipe_gap):
        print("Игра окончена!")
        pygame.quit()
        sys.exit()
    if pipe_x + pipe_width / 2 < bird_x + bird_size / 2 and pipe_x + pipe_width / 2 > bird_x - bird_size / 2:
        score += 1
    screen.fill(black)
    pygame.draw.rect(screen, white, (bird_x, bird_y, bird_size, bird_size))
    pygame.draw.rect(screen, white, (pipe_x, 0, pipe_width, pipe_y))
    pygame.draw.rect(screen, white, (pipe_x, pipe_y + pipe_gap, pipe_width, screen_height - pipe_y - pipe_gap))
    font = pygame.font.Font(None, 36)
    text = font.render(str(score), True, white)
    screen.blit(text, (screen_width / 2, 20))
    pygame.display.flip()
    pygame.time.Clock().tick(60)
