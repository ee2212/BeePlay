import pygame
from pygame import Vector2

from src.constants.room_type import RoomType


class Companion(pygame.sprite.Sprite):
    def __init__(self, position, companion_image, companion_name):
        super().__init__()
        self.distance_from_player = 90

        self.name = companion_name
        self.image = companion_image
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect(center=(position[0] + self.distance_from_player, position[1]))

        self.damage = 2

        self.speed = self.distance_from_player // 30 + 0.2 * self.distance_from_player // 30
        self.angle = self.speed * 7
        self.vec = Vector2(1, 0)
        self.rotation_cooldown = self.angle // 2
        self.rotation_ticks = self.rotation_cooldown

        self.attack_cooldown = 80
        self.attack_ticks = self.attack_cooldown
        self.poison_damage = 0
        self.poison_time = 0

    def update(self, current_room, position):
        if current_room != RoomType.COMBAT:
            if self.rotation_ticks > 0:
                self.rotation_ticks -= 1
            else:
                self.rotation_ticks = self.rotation_cooldown
                self.vec = Vector2.rotate(self.vec, self.angle)

            dx = (position[0] + self.vec[0] * self.distance_from_player) - self.rect.centerx
            dy = (position[1] + self.vec[1] * self.distance_from_player) - self.rect.centery
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance > 3:
                self.rect.x += dx / distance * self.speed
                self.rect.y += dy / distance * self.speed

            if self.attack_ticks > 0:
                self.attack_ticks -= 1