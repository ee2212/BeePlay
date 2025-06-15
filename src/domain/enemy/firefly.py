import pygame
from pygame import Vector2

from src.domain.enemy.enemy import Enemy
from src.domain.projectile.projectile import Projectile


class Firefly(Enemy):
    def __init__(self, spawn_rect, type):
        super().__init__(spawn_rect)
        self.damage = 0
        self.type = type

        self.projectile_properties = {
            "projectile_damage": 20,
            "projectile_life_time": 35,
            "projectile_speed": 0,
            "projectile_size": (10, 10),
            "projectile_texture": pygame.image.load("./core/assets/проджектайлы/светляк взрыв.png")}

        match self.type:
            case "обычный":
                self.max_health = 40
                self.move_speed = 4
                self.size = (60, 50)
                self.projectile_properties["projectile_damage"] = 35
                self.projectile_properties["projectile_size"] = (150, 150)
            case "усиленный":
                self.max_health = 55
                self.move_speed = 4.5
                self.size = (65, 53)
                self.projectile_properties["projectile_damage"] = 48
                self.projectile_properties["projectile_size"] = (185, 185)

        self.explosion_time = 180
        self.explosion_ticks = 0
        self._move_speed = self.move_speed
        self.health = self.max_health
        self.image = pygame.image.load("./core/assets/персонажи/взрывной светляк %s.png" % type)
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(center=self.get_rand_pos(self._spawn_rect, self.spawn_shift))

    def update(self, player_pos):
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 45:
            self.rect.x += dx / distance * self.move_speed
            self.rect.y += dy / distance * self.move_speed
        else:
            self.kill()
            return [Projectile("enemy", self.rect.center, Vector2(1, 1), self.projectile_properties)]

        if self.explosion_ticks < self.explosion_time:
            self.explosion_ticks += 1
        elif self.explosion_ticks >= self.explosion_time:
            self.kill()
            return [Projectile("enemy", self.rect.center, Vector2(1, 1), self.projectile_properties)]

        if self.health <= 0:
            self.kill()
            return [Projectile("enemy", self.rect.center, Vector2(1, 1), self.projectile_properties)]

        super().update()