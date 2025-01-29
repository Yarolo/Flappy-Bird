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

    def update(self, *ev):
        global running
        global game_over_screen
        for i in self.obstacles.sprites():
            if pygame.sprite.collide_mask(self, i):
                running = False
                game_over_screen = True
        if pygame.sprite.spritecollideany(self, self.borders):
            running = False
            game_over_screen = True
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


class RollBackButton(pygame.sprite.Sprite):
    def __init__(self, buttons):
        super().__init__(buttons)
        self.unclicked = pygame.image.load(os.path.join('data', 'unclicked_roll_back_button.png')).convert_alpha()
        self.clicked = pygame.image.load(os.path.join('data', 'clicked_roll_back_button.png')).convert_alpha()
        self.unclicked = pygame.transform.scale(self.unclicked, (80, 80))
        self.clicked = pygame.transform.scale(self.clicked, (80, 80))
        self.image = self.unclicked
        self.rect = self.image.get_rect()
        self.rect.x = 680
        self.rect.y = 20

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


class Button(pygame.sprite.Sprite):
    def __init__(self, text, pos, group):
        super().__init__(group)
        self.image = pygame.Surface((200, 50))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(topleft=pos)
        self.text = text
        self.pressed = False
        self.font = pygame.font.Font(None, 36)
        self.text_surface = self.font.render(self.text, True, (0, 0, 0))
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.pressed = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        screen.blit(self.text_surface, self.text_rect)


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
    rb_btn = RollBackButton(buttons)
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
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and not pause:
                rb_btn = RollBackButton(buttons)
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
    global running
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
    playbutton = PlayButton(buttons)
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
            elif event.type == pygame.MOUSEBUTTONUP and playbutton.clicked and playbutton.rect.collidepoint(event.pos):
                choose_game_mode()
            buttons.update(event)
        if not (running):
            running = True
            return
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
    infinite_button = Button("Бесконечный режим", (100, 200), buttons)
    levels_button = Button("Уровни", (100, 300), buttons)
    rb_btn = RollBackButton(buttons)
    levels_button_clicked = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            buttons.update(event)
            if event.type == pygame.MOUSEBUTTONDOWN and rb_btn.rect.collidepoint(event.pos):
                rb_btn.image = rb_btn.clicked
            elif event.type == pygame.MOUSEBUTTONDOWN and infinite_button.pressed and infinite_button.rect.collidepoint(
                    event.pos):
                main()
            elif event.type == pygame.MOUSEBUTTONUP and rb_btn.rect.collidepoint(event.pos):
                return
            elif event.type == pygame.MOUSEBUTTONDOWN and levels_button.rect.collidepoint(event.pos):
                levels_button_clicked = True

        background.draw(screen)
        buttons.draw(screen)
        screen.blit(rb_btn.image, rb_btn.rect)
        pygame.display.flip()
        clock.tick(60)
        if levels_button_clicked:
            choose_level()
            levels_button_clicked = False


def choose_level():
    background = Background("background-day.png", 800, 600)
    screen = background.screen
    clock = pygame.time.Clock()
    buttons = pygame.sprite.Group()
    easy_button = Button("Легкий", (100, 200), buttons)
    medium_button = Button("Средний", (100, 300), buttons)
    hard_button = Button("Сложный", (100, 400), buttons)
    rb_btn = RollBackButton(buttons)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            buttons.update(event)
            if event.type == pygame.MOUSEBUTTONDOWN and rb_btn.rect.collidepoint(event.pos):
                rb_btn.image = rb_btn.clicked
            elif event.type == pygame.MOUSEBUTTONUP and rb_btn.rect.collidepoint(event.pos):
                return
        background.draw(screen)
        buttons.draw(screen)
        screen.blit(rb_btn.image, rb_btn.rect)
        pygame.display.flip()
        clock.tick(60)
        if easy_button.pressed:
            pass
        elif medium_button.pressed:
            pass
        elif hard_button.pressed:
            pass


if __name__ == '__main__':
    while True:
        start_screen()
