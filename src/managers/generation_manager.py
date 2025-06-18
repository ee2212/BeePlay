import pygame
import random

from src.domain.room.boss_room import BossRoom
from src.domain.room.combat_room import CombatRoom
from src.domain.room.room import Room
from src.domain.room.shop_room import ShopRoom
from src.domain.room.treasure_room import TreasureRoom

from src.constants.room_type import RoomType


class GenerateManager:   

    def generate_dungeon(self, location_level):
        floorplan = [0] * (101 + 10 * location_level)
        maxrooms = 7 + location_level * 2
        minrooms = 5 + location_level
        cellQueue = []
        endrooms = []
        floorplanCount = 0

        def ncount(i):
            n = 0
            try:
                n += floorplan[i - 10]  # checking bottom neighbour
            except IndexError:
                pass
            try:
                n += floorplan[i + 10]  # checking up neighbour
            except IndexError:
                pass
            try:
                n += floorplan[i - 1]  # checking left neighbour
            except IndexError:
                pass
            try:
                n += floorplan[i + 1]  # checking right neighbour
            except IndexError:
                pass
            return n # number of neighbours

        def visit(i):
            nonlocal floorplanCount
            if floorplan[i]: # excisting
                return False
            if ncount(i) > 1: # more than 1 neighbour
                return False
            if floorplanCount >= maxrooms:
                return False
            if random.random() < 0.5 and i != 45: # chance 50% to skip
                return False

            cellQueue.append(i) 
            floorplan[i] = 1 # mark as excisting room

            if floorplanCount == 0:
                self.start_room = i # mark as starting
            floorplanCount += 1
            return True

        def poprandomendroom():
            if not endrooms:
                return 10
            if len(endrooms) == 1:
                return endrooms.pop(0)
            index = random.randint(0, len(endrooms) - 1)
            return endrooms.pop(index)

        visit(45)

        while cellQueue:
            i = cellQueue.pop(0)
            x = i % 10
            created = False
            if x > 1:
                created |= visit(i - 1) # left
            if x < 9:
                created |= visit(i + 1) # right
            if i > 20:
                created |= visit(i - 10) # bottom
            if i < 70:
                created |= visit(i + 10) # up
            if not created:
                endrooms.append(i)

        if floorplanCount < minrooms:
            return self.generate_dungeon(location_level)

        bossl = endrooms.pop() # furthest from starting
        treasurel = poprandomendroom()
        shopl = poprandomendroom()
        start1 = self.start_room

        rooms = []
        for i, val in enumerate(floorplan):
            if val:
                x = i % 10
                y = (i - x) // 10
                room_type = "normal"
                if i == start1:
                    room_type = "start"
                    self.start_room = (x, y, room_type)
                if i == bossl:
                    room_type = "boss"
                elif i == treasurel:
                    room_type = "treasure"
                elif i == shopl:
                    room_type = "shop"
                rooms.append((x, y, room_type))
        return rooms

    def generate_dungeon_objects(self, current_area, map_rooms):
        self.rooms = {}
        for (x, y, rtype) in map_rooms:
            r = random.randint(1, 9)
            if r <= 7: # 70% chance for combat room
                room_type = RoomType.COMBAT
                room = CombatRoom(room_type, (x, y))
                room.add_enemies(current_area)
            else:
                room_type = RoomType.NORMAL
                room = Room(room_type, (x, y))

            if rtype == "boss":
                room_type = RoomType.BOSS
                room = BossRoom(room_type, (x, y))
                room.add_boss(current_area)
                room.add_exit_door()
            elif rtype == "treasure":
                room_type = RoomType.TREASURE
                room = TreasureRoom(room_type, (x, y))
            elif rtype == "shop":
                room_type = RoomType.SHOP
                room = ShopRoom(room_type, (x, y))
            elif rtype == "start":
                room_type = RoomType.START
                room = Room(room_type, (x, y))

            self.rooms[(x, y)] = room # save room

        directions = {"up": (0, -1), "down": (0, 1),
                      "left": (-1, 0), "right": (1, 0)}
        
        for (x, y), room in self.rooms.items():
            for obstacle in range(random.randint(0, 3 + current_area)):
                room.add_obstacle(room.rect)

            for direction, (dx, dy) in directions.items(): # adding doors if neighbour excists
                neighbor = (x + dx, y + dy)
                if neighbor in self.rooms:
                    room.add_door(direction, neighbor)
        return self.rooms
    