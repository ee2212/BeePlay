import pygame

from src.managers.base_settings import screen_width, screen_height, room_width, room_height, poison_cooldown
from src.domain.chest.chest import Chest
from src.domain.room.room import Room


class TreasureRoom(Room):
    def __init__(self, room_type, room_id):
        super().__init__(room_type, room_id)
        self.chests = pygame.sprite.Group()
        self.artifacts = pygame.sprite.Group()

        self.chests.add(Chest((screen_width // 2, screen_height // 2)))

        # testing
        # for i in range(5):
        #     self.chests.add(Chest((screen_width // 2 - 300 + i*100, screen_height // 2)))
        # for i in range(5):
        #     self.chests.add(Chest((screen_width // 2 - 300 + i*100, screen_height // 2 + 100)))
