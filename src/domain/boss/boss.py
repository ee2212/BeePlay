import random
import pygame

from src.managers.base_settings import screen_width, screen_height, room_width, room_height, poison_cooldown
from src.components.health_bar import HealthBar


class Boss(pygame.sprite.Sprite):
    def __init__(self, spawn_rect):
        super().__init__()
        self.spawn_shift = 90
        self._spawn_rect = spawn_rect
        self.image = pygame.Surface((32, 32))
        self.image.fill((255, 0, 0))

        self.pollen = 100
        self._move_speed = 3
        self.move_speed = self._move_speed

        self.abilities = {
            "Dash": False,
            "1st hit invincibility": False,
            "1st shot invisibility": False}
        self.invincibility = False
        self.invisibility = False

        self.max_health = 20
        self.health = self.max_health
        self.health_bar = HealthBar(screen_width // 2 - room_width // 2, screen_height // 2 - room_height // 2, 10,
                                    screen_height // 70, \
                                    self.max_health, pygame.Color(255, 87, 87), pygame.Color(79, 79, 79))

        self.damage = 20
        self.poison_damage = 0
        self.poison_time = 0

        self.phase_cooldown = 50
        self.phase_ticks = self.phase_cooldown
        self.attack_cooldown = 20
        self.attack_ticks = self.attack_cooldown
        self.deal_damage_trigger = True
        self.taken_slowdown_mult = 0
        self.taken_slowdown_time = 0
        self.taken_poison_damage = 0
        self.taken_poison_time = 0
        self.taken_poison_ticks = poison_cooldown

        self.phase = 1
        self.phase_ticks = random.randint(250, 450)
        self.max_visual_state_ticks = 120
        self.visual_state_ticks = 0

    def update(self):
        self.health_bar.hp = self.health

        if self.taken_slowdown_time > 0:
            self.taken_slowdown_time -= 1
            self.move_speed = self._move_speed / self.taken_slowdown_mult
        elif self.taken_slowdown_time == 0:
            self.taken_slowdown_time = -1
            self.move_speed = self._move_speed

        if self.phase_ticks > 0:
            self.phase_ticks -= 1

        if self.attack_ticks > 0:
            self.attack_ticks -= 1

        if self.taken_poison_time > 0:
            self.taken_poison_time -= 1
            self.inflict_poison_damage()

        if self.health <= 0:
            self.kill()

    def get_rand_pos(self, spawn_rect, shift):
        x = random.randint(spawn_rect.left + shift, spawn_rect.right - shift)
        y = random.randint(spawn_rect.top + shift, spawn_rect.bottom - shift)
        return (x, y)

    def inflict_poison_damage(self):
        if self.taken_poison_ticks > 0:
            self.taken_poison_ticks -= 1
        else:
            self.taken_poison_ticks = poison_cooldown
            self.health -= self.taken_poison_damage