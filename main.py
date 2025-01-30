import math
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
        self.gravity = 1.123
        self.state = 'mid'
        self.angle = 0
        self.dead = False
        self.death_type = None
        self.rotation_angle = 0
        self.pipe_suck_speed = [0, 0]
        self.bounce_count = 0
        self.max_bounces = 3

    def update(self, *ev):
        global running
        global game_over_screen
        if not self.dead:
            for i in self.obstacles.sprites():
                if pygame.sprite.collide_mask(self, i):
                    if isinstance(i, Pipe):
                        self.die(death_type="pipe", obstacle=i)
                    elif isinstance(i, Ball):
                        self.die(death_type="ball")
            if pygame.sprite.spritecollideany(self, self.borders):
                border = pygame.sprite.spritecollideany(self, self.borders)
                if border.rect.y == 0:
                    self.die(death_type="top")
                else:
                    self.die(death_type="bottom")
            self.rect.y += self.vel
            self.vel += self.gravity
            if self.vel < 0:
                self.state = 'up'
            elif self.vel > 0:
                self.state = 'down'
            else:
                self.state = 'mid'
            self.image = self.images[self.state]
            self.angle = -self.vel * 1.5
            self.angle = max(-60, min(60, self.angle))
            self.image = pygame.transform.rotate(self.images[self.state], self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)
        else:
            if self.death_type == "top":
                self.angle = min(self.angle + 5, 90)
                self.image = pygame.transform.rotate(self.images['mid'], self.angle)
                self.vel += self.gravity
                self.rect.y += self.vel
                if self.rect.y >= 600:
                    self.image = pygame.transform.rotate(self.images['mid'], 180)
                    running = False
                    game_over_screen = True
            elif self.death_type == "bottom":
                self.vel += self.gravity
                self.rect.y += self.vel
                if self.rect.y >= 600:
                    self.bounce_count += 1
                    self.vel *= -0.7
                    if self.bounce_count >= self.max_bounces:
                        self.image = pygame.transform.rotate(self.images['mid'], 180)
                        running = False
                        game_over_screen = True
            elif self.death_type == "pipe":
                self.rect.x += self.pipe_suck_speed[0]
                self.rect.y += self.pipe_suck_speed[1]
                if self.rect.y < 0 or self.rect.y > 600:
                    running = False
                    game_over_screen = True
            elif self.death_type == "ball":
                self.rotation_angle += 10
                self.image = pygame.transform.rotate(self.images['mid'], self.rotation_angle)
                self.vel += self.gravity
                self.rect.y += self.vel
                if self.rect.y >= 600:
                    running = False
                    game_over_screen = True

    def die(self, death_type, obstacle=None):
        self.dead = True
        self.death_type = death_type
        if death_type == "top":
            self.vel = 0
        elif death_type == "bottom":
            self.vel = -20
        elif death_type == "pipe":
            self.pipe_suck_speed = [0, 0]
            if obstacle.rect.x > self.rect.x:
                self.pipe_suck_speed[0] = -5
            else:
                self.pipe_suck_speed[0] = 5
            self.pipe_suck_speed[1] = -5
        elif death_type == "ball":
            self.vel = 0
            self.rotation_angle = 0

    def click_event(self):
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
        self.width = width
        self.add(obstacles)
        self.original_image = pygame.transform.scale(
            pygame.image.load(os.path.join('data', 'spiked_ball.png')), (60, 60)
        ).convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.x = width
        self.vel_x = -7
        self.vel_y = random.choice([-3, -2, -1, 1, 2, 3])
        self.mask = pygame.mask.from_surface(self.image)
        self.passed = False
        self.angle = 0
        self.rotation_speed = 10
        self.movement_type = random.choice([
            "bounce", "straight", "sinusoidal", "spiral", "zigzag", "chaotic", "static"
        ])
        self.level = random.choice(["top", "middle", "bottom"])
        self.amplitude = random.randint(50, 100)
        self.frequency = random.uniform(0.01, 0.03)
        self.time = 0
        self.spiral_angle = 1
        self.chaotic_counter = 0
        self.zigzag_direction = 1
        if self.level == "top":
            self.rect.y = random.randint(50, height // 3)
        elif self.level == "middle":
            self.rect.y = random.randint(height // 3, 2 * height // 3)
        elif self.level == "bottom":
            self.rect.y = random.randint(2 * height // 3, height - 50)

    def update(self, *args):
        global cnt
        self.rect.x += self.vel_x
        if self.movement_type == "bounce":
            self.rect.y += self.vel_y
            if self.rect.y + self.image.get_height() > self.height - 20 or self.rect.y < 0:
                self.vel_y *= -1
        elif self.movement_type == "straight":
            pass
        elif self.movement_type == "sinusoidal":
            self.time += 1
            self.rect.y = self.rect.y + self.amplitude * math.sin(self.frequency * self.time)
        elif self.movement_type == "spiral":
            self.spiral_angle += 0.1
            self.rect.y = self.rect.y + 2 * math.sin(self.spiral_angle)
            self.rect.x += 2 * math.cos(self.spiral_angle)
        elif self.movement_type == "zigzag":
            self.rect.y += self.vel_y * self.zigzag_direction
            if self.rect.y + self.image.get_height() > self.height - 20 or self.rect.y < 0:
                self.zigzag_direction *= -1
        elif self.movement_type == "chaotic":
            self.chaotic_counter += 1
            if self.chaotic_counter % 10 == 0:
                self.vel_y = random.choice([-3, -2, -1, 1, 2, 3])
            self.rect.y += self.vel_y
            if self.rect.y + self.image.get_height() > self.height - 20 or self.rect.y < 0:
                self.vel_y *= -1
        elif self.movement_type == "static":
            self.rect.x -= 2
            self.rect.y = self.rect.y
        self.angle = (self.angle + self.rotation_speed) % 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
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


class Button(pygame.sprite.Sprite):
    def __init__(self, unclick, click, size, pos, buttons):
        super().__init__(buttons)
        self.unclicked_im = pygame.image.load(os.path.join('data', unclick)).convert_alpha()
        self.clicked_im = pygame.image.load(os.path.join('data', click)).convert_alpha()
        self.unclicked_im = pygame.transform.scale(self.unclicked_im, (size[0], size[1]))
        self.clicked_im = pygame.transform.scale(self.clicked_im, (size[0], size[1]))
        self.image = self.unclicked_im
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.clicked = False

    def isclicked(self):
        if self.clicked:
            self.clicked = False
            return True
        return False

    def update(self, *args, **kwargs):
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and \
                self.rect.collidepoint(args[0].pos):
            self.image = self.clicked_im
        if args and args[0].type == pygame.MOUSEBUTTONUP:
            self.image = self.unclicked_im
            if self.rect.collidepoint(args[0].pos):
                self.clicked = True


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


game_over_screen = False
running = True
cnt = Counter()


def load_record():
    try:
        with open('data/record.txt', 'r') as f:
            return int(f.read())
    except:
        return 0


def save_record(record):
    with open('data/record.txt', 'w') as f:
        f.write(str(record))


def game_over(screen, score):
    record = load_record()
    new_record = score > record
    if new_record:
        save_record(score)
        record = score
    game_over_image = pygame.image.load(os.path.join('data', 'game_over.png'))
    game_over_rect = game_over_image.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    game_over_scr = screen.copy()
    clock = pygame.time.Clock()
    score_images = []
    for i in range(10):
        score_images.append(pygame.image.load(os.path.join("data", f"{i}.png")))
    x = screen.get_width() // 2 - len(str(score)) * 20 // 2
    y = game_over_rect.bottom + 20
    for i in range(0, 256, 5):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        s = pygame.Surface((screen.get_width(), screen.get_height()))
        s.set_alpha(i)
        screen.blit(game_over_scr, (0, 0))
        s.blit(game_over_image, game_over_rect)
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
    if new_record:
        new_record_font = pygame.font.Font(None, 72)
        new_record_text = new_record_font.render("НОВЫЙ РЕКОРД!", True, (255, 215, 0))
        new_record_rect = new_record_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 100))
        record_font = pygame.font.Font(None, 48)
        record_text = record_font.render(f"Рекорд: {record}", True, (255, 255, 255))
        record_rect = record_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 100))
        for alpha in range(0, 256, 5):
            s = pygame.Surface(screen.get_size())
            s.set_alpha(alpha)
            s.blit(new_record_text, new_record_rect)
            s.blit(record_text, record_rect)
            screen.blit(s, (0, 0))
            pygame.display.flip()
            pygame.time.delay(30)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                return


def main():
    global running
    global cnt
    global game_over_screen
    cnt.score = 0
    pygame.display.set_caption('Flappy Bird')
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    borders = pygame.sprite.Group()
    buttons = pygame.sprite.Group()
    rb_btn = Button('unclicked_roll_back_button.png', 'clicked_roll_back_button.png', (80, 80), (680, 20), buttons)
    size = width, height = 800, 600
    screen = pygame.display.set_mode(size)
    br = Bird(100, 300, all_sprites, obstacles, borders)
    clock = pygame.time.Clock()
    Clouds(all_sprites, borders, width)
    Ground(all_sprites, borders, height, width)
    MYEVENTTYPE = pygame.USEREVENT + 1
    pause_screen = pygame.Surface((screen.get_width(), screen.get_height()))
    pause_screen.set_alpha(70)
    pause = False
    eazy = 300
    time = 0
    background_image = pygame.transform.scale(pygame.image.load(os.path.join("data", "background-day.png")),
                                              (width, height))
    pygame.time.set_timer(MYEVENTTYPE, 1300)
    score_images = []
    for i in range(10):
        score_images.append(pygame.image.load(os.path.join("data", f"{i}.png")))
    while running:
        for event in pygame.event.get():
            if not (pause):
                rb_btn.kill()
                pygame.mouse.set_visible(False)
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
                if event.type == pygame.MOUSEBUTTONDOWN or (
                        event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                    br.click_event()
            else:
                pygame.mouse.set_visible(True)
                buttons.update(event)
                buttons.draw(screen)
            if rb_btn.isclicked():
                return
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and not pause:
                rb_btn = Button('unclicked_roll_back_button.png', 'clicked_roll_back_button.png', (80, 80),
                                (680, 20), buttons)
                screen.blit(pause_screen, (0, 0))
                pause = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and pause:
                pause = False

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
    pygame.mouse.set_visible(True)
    if game_over_screen:
        game_over(screen, cnt.score)
    running = True
    game_over_screen = False


def start_screen():
    background = Background("background-day.png", 800, 600)
    screen = background.screen
    clock = pygame.time.Clock()
    buttons = pygame.sprite.Group()
    playbutton = Button('unclicked_play_button.png', 'clicked_play_button.png', (200, 100), (300, 350), buttons)
    bird_images = {
        'up': pygame.image.load(os.path.join('data', 'bluebird-upflap.png')).convert_alpha(),
        'mid': pygame.image.load(os.path.join('data', 'bluebird-midflap.png')).convert_alpha(),
        'down': pygame.image.load(os.path.join('data', 'bluebird-downflap.png')).convert_alpha()
    }
    bird_state = 'mid'
    bird_image = bird_images[bird_state]
    bird_rect = bird_image.get_rect(center=(100, 300))
    animation_timer = 0
    animation_speed = 30
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            buttons.update(event)
            if playbutton.isclicked():
                choose_game_mode()
        background.draw(screen)
        buttons.draw(screen)
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

        pygame.display.flip()
        clock.tick(60)


def choose_game_mode():
    background = Background("background-day.png", 800, 600)
    screen = background.screen
    clock = pygame.time.Clock()
    buttons = pygame.sprite.Group()
    infinite_button = Button("unclicked_endless_mode_button.png", "clicked_endless_mode_button.png", \
                             (150, 80), (100, 210), buttons)
    levels_button = Button("unclicked_levels_button.png", "clicked_levels_button.png", \
                           (150, 80), (100, 310), buttons)
    rb_btn = Button('unclicked_roll_back_button.png', 'clicked_roll_back_button.png', \
                    (80, 80), (680, 20), buttons)
    bird_images = {
        'up': pygame.image.load(os.path.join('data', 'bluebird-upflap.png')).convert_alpha(),
        'mid': pygame.image.load(os.path.join('data', 'bluebird-midflap.png')).convert_alpha(),
        'down': pygame.image.load(os.path.join('data', 'bluebird-downflap.png')).convert_alpha()
    }
    bird_state = 'mid'
    bird_image = bird_images[bird_state]
    bird_rect = bird_image.get_rect(center=(infinite_button.rect.left - 50, infinite_button.rect.centery))
    animation_timer = 0
    animation_speed = 30
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            buttons.update(event)
            if infinite_button.isclicked():
                main()
                return
            elif rb_btn.isclicked():
                return
            elif levels_button.isclicked():
                choose_level()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        infinite_button_rect = infinite_button.rect
        levels_button_rect = levels_button.rect
        area_padding = 50
        restricted_area_infinite = infinite_button_rect.inflate(area_padding * 2, area_padding * 2)
        restricted_area_levels = levels_button_rect.inflate(area_padding * 2, area_padding * 2)
        if restricted_area_infinite.collidepoint(mouse_x, mouse_y):
            target_x = infinite_button_rect.left - 50
            target_y = infinite_button_rect.centery
            bird_rect.centerx += (target_x - bird_rect.centerx) * 0.1
            bird_rect.centery += (target_y - bird_rect.centery) * 0.1
        elif restricted_area_levels.collidepoint(mouse_x, mouse_y):
            target_x = levels_button_rect.left - 50
            target_y = levels_button_rect.centery
            bird_rect.centerx += (target_x - bird_rect.centerx) * 0.1
            bird_rect.centery += (target_y - bird_rect.centery) * 0.1
        background.draw(screen)
        buttons.draw(screen)
        screen.blit(bird_image, bird_rect)
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

        pygame.display.flip()
        clock.tick(60)


def choose_level():
    background = Background("background-day.png", 800, 600)
    screen = background.screen
    clock = pygame.time.Clock()
    buttons = pygame.sprite.Group()
    easy_button = Button("unclicked_level_button_1.png", 'clicked_level_button_1.png', (80, 80), (100, 200), buttons)
    medium_button = Button("unclicked_level_button_2.png", 'clicked_level_button_2.png', (80, 80), (100, 300), buttons)
    hard_button = Button("unclicked_level_button_3.png", 'clicked_level_button_3.png', (80, 80), (100, 400), buttons)
    rb_btn = Button('unclicked_roll_back_button.png', 'clicked_roll_back_button.png', (80, 80), (680, 20), buttons)
    bird_images = {
        'up': pygame.image.load(os.path.join('data', 'bluebird-upflap.png')).convert_alpha(),
        'mid': pygame.image.load(os.path.join('data', 'bluebird-midflap.png')).convert_alpha(),
        'down': pygame.image.load(os.path.join('data', 'bluebird-downflap.png')).convert_alpha()
    }
    bird_state = 'mid'
    bird_image = bird_images[bird_state]
    bird_rect = bird_image.get_rect(center=(easy_button.rect.left - 50, easy_button.rect.centery))
    animation_timer = 0
    animation_speed = 10
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            buttons.update(event)
            if rb_btn.isclicked():
                return
            elif easy_button.isclicked():
                pass
            elif medium_button.isclicked():
                pass
            elif hard_button.isclicked():
                pass
        mouse_x, mouse_y = pygame.mouse.get_pos()
        easy_button_rect = easy_button.rect
        medium_button_rect = medium_button.rect
        hard_button_rect = hard_button.rect
        area_padding = 50
        restricted_area_easy = easy_button_rect.inflate(area_padding * 2, area_padding * 2)
        restricted_area_medium = medium_button_rect.inflate(area_padding * 2, area_padding * 2)
        restricted_area_hard = hard_button_rect.inflate(area_padding * 2, area_padding * 2)
        if restricted_area_easy.collidepoint(mouse_x, mouse_y):
            target_x = easy_button_rect.left - 50
            target_y = easy_button_rect.centery
            bird_rect.centerx += (target_x - bird_rect.centerx) * 0.1
            bird_rect.centery += (target_y - bird_rect.centery) * 0.1
        elif restricted_area_medium.collidepoint(mouse_x, mouse_y):
            target_x = medium_button_rect.left - 50
            target_y = medium_button_rect.centery
            bird_rect.centerx += (target_x - bird_rect.centerx) * 0.1
            bird_rect.centery += (target_y - bird_rect.centery) * 0.1
        elif restricted_area_hard.collidepoint(mouse_x, mouse_y):
            target_x = hard_button_rect.left - 50
            target_y = hard_button_rect.centery
            bird_rect.centerx += (target_x - bird_rect.centerx) * 0.1
            bird_rect.centery += (target_y - bird_rect.centery) * 0.1
        background.draw(screen)
        buttons.draw(screen)
        screen.blit(bird_image, bird_rect)
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
        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    while True:
        start_screen()
