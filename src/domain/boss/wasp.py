import math
import random

import pygame
from pygame import Vector2

from src.managers.base_settings import screen_width, screen_height, room_width, room_height, poison_cooldown
from src.components.health_bar import HealthBar
from src.constants.artifact_type import ArtifactType
from src.domain.boss.boss import Boss
from src.domain.projectile.projectile import Projectile
from src.domain.boss.boss import Boss


class Wasp(Boss):
    def __init__(self, spawn_rect):
        super().__init__(spawn_rect)
        self.artifact = ArtifactType.WASP_STINGER
        self.pollen = 1000
        self.scale = (150, 150)
        self._image = pygame.image.load("./core/assets/персонажи/оса пепси.png")
        self.image = self._image
        self.image = pygame.transform.scale(self.image, self.scale)
        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height // 2))

        self._move_speed = 7
        self.max_health = 700
        self.health = self.max_health
        self.health_bar = HealthBar(screen_width // 2 - room_width // 2, screen_height // 2 - room_height // 2,
                                    room_width, screen_height // 70, 
                                    self.max_health, pygame.Color(255, 87, 87), pygame.Color(79, 79, 79))

        self.damage = 15
        self.poison_damage = 0
        self.poison_time = 0

        self.phase = 0
        self.phase_cooldown = 50
        self.phase_cooldown_mult = 1
        self.phase_ticks = self.phase_cooldown / 2
        self.taken_poison_damage = 0
        self.taken_poison_time = 0
        self.taken_poison_ticks = poison_cooldown

        self.max_visual_state_ticks = self.phase_cooldown * 3
        self.visual_state_ticks = 0
        self.travel_target_pos = self.get_rand_pos(spawn_rect)


    def update(self, player_pos):
        super().update()
        self.image = self._image
        self.image = pygame.transform.scale(self.image, self.scale)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.deal_damage_trigger = True

        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:
            self.rect.x += dx / distance * self.move_speed
            self.rect.y += dy / distance * self.move_speed
           
        return []

    def get_rand_pos(self, room_rect):
        x = random.randint(room_rect.left + 90, room_rect.right - 90)
        y = random.randint(room_rect.top + 90, room_rect.bottom - 90)
        return (x, y)

