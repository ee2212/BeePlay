import pygame
import random

from src.managers.base_settings import screen_width, screen_height, room_width, room_height, fps_limit, poison_cooldown


class Enemy(pygame.sprite.Sprite):
    def __init__(self, spawn_rect):
        super().__init__()
        self.spawn_shift = 90
        self._spawn_rect = spawn_rect
        self.image = pygame.Surface((32, 32))
        self.image.fill((255, 0, 0))
        self._move_speed = 2
        self.move_speed = self._move_speed

        self.damage = 5
        self.max_health = 20
        self.health = self.max_health

        self.abilities = {
            "Dash": False,
            "1st hit invincibility": False,
            "1st shot invisibility": False}
        self.invincibility = False
        self.invisibility = False

        self.taken_slowdown_mult = 0
        self.taken_slowdown_time = 0
        self.deal_damage_trigger = True
        self.poison_damage = 0
        self.poison_time = 0
        self.attack_cooldown = 15
        self.attack_ticks = self.attack_cooldown
        self.taken_poison_damage = 0
        self.taken_poison_time = 0
        self.taken_poison_ticks = poison_cooldown

    def update(self):
        if self.taken_slowdown_time > 0:
            self.taken_slowdown_time -= 1
            self.move_speed = self._move_speed / self.taken_slowdown_mult
        elif self.taken_slowdown_time == 0:
            self.taken_slowdown_time = -1
            self.move_speed = self._move_speed

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