import pygame

from src.components.buttons.button import Button


class MultiStateButton(Button):
    def __init__(self, button_type, button_state, button_number, button_size, button_pos):
        super().__init__(button_type, button_size, button_pos)
        self.button_state = button_state
        self.button_number = button_number
        self.image = pygame.image.load(
            "./core/assets/кнопки/%s_%s_%s.png" % (self.button_type, self.button_state, self.button_number))
        self.image = pygame.transform.scale(self.image, self.button_size)
        self.rect = self.image.get_rect(center=button_pos)

    def update_appearance(self):
        self.image = pygame.image.load(
            "./core/assets/кнопки/%s_%s_%s.png" % (self.button_type, self.button_state, self.button_number))
        if self.highlighted and self.button_state != "закр":
            self.image = pygame.image.load(
                "./core/assets/кнопки/%s_%s_%s_подсвет.png" % (self.button_type, self.button_state, self.button_number))
        self.image = pygame.transform.scale(self.image, self.button_size)
