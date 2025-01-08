import os
import random
import sys

import pygame


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


class Bird(pygame.sprite.Sprite):
    def __init__(self, radius, x, y, game):
        super().__init__()
        self.radius = radius
        self.image = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color("red"), (radius, radius), radius)
        self.rect = pygame.Rect(x, y, 2 * radius, 2 * radius)
        self.vel = 0
        self.gravity = 0
        self.game = game

    def update(self, *ev):
        for i in trubs.sprites():
            if pygame.sprite.collide_mask(self, i):
                self.game.running = False

        self.rect.y += self.vel
        self.vel += self.gravity

    def click_event(self):
        self.gravity = 1
        self.vel = -10


class Trub(pygame.sprite.Sprite):
    def __init__(self, y, ez):
        super().__init__()
        self.y = y
        self.ez = ez
        self.image = pygame.Surface([50, 600])
        self.rect = self.image.get_rect()
        self.image.fill('green')
        self.image.fill(pygame.Color('white'), pygame.Rect(0, self.y - self.ez // 2, 50, self.ez))
        self.image.set_colorkey(pygame.Color('white'))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = 800
        self.rect.y = 0
        self.v = 5

    def update(self, *args, **kwargs):
        self.rect.x -= self.v
        if self.rect.x + 40 == 0:
            self.kill()


class Game:
    def __init__(self):
        self.background = Background("фон.jpg", 800, 600)
        self.screen = self.background.screen
        self.clock = pygame.time.Clock()
        self.all_sprites = pygame.sprite.Group()
        self.trubs = pygame.sprite.Group()
        self.bird = Bird(20, 100, 300, self)
        self.all_sprites.add(self.bird)
        self.MYEVENTTYPE = pygame.USEREVENT + 1
        pygame.time.set_timer(self.MYEVENTTYPE, 1300)
        self.eazy = 300
        self.time = 0
        self.running = True
        self.ans = False

    def run(self):
        self.clock = pygame.time.Clock()
        self.show_start_screen()
        self.play_game()

    def show_start_screen(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    rules_button_rect = self.background.font.render("Правила", True, (0, 0, 0)).get_rect(
                        topleft=(10, 10))
                    if rules_button_rect.collidepoint(event.pos):
                        self.background.show_rules = not self.background.show_rules
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    return
            self.background.draw(self.screen)
            rules_button_text = self.background.font.render("Правила", True, (0, 0, 0))
            rules_button_rect = rules_button_text.get_rect(topleft=(10, 10))
            self.screen.blit(rules_button_text, rules_button_rect)

            if self.background.show_rules:
                y = rules_button_rect.bottom + 10
                for rule in self.background.rules:
                    text = self.background.font.render(rule, True, (0, 0, 0))
                    self.screen.blit(text, (10, y))
                    y += text.get_height() + 5

            self.screen.blit(self.background.font.render("Нажмите пробел, чтобы начать", True, (0, 0, 0)), (
                self.screen.get_width() // 2 - self.background.font.size("Нажмите пробел, чтобы начать")[0] // 2,
                self.screen.get_height() // 2 - self.background.font.size("Нажмите пробел, чтобы начать")[
                    1] // 2 + 100))

            pygame.display.flip()
            self.clock.tick(60)

    def play_game(self):
        clock = pygame.time.Clock()
        self.MYEVENTTYPE = pygame.USEREVENT + 1
        pygame.time.set_timer(self.MYEVENTTYPE, 1300)
        self.eazy = 300
        self.time = 0
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == self.MYEVENTTYPE:
                    trub = Trub(random.choice(range(self.eazy // 2, 600 - self.eazy // 2 + 1)), self.eazy)
                    self.trubs.add(trub)
                    self.time += 1
                    if self.time == 30 and self.eazy > 100:
                        self.eazy -= 30
                        self.time = 0
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.bird.click_event()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.bird.click_event()
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
            self.screen.fill(pygame.Color("black"))
            self.all_sprites.update()
            self.trubs.update()
            self.trubs.draw(self.screen)
            self.all_sprites.draw(self.screen)
            self.update()
            pygame.display.flip()
            clock.tick(50)
        pygame.quit()

    def start_game(self):
        self.background.show_rules = False
        self.bird.rect.y = 300
        self.bird.vel = 0
        self.bird.gravity = 0
        self.trubs.empty()
        self.time = 0
        self.eazy = 300
        self.running = True
        self.ans = False

    def check_collision(self):
        for i in self.trubs.sprites():
            if pygame.sprite.collide_mask(self.bird, i):
                self.running = False
                self.ans = True

    def update(self):
        self.check_collision()
        if self.bird.rect.y > 600:
            self.running = False
            self.ans = True
        if not self.running:
            self.game_over()

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


if __name__ == '__main__':
    pygame.display.set_caption('test_bird_window')
    trubs = pygame.sprite.Group()
    game = Game()
    game.run()
