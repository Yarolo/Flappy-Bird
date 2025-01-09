import random
import pygame
import os


def main():
    def load_image(name, color_key=None):
        fullname = os.path.join('data', name)
        try:
            image = pygame.image.load(fullname)
        except pygame.error as message:
            print('Не удаётся загрузить:', name)
            raise SystemExit(message)
        image = image.convert_alpha()
        if color_key is not None:
            if color_key == -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
        return image


    class Bird(pygame.sprite.Sprite):
        def __init__(self, radius, x, y):
            super().__init__(all_sprites)
            self.radius = radius
            self.image = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA, 32)
            pygame.draw.circle(self.image, pygame.Color("red"), (radius, radius), radius)
            self.rect = pygame.Rect(x, y, 2 * radius, 2 * radius)
            self.vel = 0
            self.gravity = 0

        def update(self, *ev):
            nonlocal running
            for i in pipes.sprites():
                if pygame.sprite.collide_mask(self, i):
                    running = False
            if pygame.sprite.spritecollideany(self, borders):
                running = False
            self.rect.y += self.vel
            self.vel += self.gravity

        def click_event(self):
            self.gravity = 1
            self.vel = -10

    class Pipe(pygame.sprite.Sprite):
        def __init__(self, y, ez):
            super().__init__(all_sprites)
            self.add(pipes)
            self.y = y
            self.ez = ez
            self.image = pygame.Surface([50, height])
            self.rect = self.image.get_rect()
            self.image.fill('green')
            self.image.fill(pygame.Color('white'), pygame.Rect(0, self.y - self.ez // 2, 50, self.ez))
            self.image.set_colorkey(pygame.Color('white'))
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_rect()
            self.rect.x = weight
            self.rect.y = 0
            self.v = 5

        def update(self, *args, **kwargs):
            self.rect.x -= self.v
            if self.rect.x + 40 == 0:
                self.kill()
    class Ground(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__(all_sprites)
            self.add(borders)
            self.image = pygame.Surface([weight, 20])
            self.rect = self.image.get_rect()
            self.image.fill('brown')
            self.image.set_colorkey(pygame.Color('white'))
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_rect()
            self.rect.x = 0
            self.rect.y = height-20

    class Clouds(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__(all_sprites)
            self.add(borders)
            self.image = pygame.Surface([weight, 20])
            self.rect = self.image.get_rect()
            self.image.fill('blue')
            self.image.set_colorkey(pygame.Color('white'))
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_rect()
            self.rect.x = 0
            self.rect.y = 0

    pygame.display.set_caption('test_bird_window')
    all_sprites = pygame.sprite.Group()

    size = weight, height = 800, 600
    screen = pygame.display.set_mode(size)
    br = Bird(20, 100, 300)
    clock = pygame.time.Clock()
    pipes = pygame.sprite.Group()
    borders = pygame.sprite.Group()
    Clouds()
    Ground()
    MYEVENTTYPE = pygame.USEREVENT + 1
    pygame.time.set_timer(MYEVENTTYPE, 1300)
    eazy = 300
    time = 0
    running = True
    ans = False
    while running:
        for event in pygame.event.get():
            if event.type == MYEVENTTYPE:
                Pipe(random.choice(range(eazy // 2, size[1] - eazy // 2 + 1)), eazy)
                time += 1
                if time == 20 and eazy > 100:
                    eazy -= 40
                    time = 0
            if event.type == pygame.MOUSEBUTTONDOWN:
                br.click_event()
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        screen.fill(pygame.Color("black"))
        all_sprites.update(event)
        all_sprites.draw(screen)
        borders.draw(screen)
        pygame.display.flip()
        clock.tick(50)
    pygame.quit()


if __name__ == '__main__':
    main()
