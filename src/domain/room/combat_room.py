from src.domain.enemy.butterfly import Butterfly
from src.domain.enemy.cockroach import Cockroach
from src.domain.enemy.firefly import Firefly
from src.domain.enemy.work import Worm
from src.domain.room.room import Room

import random


class CombatRoom(Room):
    def __init__(self, room_type, room_id):
        super().__init__(room_type, room_id)

    def add_enemies(self, current_area):
        for _ in range(1 + random.randint(0, current_area)):
            mult = random.randint(1, current_area)
            match pow(random.randint(2, 3), mult):
                # area1
                case 2:
                    self.enemies.add(Cockroach(self.rect, "обычный"))
                case 3:
                    self.enemies.add(Worm(self.rect, "обычный"))
                # area2
                case 4:
                    self.enemies.add(Butterfly(self.rect, "обычный"))
                case 9:
                    self.enemies.add(Worm(self.rect, "усиленный"))
                # area3
                case 8:
                    self.enemies.add(Firefly(self.rect, "обычный"))
                case 27:
                    self.enemies.add(Cockroach(self.rect, "усиленный"))
                # area4
                case 16:
                    self.enemies.add(Cockroach(self.rect, "обычный"))  # PLACEHOLDER #красный муравей
                case 81:
                    self.enemies.add(Butterfly(self.rect, "усиленный"))
                # area5
                case 32:
                    self.enemies.add(Firefly(self.rect, "усиленный"))
                case 243:
                    self.enemies.add(Worm(self.rect, "усиленный"))  # PLACEHOLDER #усиленный красный муравей
