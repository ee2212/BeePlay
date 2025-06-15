import pygame
import random
from pygame import Vector2

from src.domain.enemy.enemy import Enemy
from src.domain.projectile.projectile import Projectile


class Worm(Enemy):
    def __init__(self, spawn_rect, type):
        super().__init__(spawn_rect)
        self.health = self.max_health
        self.image = pygame.image.load("./core/assets/персонажи/червь %s.png" % type)
        self._image = self.image
        self.size = (80, 80)
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(center=self.get_rand_pos(self._spawn_rect, self.spawn_shift))

        self.phase = 1
        self.max_visual_state_ticks = 120
        self.visual_state_ticks = 0

        self.projectile_properties = {
            "projectile_damage": self.damage,
            "projectile_speed": 10,
            "projectile_texture": pygame.image.load("./core/assets/проджектайлы/слеза грязь.png")}

        match type:
            case "обычный":
                self.attack_cooldown = 35
                self.max_health = 40
                self.projectile_properties["projectile_speed"] = 5
                self._phase_ticks = random.randint(150, 300)
                self.phase_ticks = self._phase_ticks
            case "усиленный":
                self.attack_cooldown = 17
                self.max_health = 55
                self.projectile_properties["projectile_speed"] = 7
                self._phase_ticks = random.randint(100, 200)
                self.phase_ticks = self._phase_ticks
        self.health = self.max_health

    def update(self, player_pos):
        super().update()

        if self.phase_ticks > 0:
            self.phase_ticks -= 1
        else:
            match self.phase:
                case 1:
                    self.phase_ticks = 100
                    self.phase = 2
                case 2:
                    self.visual_state_ticks = 0
                    self.phase_ticks = self._phase_ticks
                    self.image = self._image
                    self.image = pygame.transform.scale(self.image, self.size)
                    self.rect = self.image.get_rect(center=self.get_rand_pos(self._spawn_rect, self.spawn_shift))
                    self.phase = 1

        if self.phase == 1:
            if self.attack_ticks == 0:
                self.attack_ticks = self.attack_cooldown
                direction = Vector2(player_pos) - Vector2(self.rect.center)
                if direction.length() > 0:
                    projectile = [Projectile("enemy", self.rect.center, direction, self.projectile_properties)]
                    return projectile

        elif self.phase == 2 and self.visual_state_ticks <= self.max_visual_state_ticks:
            self.visual_state_ticks += 1
            progress = self.visual_state_ticks / self.max_visual_state_ticks
            size_x = self.size[0] - int(self.size[0] * progress)
            size_y = self.size[1] - int(self.size[1] * progress)
            alpha = int(255 * progress)
            self.image = pygame.transform.scale(self._image, (size_x, size_y))
            self.image.set_alpha(min(255 - alpha, 255))
            self.rect = self.image.get_rect(center=self.rect.center)
