import pygame

from src.domain.room.room import Room


class ShopRoom(Room):
    def __init__(self, room_type, room_id):
        super().__init__(room_type, room_id)
        self.artifacts = pygame.sprite.Group()
        self.prices = []
        self.prices_positions = []
        self.shopkeeper_image = pygame.image.load("./core/assets/персонажи/шмелец продавец.png")
        self.shopkeeper_image = pygame.transform.scale(self.shopkeeper_image, (70, 70))
