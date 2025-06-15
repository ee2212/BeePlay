import pygame

from src.domain.companion.companion import Companion


class Turnip(Companion):
    def __init__(self, position, companion_image, companion_name):
        super().__init__(position, companion_image, companion_name)
        self.distance_from_player = 0
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.rect = self.image.get_rect(center=(position[0] + self.distance_from_player, position[1]))
        self.damage = 3
        self.poison_damage = 15
        self.poison_time = 180
        self.attack_cooldown = 50
        self.speed = 8