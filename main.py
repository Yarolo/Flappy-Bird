import os
import random
import sys

import pygame


class Counter:
    def __init__(self):
        self.score = 0

    def update_score(self):
        self.score += 1


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y, all_sprites, obstacles, borders):
        super().__init__(all_sprites)
        self.obstacles = obstacles
        self.borders = borders
        self.images = {
            'up': pygame.image.load(os.path.join('data', 'bluebird-upflap.png')).convert_alpha(),
            'mid': pygame.image.load(os.path.join('data', 'bluebird-midflap.png')).convert_alpha(),
            'down': pygame.image.load(os.path.join('data', 'bluebird-downflap.png')).convert_alpha()
        }
        self.image = self.images['mid']
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = 0
        self.gravity = 0
        self.state = 'mid'
        self.angle = 0

    def update(self, *ev):
        global running
        for i in self.obstacles.sprites():
            if pygame.sprite.collide_mask(self, i):
                running = False
        if pygame.sprite.spritecollideany(self, self.borders):
            running = False
        self.rect.y += self.vel
        self.vel += self.gravity
        if self.vel < 0:
            self.state = 'up'
        elif self.vel > 0:
            self.state = 'down'
        else:
            self.state = 'mid'
        self.image = self.images[self.state]
        self.angle = -self.vel * 4
        self.angle = max(-60, min(60, self.angle))
        self.image = pygame.transform.rotate(self.images[self.state], self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def click_event(self):
        self.gravity = 1.123
        self.vel = -10


class Pipe(pygame.sprite.Sprite):
    def __init__(self, y, ez, all_sprites, obstacles, height, width):
        super().__init__(all_sprites)
        self.add(obstacles)
        self.y = random.randint(50, height - 200)
        self.ez = ez
        self.pipe_image_mid = pygame.image.load(os.path.join('data', 'pipe_mid.png')).convert_alpha()
        self.pipe_image_up = pygame.image.load(os.path.join('data', 'pipe_up.png'))
        self.image = pygame.Surface([52, height])
        self.image.fill('white')
        self.upper_limit = self.y - self.ez // 2
        self.lower_limit = self.y - self.ez // 2 + self.ez
        for i in range(self.upper_limit - self.pipe_image_up.get_height()):
            self.image.blit(self.pipe_image_mid, (0, i))
        self.image.blit(pygame.transform.flip(self.pipe_image_up, False, True),
                        (0, self.upper_limit - self.pipe_image_up.get_height()))
        self.image.blit(self.pipe_image_up, (0, self.lower_limit))
        for i in range(self.lower_limit + self.pipe_image_up.get_height(), height):
            self.image.blit(self.pipe_image_mid, (0, i))
        self.image.set_colorkey(('white'))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = width
        self.rect.y = 0
        self.v = 5
        self.passed = False

    def update(self, *args, **kwargs):
        global cnt
        self.rect.x -= self.v
        if self.rect.x + 50 == 0 and not self.passed:
            self.passed = True
            cnt.update_score()
        if self.rect.x + 50 < 0:
            self.kill()


class Ball(pygame.sprite.Sprite):
    def __init__(self, all_sprites, obstacles, width, height):
        super().__init__(all_sprites)
        self.height = height
        self.add(obstacles)
        self.image = pygame.transform.scale(pygame.image.load(os.path.join('data', 'spiked_ball.png')), (60, 60))
        self.rect = self.image.get_rect()
        self.rect.x = width
        self.vel_x = -5
        self.vel_y = random.choice([-5, 5])
        self.mask = pygame.mask.from_surface(self.image)
        if self.rect.y + self.image.get_height() > self.height - 20 or self.rect.y < 0:
            self.vel_y = -self.vel_y + random.uniform(-1, 1)
        self.passed = False

    def update(self, *args):
        global cnt
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        if self.rect.y + self.image.get_height() > self.height - 20 or self.rect.y < 0:
            self.vel_y *= -1
        if self.rect.x + self.image.get_width() < 0:
            self.kill()
        if self.rect.x + 50 == 0 and not self.passed:
            self.passed = True
            cnt.update_score()


class Ground(pygame.sprite.Sprite):
    def __init__(self, all_sprites, borders, height, width):
        super().__init__(all_sprites)
        self.add(borders)
        self.image = pygame.transform.scale(pygame.image.load(os.path.join("data", "base.png")), (width, 20))
        self.rect = self.image.get_rect()
        self.image.set_colorkey(pygame.Color('white'))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = height - 20

    def get_height(self):
        return 20


class Clouds(pygame.sprite.Sprite):
    def __init__(self, all_sprites, borders, width):
        super().__init__(all_sprites)
        self.add(borders)
        self.image = pygame.transform.scale(pygame.image.load(os.path.join("data", "sky.png")),
                                            (width, 20)).convert_alpha()
        self.rect = self.image.get_rect()

        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

    def get_height(self):
        return 20


class PlayButton(pygame.sprite.Sprite):
    def __init__(self, buttons):
        super().__init__(buttons)
        self.unclicked = pygame.image.load(os.path.join('data', 'unclicked_play_button.png')).convert_alpha()
        self.clicked = pygame.image.load(os.path.join('data', 'clicked_play_button.png')).convert_alpha()
        self.unclicked = pygame.transform.scale(self.unclicked, (200, 100))
        self.clicked = pygame.transform.scale(self.clicked, (200, 100))
        self.image = self.unclicked
        self.rect = self.image.get_rect()
        self.rect.x = 300
        self.rect.y = 350

    def update(self, *args, **kwargs):
        global running
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and \
                self.rect.collidepoint(args[0].pos):
            self.image = self.clicked
        if args and args[0].type == pygame.MOUSEBUTTONUP:
            self.image = self.unclicked
            if self.rect.collidepoint(args[0].pos):
                running = False


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


running = True
cnt = Counter()


def game_over(screen, last_frame, score):
    game_over_image = pygame.image.load(os.path.join('data', 'game_over.png'))
    game_over_rect = game_over_image.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    clock = pygame.time.Clock()
    score_images = []
    for i in range(10):
        score_images.append(pygame.image.load(os.path.join("data", f"{i}.png")))
    x = screen.get_width() // 2 - len(str(score)) * 20 // 2
    y = game_over_rect.bottom + 20
    current_score = 0
    for i in range(255):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        s = pygame.Surface((screen.get_width(), screen.get_height()))
        s.get_height()
        s.set_alpha(i)
        s.blit(game_over_image, game_over_rect)
        if i > 100:
            score_str = str(min(i - 100, score))
            x = screen.get_width() // 2 - len(str(score)) * 20 // 2
            for digit in score_str:
                s.blit(score_images[int(digit)], (x, y))
                x += 20
        screen.blit(s, (0, 0))
        pygame.display.flip()
        clock.tick(24)
    for i in range(score + 1):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        s = pygame.Surface((screen.get_width(), screen.get_height()))
        s.blit(game_over_image, game_over_rect)
        score_str = str(i)
        x = screen.get_width() // 2 - len(str(score)) * 20 // 2
        for digit in score_str:
            s.blit(score_images[int(digit)], (x, y))
            x += 20
        screen.blit(s, (0, 0))
        pygame.display.flip()
        if i < score // 8:
            clock.tick(200)
        elif i < score // 7:
            clock.tick(180)
        elif i < score // 6:
            clock.tick(150)
        elif i < score // 5:
            clock.tick(130)
        elif i < score // 4:
            clock.tick(100)
        elif i < score // 3:
            clock.tick(80)
        elif i < score // 2:
            clock.tick(50)
        elif i < score * 3 // 4:
            clock.tick(20)
        else:
            clock.tick(5)

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
                return


def main():
    global running
    global cnt
    pygame.display.set_caption('Flappy Bird')
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    borders = pygame.sprite.Group()

    size = width, height = 800, 600
    screen = pygame.display.set_mode(size)
    br = Bird(100, 300, all_sprites, obstacles, borders)
    clock = pygame.time.Clock()

    cl = Clouds(all_sprites, borders, width)
    gr = Ground(all_sprites, borders, height, width)
    MYEVENTTYPE = pygame.USEREVENT + 1
    flag = True
    pause = False
    eazy = 300
    time = 0
    background_image = pygame.transform.scale(pygame.image.load(os.path.join("data", "background-day.png")),
                                              (width, height))
    score_images = []
    for i in range(10):
        score_images.append(pygame.image.load(os.path.join("data", f"{i}.png")))

    while running:
        for event in pygame.event.get():
            if not (pause):
                if event.type == MYEVENTTYPE:
                    time += 1
                    if time % 10 == 0 and eazy > 100:
                        eazy -= 40
                    if time // 20 >= 1:
                        is_pipe = random.choice((False, True))
                        if is_pipe:
                            Pipe(random.choice(range(eazy // 2, size[1] - eazy // 2 + 1)), eazy, all_sprites, obstacles,
                                 height, width)
                        else:
                            Ball(all_sprites, obstacles, width, height)
                    else:
                        Pipe(random.choice(range(eazy // 2, size[1] - eazy // 2 + 1)), eazy, all_sprites, obstacles,
                             height, width)
            if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                if flag:
                    flag = False
                    pygame.time.set_timer(MYEVENTTYPE, 1300)
                br.click_event()
                pause = False
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if pause:
                        running = False
                    else:
                        pause = True
        if not (pause):
            screen.blit(background_image, (0, 0))
            all_sprites.update()
            all_sprites.draw(screen)
            borders.draw(screen)
            score = cnt.score
            x = width // 2 - len(str(score)) * 20 // 2
            for digit in str(score):
                screen.blit(score_images[int(digit)], (x, height // 2 - 20))
                x += 20
        pygame.display.flip()
        clock.tick(50)

    game_over(screen, screen.copy(), cnt.score)


def start_screen():
    background = Background("background-day.png", 800, 600)
    screen = background.screen
    clock = pygame.time.Clock()
    buttons = pygame.sprite.Group()
    bird_images = {
        'up': pygame.image.load(os.path.join('data', 'bluebird-upflap.png')).convert_alpha(),
        'mid': pygame.image.load(os.path.join('data', 'bluebird-midflap.png')).convert_alpha(),
        'down': pygame.image.load(os.path.join('data', 'bluebird-downflap.png')).convert_alpha()
    }
    bird_state = 'mid'
    bird_image = bird_images[bird_state]
    bird_rect = bird_image.get_rect(center=(100, 300))
    animation_timer = 0
    animation_speed = 10
    PlayButton(buttons)

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
            if event.type == pygame.MOUSEBUTTONDOWN and buttons.sprites()[0].rect.collidepoint(event.pos):
                return

        background.draw(screen)
        screen.blit(bird_image, bird_rect)
        rules_button_text = background.font.render("Правила", True, (0, 0, 0))
        rules_button_rect = rules_button_text.get_rect(topleft=(10, 10))
        screen.blit(rules_button_text, rules_button_rect)

        if background.show_rules:
            y = rules_button_rect.bottom + 10
            for rule in background.rules:
                text = background.font.render(rule, True, (0, 0, 0))
                screen.blit(text, (10, y))
                y += text.get_height() + 5

        animation_timer += 1
        if animation_timer >= animation_speed:
            animation_timer = 0
            if bird_state == 'mid':
                bird_state = 'up'
            elif bird_state == 'up':
                bird_state = 'down'
            else:
                bird_state = 'mid'
            bird_image = bird_images[bird_state]
        buttons.update(event)
        buttons.draw(screen)
        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    start_screen()
    main()
