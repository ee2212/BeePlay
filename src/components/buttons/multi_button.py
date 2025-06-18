import pygame

from src.components.buttons.button import Button


class MultiButton(Button):
    def __init__(self, button_type, button_number, button_size, button_pos):
        super().__init__(button_type, button_size, button_pos)
        self.button_number = button_number
        self.image = pygame.image.load("./core/assets/кнопки/%s_%s.png" % (self.button_type, self.button_number))
        self.image = pygame.transform.scale(self.image, self.button_size)
        self.rect = self.image.get_rect(center=button_pos)

    def update_appearance(self):
        self.image = pygame.image.load("./core/assets/кнопки/%s_%s.png" % (self.button_type, self.button_number))
        if self.highlighted:
            self.image = pygame.image.load(
                "./core/assets/кнопки/%s_%s_подсвет.png" % (self.button_type, self.button_number))
        self.image = pygame.transform.scale(self.image, self.button_size)
