import pygame
from pygame import Vector2

from src.domain.companion.companion import Companion
from src.domain.projectile.projectile import Projectile


class Fly(Companion):
    def __init__(self, position, companion_image, companion_name):
        super().__init__(position, companion_image, companion_name)
        self.distance_from_player = 80
        self.damage = 2
        self.attack_cooldown = 35
        self.attack_ticks = self.attack_cooldown
        self.projectile_properties = {
            "projectile_damage": self.damage * 3,
            "projectile_speed": 5,
            "projectile_texture": pygame.image.load("./core/assets/проджектайлы/слеза мухо.png"),
            "projectile_size": (10, 10)}

    def update(self, current_room, position, mouse_pos):
        super().update(current_room, position)

        if self.attack_ticks == 0:
            self.attack_ticks = self.attack_cooldown
            direction = Vector2(mouse_pos) - Vector2(self.rect.center)
            if direction.length() > 0:
                projectiles = [Projectile("player", self.rect.center, direction, self.projectile_properties)]
                return projectiles
        return []