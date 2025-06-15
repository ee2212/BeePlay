import pygame

from src.managers.base_settings import screen_width, screen_height, room_width, room_height, poison_cooldown


class Door(pygame.sprite.Sprite):
    def __init__(self, direction, room_id):
        super().__init__()
        self._image = pygame.image.load("./core/assets/комнаты/двери листики открытые.png")
        self.size = (90, 60)
        self.room_id = room_id
        self.direction = direction
        self.draw_door(True)

    def draw_door(self, state):
        if state == True:
            self.image = self._image
        else:
            self.image = pygame.image.load("./core/assets/комнаты/двери листики закрытые.png")
        self.image = pygame.transform.scale(self.image, self.size)

        if self.direction == "up":
            self.rect = self.image.get_rect(center=(screen_width // 2, (screen_height - room_height) // 2 + 35))
        elif self.direction == "down":
            self.image = pygame.transform.rotate(self.image, 180)
            self.rect = self.image.get_rect(center=(screen_width // 2, (screen_height + room_height) // 2 - 32))
        elif self.direction == "left":
            self.image = pygame.transform.rotate(self.image, 90)
            self.rect = self.image.get_rect(center=((screen_width - room_width) // 2 + 48, screen_height // 2))
        elif self.direction == "right":
            self.image = pygame.transform.rotate(self.image, 270)
            self.rect = self.image.get_rect(center=((screen_width + room_width) // 2 - 45, screen_height // 2))
