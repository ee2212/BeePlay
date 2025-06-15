import pygame

class HealthBar:
    def __init__(self, x, y, w, h, max_hp, color_hp, color_max_hp):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.hp, self.max_hp = max_hp, max_hp
        self.color_max_hp, self.color_hp = color_max_hp, color_hp

    def draw(self, surface, shift):
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, self.color_max_hp, (self.x + shift * 150, self.y + shift * 50, self.w, self.h))
        pygame.draw.rect(surface, self.color_hp, (self.x + shift * 150, self.y + shift * 50, self.w * ratio, self.h))

