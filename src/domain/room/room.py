import pygame

from src.managers.base_settings import screen_width, screen_height, room_width, room_height, poison_cooldown
from src.domain.door.door import Door
from src.domain.obstacle.obstacle import Obstacle


class Room:
    def __init__(self, room_type, room_id):
        self.projectiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        self.room_type = room_type
        self.room_id = room_id
        self.rect = pygame.Rect((screen_width - room_width) // 2, (screen_height - room_height) // 2, room_width,
                                room_height)

        self.obstacles = pygame.sprite.Group()
        self.doors_open = True
        self.doors_connections = {}
        self.doors = pygame.sprite.Group()
        self.cleared = False
        self.visited = False
        self.current = False

    def add_bg_image(self, current_area):
        match current_area:
            case 1:
                r = "синяя"
            case 2:
                r = "сиреневая"
            case 3:
                r = "желтая"
            case 4:
                r = "розовая"
            case 5:
                r = "красная"
        self.image = pygame.image.load("./core/assets/комнаты/%s комната.png" % r)
        self.image = pygame.transform.scale(self.image, (room_width, room_height))
        self.rect = self.image.get_rect()

    def add_door(self, direction, connected_room_id):
        door = Door(direction, connected_room_id)
        self.doors_connections[direction] = connected_room_id
        self.doors.add(door)

    def add_obstacle(self, room_rect):
        obstacle = Obstacle(room_rect)
        self.obstacles.add(obstacle)

    def toggle_doors(self, state):
        if state == True:
            self.doors_open = True
        else:
            self.doors_open = False

        for door in self.doors:
            door.draw_door(state)