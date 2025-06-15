import pygame
import random


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, room_rect):
        super().__init__()
        self.size = (35, 45)
        self.image = pygame.image.load("./core/assets/комнаты/препятствие.png")
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(center=self.get_rand_pos(room_rect))
        self.slowdown_mult = 3

    def get_rand_pos(self, room_rect):
        x = random.randint(room_rect.left + 90, room_rect.right - 90)
        y = random.randint(room_rect.top + 90, room_rect.bottom - 90)
        return (x, y)