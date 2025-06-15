import pygame

from src.managers.base_settings import screen_width, screen_height, room_width, room_height, poison_cooldown
from src.domain.door.door import Door


class ExitDoor(Door):
    def __init__(self):
        super().__init__("exit", 00)
        self._image = pygame.image.load("./core/assets/комнаты/дверь выход.png")
        self.size = (80, 105)
        self.draw_door(True)

    def draw_door(self, state):
        if state == True:
            self.image = self._image
            self.image = pygame.transform.scale(self.image, self.size)
            self.image.set_alpha(170)
        else:
            self.image.set_alpha(0)

        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height // 2 - room_height // 4))
