import math
import random

import pygame
from pygame import Vector2

from src.managers.base_settings import screen_width, screen_height, room_width, room_height, poison_cooldown
from src.components.health_bar import HealthBar
from src.constants.artifact_type import ArtifactType
from src.domain.boss.boss import Boss
from src.domain.projectile.projectile import Projectile


class Rat(Boss):
    def __init__(self, spawn_rect):
        super().__init__(spawn_rect)
        self.artifact = ArtifactType.RAT_TAIL
        self.pollen = 275
        self.scale = (120, 80)
        self._image = pygame.image.load("./core/assets/персонажи/крыса альбинос.png")
        self.image = self._image
        self.image = pygame.transform.scale(self.image, self.scale)
        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height // 2))

        self._move_speed = 7.5

        self.max_health = 475
        self.health = self.max_health
        self.health_bar = HealthBar(screen_width // 2 - room_width // 2, screen_height // 2 - room_height // 2,
                                    room_width, screen_height // 70, \
                                    self.max_health, pygame.Color(255, 87, 87), pygame.Color(79, 79, 79))

        self.damage = 18
        self.poison_damage = 0
        self.poison_time = 0

        self.phase = 0
        self.phase_cooldown_mult = 1
        self.phase_ticks = self.phase_cooldown / 2
        self.taken_poison_damage = 0
        self.taken_poison_time = 0
        self.taken_poison_ticks = poison_cooldown

        self.max_visual_state_ticks = self.phase_cooldown * 3
        self.visual_state_ticks = 0

        self.travel_direction = Vector2(0, 0)
        self.dash_quantity = 3
        self.dash_counter = 0

        self.projectiles_quantity = 3
        self.projectile_counter = 0
        self.projectile_properties = {
            "projectile_damage": self.damage,
            "projectile_speed": 12,
            "projectile_poison_damage": self.poison_damage,
            "projectile_poison_time": self.poison_time,
            "projectile_texture": pygame.image.load("./core/assets/проджектайлы/слеза крыса.png")}

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
                    if self.phase == 1:
                        self.phase = 3
                    else:
                        self.projectiles_quantity = 3
                        self.projectile_counter = 0
                        self.phase = 1
                        self.phase_cooldown_mult = 0.2 + random.random()
                case 4 | 5 | 6:
                    self.phase_cooldown_mult = 0.7 + random.random()
                    if self.phase == 2 or self.phase == 1:
                        self.phase = 3
                    else:
                        self.projectiles_quantity = 9
                        self.projectile_counter = 0
                        self.visual_state_ticks = 0
                        self.phase_cooldown_mult = 2
                        self.phase = 2
                        self.travel_target_pos = player_pos
                        self.travel_direction = (
                                Vector2(self.travel_target_pos) - Vector2(self.rect.center)).normalize()
                case 7 | 8 | 9:
                    self.phase = 3
                    self.phase_cooldown_mult = 0.5 ** random.random()

            self.phase_ticks = int(self.phase_cooldown * self.phase_cooldown_mult)

        match self.phase:
            case 1:  # 3 bullets shot at player
                bullets = []
                if self.phase_ticks \
                        == int(self.phase_cooldown * self.phase_cooldown_mult / self.projectiles_quantity * (
                        self.projectiles_quantity - self.projectile_counter)):
                    direction = Vector2(player_pos) - Vector2(self.rect.center)
                    if direction.length() > 0:
                        self.projectile_properties["projectile_speed"] = 12
                        self.projectile_properties["projectile_life_time"] = 200
                        self.projectile_counter += 1
                        bullet = Projectile("boss", self.rect.center, direction, self.projectile_properties)
                        bullets.append(bullet)
                return bullets

            case 2:  # 3 dashes to player last position and leaving bullets
                wall_correct = 50
                self.rect.clamp_ip(pygame.Rect((screen_width - room_width) // 2 + wall_correct * 1.2, \
                                               (screen_height - room_height) // 2 + wall_correct,
                                               room_width - wall_correct * 2.2, room_height - wall_correct * 2))

                bullets = []
                if self.phase_ticks == 1:
                    self.dash_counter = 0
                    self.projectile_counter = 0

                if self.phase_ticks == \
                        int(self.phase_cooldown * self.phase_cooldown_mult / self.dash_quantity * (
                                self.dash_quantity - self.dash_counter)):
                    self.dash_counter += 1
                    self.travel_target_pos = player_pos
                    self.travel_direction = (Vector2(self.travel_target_pos) - Vector2(self.rect.center)).normalize()
                # print("self.dash_counter:", self.dash_counter," self.dash_quantity:",self.dash_quantity,\
                #       " self.attack_cooldown:",self.attack_cooldown," self.attack_ticks:",self.attack_ticks)

                if self.phase_ticks \
                        == int(self.phase_cooldown * self.phase_cooldown_mult / self.projectiles_quantity * (
                        self.projectiles_quantity - self.projectile_counter)):
                    self.projectile_properties["projectile_speed"] = 0
                    self.projectile_properties["projectile_life_time"] = 100
                    self.projectile_counter += 1
                    bullet = Projectile("boss", self.rect.center, Vector2(1, 1), self.projectile_properties)
                    bullets.append(bullet)

                self.rect.x += self.travel_direction.x * self.move_speed
                self.rect.y += self.travel_direction.y * self.move_speed

                return bullets
            case 3:
                pass

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