import math
import random

import pygame
from pygame import Vector2

from src.managers.base_settings import screen_width, screen_height, room_width, room_height, poison_cooldown
from src.components.health_bar import HealthBar
from src.constants.artifact_type import ArtifactType
from src.domain.boss.boss import Boss
from src.domain.projectile.projectile import Projectile


class Frog(Boss):
    def __init__(self, spawn_rect):
        super().__init__(spawn_rect)
        self.artifact = ArtifactType.FROG_LEG
        self.pollen = 200
        self.scale = (150, 100)
        self._image = pygame.image.load("./core/assets/персонажи/лягушка.png")
        self.image = self._image
        self.image = pygame.transform.scale(self.image, self.scale)
        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height // 2))

        self._move_speed = 4
        self.max_health = 400
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

        self.projectile_properties = {
            "projectile_damage": 8,
            "projectile_speed": 6,
            "projectile_poison_damage": self.poison_damage,
            "projectile_poison_time": self.poison_time,
            "projectile_texture": pygame.image.load("./core/assets/проджектайлы/слеза лягушка.png")}

    def update(self, player_pos):
        super().update()
        if self.phase_ticks == 0:
            self.image = self._image
            self.image = pygame.transform.scale(self.image, self.scale)
            self.rect = self.image.get_rect(center=self.rect.center)
            self.deal_damage_trigger = True
            rand = random.randint(1, 9)
            match rand:
                case 1 | 2 | 3:
                    self.phase = 1
                    self.phase_cooldown_mult = 0.2 + random.random()
                case 4 | 5 | 6:
                    self.phase_cooldown_mult = 0.7 + random.random()
                    self.phase = 2
                case 7 | 8:
                    if self.phase == 3:
                        self.phase = 4
                    else:
                        self.deal_damage_trigger = False
                        self.visual_state_ticks = 0
                        self.phase_cooldown_mult = 2
                        self.phase = 3
                        self.travel_target_pos = self.get_rand_pos(self._spawn_rect)
                        self.max_visual_state_ticks = int(self.phase_cooldown * self.phase_cooldown_mult)
                case 9:
                    if self.phase == 4:
                        self.phase = 3
                    else:
                        self.phase = 4
                        self.phase_cooldown_mult = 1.5 + random.random()
            self.phase_ticks = int(self.phase_cooldown * self.phase_cooldown_mult)

        print(self.phase_ticks, "   ", self.phase_cooldown, "   ", self.phase)
        match self.phase:
            case 1:
                dx = player_pos[0] - self.rect.centerx
                dy = player_pos[1] - self.rect.centery
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance > 0:
                    self.rect.x += dx / distance * self.move_speed
                    self.rect.y += dy / distance * self.move_speed
            case 2:
                if self.phase_ticks == int(self.phase_cooldown * self.phase_cooldown_mult / 2):
                    return self.shoot_all_directions("boss", self.rect.center, self.projectile_properties)
            case 3:
                if self.phase_ticks == 1:
                    return self.shoot_all_directions("boss", self.rect.center, self.projectile_properties)

                if self.visual_state_ticks <= self.phase_ticks:
                    self.visual_state_ticks += 1
                else:
                    self.visual_state_ticks -= 1

                progress = self.visual_state_ticks / self.max_visual_state_ticks
                size_x = self.scale[0] - int(self.scale[0] * progress)
                size_y = self.scale[1] - int(self.scale[1] * progress)
                alpha = int(255 * progress / 2)
                self.image = pygame.transform.scale(self._image, (size_x, size_y))
                self.image.set_alpha(min(255 - alpha, 255))
                self.rect = self.image.get_rect(center=self.rect.center)

                dx = self.travel_target_pos[0] - self.rect.centerx
                dy = self.travel_target_pos[1] - self.rect.centery - progress * 200
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance > 0:
                    self.rect.x += dx / distance * self.move_speed
                    self.rect.y += dy / distance * self.move_speed

            case 4:
                pass  # период простоя. Ничего не делает, стоит на месте

        return []

    def get_rand_pos(self, room_rect):
        x = random.randint(room_rect.left + 90, room_rect.right - 90)
        y = random.randint(room_rect.top + 90, room_rect.bottom - 90)
        return (x, y)

    def shoot_all_directions(self, source, position, effects=None):
        projectiles = []
        for _ in range(random.randint(12, 18)):
            angle = random.uniform(0, 2 * math.pi)
            direction = Vector2(math.cos(angle), math.sin(angle))
            projectile = Projectile(source, position, direction, effects)
            projectiles.append(projectile)
        return projectiles
