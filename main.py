import math
import os
import random
import sys

import pygame


# Класс для отслеживания счета в игре
class Counter:
    # Инициализация счета
    def __init__(self):
        self.score = 0

    # Метод для увеличения счета
    def update_score(self):
        self.score += 1


# Класс для анимации смерти персонажа
class Particle(pygame.sprite.Sprite):
    # Создание перьев
    def __init__(self, x, y, size, color, velocity, all_sprites=None):
        super().__init__()
        self.image = pygame.transform.scale(
            pygame.image.load(os.path.join('data', 'stylus.png')).convert_alpha(), (size * 2, size * 2))
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = velocity
        self.lifetime = random.randint(30, 60)
        if all_sprites:
            all_sprites.add(self)

    # Определение положения и времени жизни перьев
    def update(self, *args):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()


# Класс взаимодействия с персонажем
class Bird(pygame.sprite.Sprite):
    # Инициализация параметров птицы
    def __init__(self, x, y, all_sprites, obstacles, borders):
        super().__init__(all_sprites)
        self.obstacles = obstacles
        self.borders = borders
        self.images = {
            'up': pygame.image.load(os.path.join('data', 'bluebird-upflap.png')).convert_alpha(),
            'mid': pygame.image.load(os.path.join('data', 'bluebird-midflap.png')).convert_alpha(),
            'down': pygame.image.load(os.path.join('data', 'bluebird-downflap.png')).convert_alpha(),
            'dead': pygame.image.load(os.path.join('data', 'bluebird_dead.png')).convert_alpha()
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
        self.skidding = False
        self.skid_timer = 0
        self.all_sprites = all_sprites
        self.lose = False
        self.win = False

    # Проверка на поражение
    def islose(self):
        if self.lose:
            self.lose = False
            return True
        return False

    # Проверка на победу
    def iswin(self):
        if self.win:
            self.win = False
            return True
        return False

    # Убивают птицу и выполняют анимацию смерти
    def die(self, death_type, obstacle=None):
        self.dead = True
        self.death_type = death_type
        if death_type == "ground":
            self.vel = 0
        elif death_type == "pipe" or death_type == "ball":
            self.create_feathers_particles()
            self.kill()
            self.lose = True
        elif death_type == "top":
            self.vel = 0
        elif death_type == "bottom":
            self.vel = -20

    def create_feathers_particles(self):
        if hasattr(self, 'all_sprites') and self.all_sprites:
            for _ in range(25):
                velocity = [random.uniform(-5, 5), random.uniform(-5, 5)]
                Particle(self.rect.centerx, self.rect.centery, random.randint(5, 10),
                         (255, 0, 0), velocity, self.all_sprites)

    # Отрисовка движения птицы
    def update(self, *ev):
        if not self.dead:
            for i in self.obstacles.sprites():
                if pygame.sprite.collide_mask(self, i):
                    if isinstance(i, Pipe):
                        self.die(death_type="pipe", obstacle=i)
                    elif isinstance(i, Ball):
                        self.die(death_type="ball")
                    elif isinstance(i, Finish):
                        self.win = True
            for border in self.borders.sprites():
                if pygame.sprite.collide_mask(self, border):
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
                self.angle = min(self.angle + 5, 90)  # Поворот птицы вверх
                self.image = pygame.transform.rotate(self.images['mid'], self.angle)
                self.vel += self.gravity
                self.rect.y += self.vel
                if self.rect.y >= 600 or self.angle >= 90:
                    self.image = self.images['dead']
                    self.lose = True
            elif self.death_type == "bottom":
                self.vel += self.gravity
                self.rect.y += self.vel
                if self.rect.y >= 560:
                    self.rect.y = 560
                    self.bounce_count += 1
                    self.vel *= -0.7
                    if self.bounce_count >= self.max_bounces:
                        self.image = self.images['dead']
                        self.lose = True

    # Движение птицы вверх по нажатию "прыжка"
    def click_event(self):
        if not self.dead:
            self.vel = -10


# Класс для труб
class Pipe(pygame.sprite.Sprite):
    # Инициализация параметров труб
    def __init__(self, y, ez, all_sprites, obstacles, height, width):
        super().__init__(all_sprites)
        self.add(obstacles)
        self.y = y
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

    # Обновление счетчика и положения труб
    def update(self, *args, **kwargs):
        self.rect.x -= self.v
        if self.rect.x + 50 == 0 and not self.passed:
            self.passed = True
            args[0].update_score()
        if self.rect.x + 50 < 0:
            self.kill()


# Класс для шипованного шара
class Ball(pygame.sprite.Sprite):
    # Инициализация и определение типа движения шара
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
        self.rotation_speed = 11
        self.movement_type = random.choice([
            "bounce", "spiral", "zigzag", "chaotic", "static"
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

    # Отрисовка шара в зависимости от типа его движения
    def update(self, *args):
        self.rect.x += self.vel_x
        if self.movement_type == "bounce":
            self.rect.y += self.vel_y
            if self.rect.y + self.image.get_height() > self.height - 20 or self.rect.y < 0:
                self.vel_y *= -1
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
            args[0].update_score()


# Класс, отвечающий за нижнюю границу экрана
class Ground(pygame.sprite.Sprite):
    # Инициализация
    def __init__(self, all_sprites, borders, height, width):
        super().__init__(all_sprites)
        self.add(borders)
        self.image = pygame.transform.scale(pygame.image.load(os.path.join("data", "base.png")), (width, 20))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = height - 20

    # Возвращает высоту
    def get_height(self):
        return 20


# Класс финишна для уровней
class Finish(pygame.sprite.Sprite):
    # Инициализация
    def __init__(self, x, all_sprites, obstacles):
        super().__init__(all_sprites)
        self.add(obstacles)
        self.image = pygame.transform.scale(pygame.image.load(os.path.join("data", "finish.png")), (50, 600))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = 0
        self.v = 5

    # отрисовка
    def update(self, *args, **kwargs):
        self.rect.x -= self.v
        if self.rect.x + 50 < 0:
            self.kill()


# Класс, отвечающий за верхнюю границу экрана
class Clouds(pygame.sprite.Sprite):
    # Инициализация
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

    # Возвращает высоту
    def get_height(self):
        return 20


# Класс кнопок
class Button(pygame.sprite.Sprite):
    # Инициализация
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

    # Проверка на нажатие
    def isclicked(self):
        if self.clicked:
            self.clicked = False
            return True
        return False

    # Отрисовка с выбором нажатой/ненажатой картинки
    def update(self, *args, **kwargs):
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and \
                self.rect.collidepoint(args[0].pos):
            self.image = self.clicked_im
        if args and args[0].type == pygame.MOUSEBUTTONUP:
            self.image = self.unclicked_im
            if self.rect.collidepoint(args[0].pos):
                self.clicked = True


# Класс заднего фона
class Background:
    # Инициализация
    def __init__(self, filename, screen_width, screen_height):
        pygame.init()
        self.screen_width, self.screen_height = screen_width, screen_height
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Flappy Bird")
        self.image = pygame.transform.scale(pygame.image.load(os.path.join('data', filename)),
                                            (self.screen_width, self.screen_height))

    # Отрисовка
    def draw(self, screen):
        screen.blit(self.image, (0, 0))


# Возвращает рекорд из record.txt
def load_record():
    try:
        with open('data/record.txt', 'r') as f:
            return int(f.read())
    except:
        return 0


# Записывает рекорд в record.txt
def save_record(record):
    with open('data/record.txt', 'w') as f:
        f.write(str(record))


# Финальное окно
def game_over(screen, score, isscoring=True):
    game_over_image = pygame.transform.scale(pygame.image.load(os.path.join('data', 'game_over.png')), (400, 160))
    game_over_rect = game_over_image.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    game_over_scr = screen.copy()
    clock = pygame.time.Clock()
    score_images = []
    for i in range(10):
        score_images.append(pygame.image.load(os.path.join("data", f"{i}.png")))
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
    if isscoring:
        scoring(screen, score, game_over_rect, game_over_image, score_images, clock)


# Анимации для конечного экрана
def scoring(screen, score, game_over_rect, game_over_image, score_images, clock):
    # Позиция для отображения счета
    x = screen.get_width() // 2 - len(str(score)) * 20 // 2
    y = game_over_rect.bottom + 20
    record = load_record()
    new_record = score > record
    if new_record:
        save_record(score)
        record = score
    # Загрузка изображений для нового рекорда
    new_record_images = []
    for i in range(1, 9):  # Загружаем 8 кадров для переливов
        image = pygame.image.load(os.path.join("data", f"record{i}.png")).convert_alpha()
        new_record_images.append(image)
    # Параметры анимации нового рекорда
    new_record_index = 0  # Индекс текущего кадра
    new_record_timer = 0  # Таймер для переключения кадров
    new_record_y = -100  # Начальная позиция выше экрана
    velocity = 0  # Начальная скорость падения
    gravity = 0.5  # Ускорение свободного падения
    angle = 20  # Угол поворота (фиксированный угол 20 градусов)
    scale = 0.2  # Начальный масштаб
    scale_speed = 0.02  # Скорость увеличения масштаба
    max_scale = 0.8  # Максимальный масштаб (меньше, чем 400x160)
    bouncing = True
    final_animation = False
    confetti_active = False
    confetti_particles = []
    # Анимация счета
    for i in range(score + 1):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        # Отрисовка текущего состояния
        s = pygame.Surface((screen.get_width(), screen.get_height()))
        s.blit(game_over_image, game_over_rect)
        score_str = str(i)
        x = screen.get_width() // 2 - len(str(score)) * 20 // 2
        for digit in score_str:
            s.blit(score_images[int(digit)], (x, y))
            x += 20
        screen.blit(s, (0, 0))
        pygame.display.flip()
        # Настройка скорости отображения счета
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
    # Анимация нового рекорда
    sparkle_active = False
    while bouncing or final_animation or sparkle_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        # Логика падения
        if bouncing:
            velocity += gravity
            new_record_y += velocity
            scale += scale_speed
            if new_record_y >= 500:  # Фиксируем позицию ещё ниже (например, 500)
                new_record_y = 500
                velocity = -velocity * 0.7
                if abs(velocity) < 2:
                    bouncing = False
                    final_animation = True
        # Логика финальной анимации
        if final_animation:
            if scale < max_scale:
                scale += 0.01
            if scale >= max_scale:
                final_animation = False
                sparkle_active = True
        # Отрисовка
        s = pygame.Surface((screen.get_width(), screen.get_height()))
        s.blit(game_over_image, game_over_rect)
        score_str = str(score)
        x = screen.get_width() // 2 - len(str(score)) * 20 // 2
        for digit in score_str:
            s.blit(score_images[int(digit)], (x, y))
            x += 20
        if sparkle_active:
            new_record_timer += 1
            if new_record_timer >= 9:
                new_record_timer = 0
                new_record_index = (new_record_index + 1) % len(new_record_images)
            current_image = new_record_images[new_record_index]
        else:
            current_image = new_record_images[0]

        scaled_size = (
            int(current_image.get_width() * scale),
            int(current_image.get_height() * scale)
        )
        max_width, max_height = 320, 128  # Ограничение максимального размера
        if scaled_size[0] > max_width or scaled_size[1] > max_height:
            scaled_size = max_width, max_height
        scaled_image = pygame.transform.scale(current_image, scaled_size)
        rotated_image = pygame.transform.rotate(scaled_image, angle)
        rotated_rect = rotated_image.get_rect(center=(screen.get_width() // 2, new_record_y))
        s.blit(rotated_image, rotated_rect.topleft)
        screen.blit(s, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    # Ожидание завершения
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                return


# Cтартовое окно
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
    animation_speed = 10
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            buttons.update(event)
            if playbutton.isclicked():
                choose_game_mode(screen, background)
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


# Выбор режима игры
def choose_game_mode(screen, background):
    clock = pygame.time.Clock()
    buttons = pygame.sprite.Group()
    infinite_button = Button("unclicked_endless_mode_button.png", "clicked_endless_mode_button.png",
                             (150, 80), (100, 210), buttons)
    levels_button = Button("unclicked_levels_button.png", "clicked_levels_button.png",
                           (150, 80), (100, 310), buttons)
    rb_btn = Button('unclicked_roll_back_button.png', 'clicked_roll_back_button.png',
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
    animation_speed = 10
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            buttons.update(event)
            if infinite_button.isclicked():
                main(screen)
                return
            elif rb_btn.isclicked():
                return
            elif levels_button.isclicked():
                choose_level(screen, background)
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


# Выбор уровня
def choose_level(screen, background):
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
                main(screen, 'eazy')
            elif medium_button.isclicked():
                main(screen, 'medium')
            elif hard_button.isclicked():
                main(screen, 'hard')
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


# Надпись "победа" при прохождении уровня
def win(screen, initial_scale=10.0, target_scale=3.0, scale_speed=0.1):
    last_frame = screen.copy()
    try:
        image = pygame.image.load(os.path.join("data", "win.png")).convert_alpha()
    except FileNotFoundError:
        print("Ошибка: Файл 'stamp.png' не найден в папке 'data'.")
        return
    original_size = image.get_size()
    scale = initial_scale
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        scale = max(scale - scale_speed, target_scale)
        screen.blit(last_frame, (0, 0))
        scaled_size = (int(original_size[0] * scale), int(original_size[1] * scale))
        scaled_image = pygame.transform.smoothscale(image, scaled_size)
        scaled_rect = scaled_image.get_rect(center=screen.get_rect().center)
        screen.blit(scaled_image, scaled_rect.topleft)
        if scale <= target_scale:
            pygame.time.wait(2000)
            return

        pygame.display.flip()
        clock.tick(60)


# Создание легкого уровня
def make_easy_level(size, all_sprites, obstacles):
    pygame.display.set_caption('Flappy Bird Easy Level')
    eazy = 250
    x = size[0]
    y = 150
    for i in range(24):
        Pipe(y, eazy, all_sprites, obstacles, size[1], x)
        x += 250
        if i <= 11:
            y += 30
        else:
            y -= 30
    Finish(x, all_sprites, obstacles)


# Создание среднего уровня
def make_medium_level(size, all_sprites, obstacles):
    pygame.display.set_caption('Flappy Bird Medium Level')
    medium = 180
    x = size[0]
    y = 250
    for i in range(24):
        Pipe(y, medium, all_sprites, obstacles, size[1], x)
        x += 225
        if i % 2 == 0:
            y += 50
        else:
            y -= 50
    Finish(x, all_sprites, obstacles)


# Основа игры
def main(screen, level='infinity'):
    pygame.mixer.init()
# Установка названия окна игры
    pygame.display.set_caption('Flappy Bird Easy Level')
# Создание групп спрайтов
    try:
        pygame.mixer.music.load(os.path.join("data", "C418 — Aria Math (Synthwave remix).mp3"))
        # Загружаем фоновую музыку
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except pygame.error as e:
        print(f"Ошибка загрузки музыки: {e}")
    try:
        # Загружаем фоновую музыку смерти
        death_sound = pygame.mixer.Sound(os.path.join("data", "die.mp3"))
        death_sound.set_volume(0.7)
    except pygame.error as e:
        print(f"Ошибка загрузки звука смерти: {e}")
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    borders = pygame.sprite.Group()
    buttons = pygame.sprite.Group()
# Создание кнопки "Назад"
    rb_btn = Button('unclicked_roll_back_button.png', 'clicked_roll_back_button.png', (80, 80), (680, 20), buttons)
# Создание основных объектов
    size = width, height = screen.get_size()
    br = Bird(100, 300, all_sprites, obstacles, borders)
    Clouds(all_sprites, borders, width)
    Ground(all_sprites, borders, height, width)
    clock = pygame.time.Clock()
    cnt = Counter()
    cnt.score = 0
# Загрузка изображений цифр для отображения счета
    score_images = []
    for i in range(10):
        score_images.append(pygame.image.load(os.path.join("data", f"{i}.png")))
# Установка таймера для бесконечного уровня
    if level == 'infinity':
        MYEVENTTYPE = pygame.USEREVENT + 1
        pygame.time.set_timer(MYEVENTTYPE, 1300)
        eazy = 300
        time = 0
# Создание уровня в зависимости от выбранного уровня сложности
    if level == 'eazy':
        make_easy_level(size, all_sprites, obstacles)
    if level == 'medium':
        make_medium_level(size, all_sprites, obstacles)
    if level == 'hard':
        MYEVENTTYPE2 = pygame.USEREVENT + 2
        pygame.time.set_timer(MYEVENTTYPE2, 500)
        ball_cnt = 0
# Создание экрана паузы
    pause_screen = pygame.Surface((screen.get_width(), screen.get_height()))
    pause_screen.set_alpha(70)
    pause = False
# Загрузка изображения фона
    background_image = pygame.transform.scale(pygame.image.load(os.path.join("data", "background-day.png")),
                                              (width, height))
# Основной цикл игры
    while True:
        for event in pygame.event.get():
            if not pause:
                rb_btn.kill()
                pygame.mouse.set_visible(False)
                if level == 'hard':
                    if ball_cnt <= 100:
                        if event.type == MYEVENTTYPE2:
                            for i in range(3):
                                Ball(all_sprites, obstacles, width, height)
                                ball_cnt += 1
                    else:
                        Finish(800, all_sprites, obstacles)
                if level == 'infinity':
                    if event.type == MYEVENTTYPE:
                        time += 1
                        if time % 10 == 0 and eazy > 100:
                            eazy -= 40
                        if time // 20 >= 1:
                            is_pipe = random.choice((False, True))
                            if is_pipe:
                                Pipe(random.choice(range(eazy // 2, size[1] - eazy // 2 + 1)), eazy, all_sprites,
                                     obstacles,
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
                pygame.mixer.music.stop()
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
            if br.islose():
                death_sound.play()
                pygame.mixer.music.stop()
                pygame.mouse.set_visible(True)
                if not (level == 'infinity'):
                    game_over(screen, cnt.score, False)
                game_over(screen, cnt.score)
                return
            if br.iswin():
                pygame.mixer.music.stop()
                pygame.mouse.set_visible(True)
                win(screen)
                return

        if not pause:
            screen.blit(background_image, (0, 0))
            all_sprites.update(cnt)
            all_sprites.draw(screen)
            borders.draw(screen)
            if level == 'infinity':
                score = cnt.score
                x = width // 2 - len(str(score)) * 20 // 2
                for digit in str(score):
                    screen.blit(score_images[int(digit)], (x, height // 2 - 20))
                    x += 20

        pygame.display.flip()
        clock.tick(50)


# Основная точка входа в программу
if __name__ == '__main__':
    while True:
        start_screen()
