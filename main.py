import os
import random
import sys

import pygame


def start_screen():
    class Background:
        def __init__(self, filename, screen_width, screen_height):
            pygame.init()
            self.screen_width, self.screen_height = screen_width, screen_height
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            pygame.display.set_caption("Flappy Bird")
            self.image = pygame.transform.scale(pygame.image.load(os.path.join('data', filename)),
                                                (self.screen_width, self.screen_height))
            self.font = pygame.font.Font(None, 24)
            self.rules = [
                "Цель игры - пролететь как можно дальше.",
                "Если птица столкнется с трубой или упадет на землю, игра закончится.",
                "Игрок может начать игру заново, нажав пробел."
            ]
            self.show_rules = False

        def draw(self, screen):
            screen.blit(self.image, (0, 0))

    background = Background("фон.jpg", 800, 600)
    screen = background.screen
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                rules_button_rect = background.font.render("Правила", True, (0, 0, 0)).get_rect(
                    topleft=(10, 10))
                if rules_button_rect.collidepoint(event.pos):
                    background.show_rules = not background.show_rules
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return
        background.draw(screen)
        rules_button_text = background.font.render("Правила", True, (0, 0, 0))
        rules_button_rect = rules_button_text.get_rect(topleft=(10, 10))
        screen.blit(rules_button_text, rules_button_rect)

        if background.show_rules:
            y = rules_button_rect.bottom + 10
            for rule in background.rules:
                text = background.font.render(rule, True, (0, 0, 0))
                screen.blit(text, (10, y))
                y += text.get_height() + 5

            screen.blit(background.font.render("Нажмите пробел, чтобы начать", True, (0, 0, 0)), (
                screen.get_width() // 2 - background.font.size("Нажмите пробел, чтобы начать")[0] // 2,
                screen.get_height() // 2 - background.font.size("Нажмите пробел, чтобы начать")[
                    1] // 2 + 100))

        pygame.display.flip()
        clock.tick(60)


def game_over_screen():
    def game_over(self):
        self.background.draw(self.screen)
        self.all_sprites.draw(self.screen)
        self.trubs.draw(self.screen)
        self.screen.blit(self.background.font.render("Игра окончена", True, (0, 0, 0)), (200, 300))
        self.screen.blit(self.background.font.render("Нажмите пробел, чтобы начать заново", True, (0, 0, 0)),
                         (150, 350))
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False
                    self.start_game()
