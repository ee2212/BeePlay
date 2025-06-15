import pygame
import os

class Button(pygame.sprite.Sprite):
    def __init__(self, button_type, button_size, button_pos):
        super().__init__()
        self.button_type = button_type
        self.button_size = button_size
        if os.path.exists("./core/assets/кнопки/%s.png" % self.button_type):
            self.image = pygame.image.load("./core/assets/кнопки/%s.png" % self.button_type)
            self.image = pygame.transform.scale(self.image, self.button_size)
            self.rect = self.image.get_rect(center=button_pos)
        else:
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 0, 0))
        self.highlighted = False

    def update_appearance(self):
        self.image = pygame.image.load("./core/assets/кнопки/%s.png" % self.button_type)
        if self.highlighted:
            self.image = pygame.image.load("./core/assets/кнопки/%s_подсвет.png" % self.button_type)
        self.image = pygame.transform.scale(self.image, self.button_size)
