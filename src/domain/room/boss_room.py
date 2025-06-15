import pygame

from src.domain.boss.frog import Frog
from src.domain.boss.rat import Rat
from src.domain.boss.sparrow import Sparrow
from src.domain.boss.spider import Spider
from src.domain.boss.wasp import Wasp
from src.domain.door.exit_door import ExitDoor
from src.domain.room.room import Room


class BossRoom(Room):
    def __init__(self, room_type, room_id):
        super().__init__(room_type, room_id)
        self.bosses = pygame.sprite.Group()
        self.chests = pygame.sprite.Group()
        self.artifacts = pygame.sprite.Group()

    def add_boss(self, current_area):
        match current_area:
            case 1:
                self.bosses.add(Frog(self.rect))
            case 2:
                self.bosses.add(Rat(self.rect))
            case 3:
                self.bosses.add(Sparrow(self.rect))
            case 4:
                self.bosses.add(Spider(self.rect))
            case 5:
                self.bosses.add(Wasp(self.rect))

    def add_exit_door(self):
        door = ExitDoor()
        self.doors.add(door)