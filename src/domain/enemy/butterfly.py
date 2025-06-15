import pygame

from src.domain.enemy.enemy import Enemy


class Butterfly(Enemy):
    def __init__(self, spawn_rect, type):
        super().__init__(spawn_rect)
        self.damage = 0
        self.type = type
        match self.type:
            case "обычный":
                self.attack_cooldown = 20
                self.poison_damage = 10
                self.poison_time = 180
                self.max_health = 65
                self.move_speed = 2.5
                self.size = (42, 70)
            case "усиленный":
                self.attack_cooldown = 10
                self.max_health = 90
                self.move_speed = 3
                self.size = (55, 85)

        self._move_speed = self.move_speed
        self.health = self.max_health
        self.image = pygame.image.load("./core/assets/персонажи/бабочка %s.png" % type)
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(center=self.get_rand_pos(self._spawn_rect, self.spawn_shift))

    def update(self, player_pos):
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:
            self.rect.x += dx / distance * self.move_speed
            self.rect.y += dy / distance * self.move_speed

        super().update()