import pygame


class Projectile(pygame.sprite.Sprite):
    def __init__(self, source, position, direction, effects=None):
        super().__init__()
        self.effects = effects or {}
        self.image = self.effects.get('projectile_texture',
                                      pygame.image.load("./core/assets/проджектайлы/слеза по базе.png"))
        self.image = pygame.transform.scale(self.image, self.effects.get('projectile_size', (16, 16)))
        self.rect = self.image.get_rect(center=position)
        self.speed = self.effects.get('projectile_speed', 0)
        self.damage = self.effects.get('projectile_damage', 0)
        self.direction = direction.normalize()
        self.source = source
        self.poison_damage = self.effects.get('projectile_poison_damage', 0)
        self.poison_time = self.effects.get('projectile_poison_time', 0)
        self.slowdown_mult = self.effects.get('projectile_slowdown_mult', 0)
        self.slowdown_time = self.effects.get('projectile_slowdown_time', 0)
        self.life_time = self.effects.get('projectile_life_time', 300)

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        if self.life_time > 0:
            self.life_time -= 1
        elif self.life_time == 0:
            self.kill()