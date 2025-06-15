import os
import sys
import random

import pygame

from src.components.button import Button
from src.components.multi_state_button import MultiStateButton
from src.domain.artifact.artifact import Artifact
from src.domain.enemy.cockroach import Cockroach
from src.domain.obstacle.obstacle import Obstacle
from src.domain.player.player import Player
from src.domain.projectile.projectile import Projectile
from src.domain.room.boss_room import BossRoom
from src.domain.room.combat_room import CombatRoom
from src.domain.room.room import Room
from src.domain.room.shop_room import ShopRoom
from src.domain.room.treasure_room import TreasureRoom

from enum import Enum
from pygame.math import Vector2

from src.managers.base_settings import screen_width, screen_height, room_width, room_height, fps_limit
from src.managers.save_manager import SavesSystem
from src.managers.game_state_manager import GameStateManager, GameState
from src.managers.settings_manager import SettingsManager

from src.constants.room_type import RoomType

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

save_manager = SavesSystem(".save", "saves")
state_manager = GameStateManager()

# screen_width, screen_height = 1920, 1080
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
pygame.display.set_caption("Пчелиное Приключение")


class Game:
    def __init__(self):
        self.running = True
        self.interaction_cooldown = 10
        self.interaction_ticks = self.interaction_cooldown

        self.player = Player()
        self.buttons = pygame.sprite.Group()

        self.start_room = pygame.sprite.Group()
        self.rooms = {}
        self.map_rooms = []
        self.current_room = None
        self.current_area = 1

        self.add_buttons()

    # ________________________________________________________________________

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
                n += floorplan[i - 10]
            except IndexError:
                pass
            try:
                n += floorplan[i + 10]
            except IndexError:
                pass
            try:
                n += floorplan[i - 1]
            except IndexError:
                pass
            try:
                n += floorplan[i + 1]
            except IndexError:
                pass
            return n

        def visit(i):
            nonlocal floorplanCount
            if floorplan[i]:
                return False
            if ncount(i) > 1:
                return False
            if floorplanCount >= maxrooms:
                return False
            if random.random() < 0.5 and i != 45:
                return False

            cellQueue.append(i)
            floorplan[i] = 1

            if floorplanCount == 0:
                self.start_room = i
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
            if x > 1: created |= visit(i - 1)
            if x < 9: created |= visit(i + 1)
            if i > 20: created |= visit(i - 10)
            if i < 70: created |= visit(i + 10)
            if not created:
                endrooms.append(i)

        if floorplanCount < minrooms:
            return self.generate_dungeon(location_level)

        bossl = endrooms.pop()
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
                # elif i == secretl:
                #     room_type = "secret"
                rooms.append((x, y, room_type))
        return rooms

    def generate_dungeon_objects(self):
        self.rooms = {}
        for (x, y, rtype) in self.map_rooms:
            r = random.randint(1, 9)
            if r <= 7:
                room_type = RoomType.COMBAT
                room = CombatRoom(room_type, (x, y))
                room.add_enemies(self.current_area)
            else:
                room_type = RoomType.NORMAL
                room = Room(room_type, (x, y))

            if rtype == "boss":
                room_type = RoomType.BOSS
                room = BossRoom(room_type, (x, y))
                room.add_boss(self.current_area)
                room.add_exit_door()
            elif rtype == "treasure":
                room_type = RoomType.TREASURE
                room = TreasureRoom(room_type, (x, y))
            elif rtype == "shop":
                room_type = RoomType.SHOP
                room = ShopRoom(room_type, (x, y))
            # elif rtype == "secret":
            #     room_type = RoomType.SECRET
            #     room = SecretRoom(room_type, (x, y))
            elif rtype == "start":
                room_type = RoomType.START
                room = Room(room_type, (x, y))

            self.rooms[(x, y)] = room

        directions = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
        for (x, y), room in self.rooms.items():
            for obstacle in range(random.randint(0, 3 + self.current_area)):
                room.add_obstacle(room.rect)
            for direction, (dx, dy) in directions.items():
                neighbor = (x + dx, y + dy)
                if neighbor in self.rooms:
                    room.add_door(direction, neighbor)

        for (x, y, rtype) in self.map_rooms:
            if rtype == "start":
                self.current_room = self.rooms[(x, y)]
                self.player.rect.center = self.current_room.rect.center
                break

    # ________________________________________________________________________

    def draw_ui(self):
        # fps counter
        font = pygame.font.Font(None, 26)
        text = font.render(str(int(clock.get_fps())), True, (255, 0, 0))
        screen.blit(text, (screen_width - 20, 0))
        self.draw_currency_ui()
        self.draw_health_ui()
        self.draw_artifacts_ui(self.player.current_bag, (0, screen_height - 60))

    def draw_menu(self):
        pass

    def draw_currency_ui(self):
        font = pygame.font.Font(None, 36)
        text = [
            f"Пыльца: {self.player.pollen}",
            f"Мёд: {self.player.honey}",
        ]
        for i, element in enumerate(text):
            surface = font.render(element, True, (255, 255, 255))
            screen.blit(surface, (10, 10 + i * 30))

    def draw_health_ui(self):
        font = pygame.font.Font(None, 26)
        text = font.render(f"Здоровье: {self.player.health}", True, (255, 255, 255))
        screen.blit(text, (screen_width // 2 - room_width // 2, screen_height // 2 + room_height // 2 + 15))
        self.player.health_bar.draw(screen, 0)

        if self.current_room.room_type == RoomType.BOSS:
            bosses_list = list(self.current_room.bosses)
            for boss in bosses_list:
                boss.health_bar.draw(screen, bosses_list.index(boss))
                text = font.render(f"Здоровье: {boss.health}", True, (255, 255, 255))
                screen.blit(text, (screen_width // 2 - room_width // 2, screen_height // 2 - room_height // 2 - 17.5))

    def draw_artifacts_ui(self, bag_number, pos):
        artifacts_to_draw = []

        for artifact in self.player.owned_artifacts[bag_number]:
            artifacts_to_draw.append(artifact.image)

        for image in artifacts_to_draw:
            mod_image = pygame.transform.scale(image, (50, 50))
            screen.blit(mod_image, (pos[0] + artifacts_to_draw.index(image) * 80 + 20, pos[1]), mod_image.get_rect())

    def draw_prices(self, prices, position):
        font = pygame.font.Font(None, 30)
        text = "Артефакты за мёд!"
        surface = font.render(text, True, (255, 255, 255))
        screen.blit(surface, (screen_width // 2 - 100, screen_height // 2 - 150))

        for i in range(0, len(prices)):
            text = [f'{prices[i]}']
            for t, text in enumerate(text):
                surface = font.render(text, True, (255, 255, 255))
                screen.blit(surface, (position[i][0] - 20, screen_height // 2 + 55 + t * 30))

    def draw_minimap(self):
        base_x = screen_width - 305
        base_y = -20

        for (x, y, room_type) in self.map_rooms:

            rs = self.rooms
            r = rs[(x, y)]
            if r.visited == False:
                color = (50, 50, 50)
            else:
                match room_type:
                    case "normal":
                        color = (100, 100, 100)
                    case "boss":
                        color = (205, 0, 0)
                    case "treasure":
                        color = (205, 205, 0)
                    case "shop":
                        color = (205, 105, 0)
                    # case "secret":
                    #     color = (128, 0, 128)
                    case "start":
                        color = (150, 200, 150)
                if r.current == True:
                    color = (color[0] + 50, color[1] + 50, color[2] + 50)
            px = base_x + x * 30
            py = base_y + y * 30

            s = pygame.Surface((28, 28))
            s.set_alpha(128)
            s.fill((color))
            screen.blit(s, (px, py))

    # ________________________________________________________________________

    def handle_room_interaction(self):
        keys = pygame.key.get_pressed()

        self.handle_doors_interaction(keys)

        match self.current_room.room_type:
            case RoomType.COMBAT:
                if self.current_room.cleared == False:
                    for enemy in self.current_room.enemies:
                        self.handle_combat(enemy)
                    self.current_room.enemies.draw(screen)
                    if len(self.current_room.enemies) == 0:
                        self.player.pollen += random.randint(10 * self.current_area, 25 * self.current_area)
                        self.current_room.cleared = True
                        self.current_room.toggle_doors(True)
            case RoomType.TREASURE:
                self.current_room.chests.draw(screen)
                self.current_room.artifacts.draw(screen)
                self.handle_treasure_chest_interaction()
                if keys[pygame.K_e]:
                    for artifact in self.current_room.artifacts:
                        if self.player.rect.colliderect(artifact.rect):
                            self.handle_dropped_artifacts_interaction(artifact)
            case RoomType.SHOP:
                if self.current_room.visited == False:
                    for i in range(-1, 2):
                        position = (screen_width // 2 + 100 * i, screen_height // 2)
                        artl = Artifact.get_random_artifact(Artifact,
                                                            self.player.owned_artifacts[self.player.current_bag],
                                                            self.current_room.artifacts, position)
                        for property, value in artl.properties.items():
                            if property == "price":
                                self.current_room.prices.append(value)
                                self.current_room.prices_positions.append(position)
                        self.current_room.artifacts.add(artl)
                    self.current_room.visited = True
                self.draw_prices(self.current_room.prices, self.current_room.prices_positions)
                screen.blit(self.current_room.shopkeeper_image, (screen_width // 2 - 35, screen_height // 2 - 125))
                self.current_room.artifacts.draw(screen)
                if keys[pygame.K_e]:
                    for artifact in self.current_room.artifacts:
                        for property, value in artifact.properties.items():
                            if property == "price":
                                if value <= self.player.honey:
                                    if self.player.rect.colliderect(artifact.rect):
                                        self.player.honey -= value
                                        self.handle_dropped_artifacts_interaction(artifact)
            case RoomType.BOSS:
                self.current_room.obstacles = pygame.sprite.Group()
                self.current_room.bosses.draw(screen)
                self.current_room.artifacts.draw(screen)
                for boss in self.current_room.bosses:
                    self.handle_combat(boss)
                    if boss.health <= 0:
                        boss.kill()
                        self.player.pollen += boss.pollen
                        self.current_room.artifacts.add(Artifact(boss.artifact, boss.rect.center))
                if len(self.current_room.bosses) == 0:
                    if keys[pygame.K_e]:
                        for artifact in self.current_room.artifacts:
                            if self.player.rect.colliderect(artifact.rect):
                                self.handle_dropped_artifacts_interaction(artifact)
                    self.current_room.cleared = True
                    self.current_room.toggle_doors(True)

        self.handle_projectiles()
        self.current_room.projectiles.update()
        self.current_room.projectiles.draw(screen)

    def handle_treasure_chest_interaction(self):
        for chest in self.current_room.chests:
            if self.player.rect.colliderect(chest.rect) and chest.opened == False:
                chest.opened = True
                chest.image = pygame.image.load("./core/assets/комнаты/сундук открытый.png")
                chest.image = pygame.transform.scale(chest.image, chest.size)
                artl = chest.open_chest(self.player.owned_artifacts[self.player.current_bag],
                                        self.current_room.artifacts, chest.rect.center)
                if type(artl) == Artifact:
                    self.current_room.artifacts.add(artl)

    def handle_dropped_artifacts_interaction(self, artifact):
        if len(self.player.owned_artifacts[self.player.current_bag]) < 5:
            self.player.owned_artifacts[self.player.current_bag].append(artifact)
            self.player.apply_artifact_effects(artifact)
            self.current_room.artifacts.remove(artifact)

    def handle_combat(self, entity):
        new_object = entity.update(self.player.rect.center)
        if type(new_object) == list:
            if len(new_object) > 0 and type(new_object[0]) == Projectile:
                self.current_room.projectiles.add(*new_object)
        elif type(new_object) == Cockroach:
            for i in range(random.randint(1, 1 + self.current_area)):
                self.current_room.enemies.add(Cockroach(new_object.rect, "маленький " + new_object.type))
            entity.kill()

        if entity.rect.colliderect(
                self.player.rect) and entity.attack_ticks == 0 and entity.deal_damage_trigger == True:
            entity.attack_ticks = entity.attack_cooldown
            self.handle_damage(self.player, entity)

        for companion in self.player.companions:
            if entity.rect.colliderect(companion.rect) and companion.attack_ticks == 0:
                companion.attack_ticks = companion.attack_cooldown
                self.handle_damage(entity, companion)
                if companion.poison_damage > 0:
                    entity.taken_poison_damage = companion.poison_damage
                    entity.taken_poison_time = companion.poison_time

        self.handle_obstacles(entity)

    def handle_damage(self, target, source):
        if target.invincibility == True:
            target.invincibility = False
        elif target.invincibility == False:
            target.health -= source.damage
            if source.poison_damage > 0:
                target.taken_poison_damage = source.poison_damage
                target.taken_poison_time = source.poison_time

    def handle_obstacles(self, object):
        for obstacle in self.current_room.obstacles:
            if object.rect.colliderect(obstacle.rect):
                object.taken_slowdown_mult = obstacle.slowdown_mult
                object.taken_slowdown_time = 1

    def handle_projectiles(self):
        for projectile in self.current_room.projectiles:
            hits = []
            if projectile.source == "player":
                if len(self.current_room.enemies) > 0:
                    hits = pygame.sprite.spritecollide(projectile, self.current_room.enemies, False)
                elif self.current_room.room_type == RoomType.BOSS:
                    hits = pygame.sprite.spritecollide(projectile, self.current_room.bosses, False)
            elif projectile.source == "enemy" or projectile.source == "boss":
                hits = [self.player] if self.player.rect.colliderect(projectile.rect) else []

            if len(self.current_room.obstacles) > 0:
                hits += pygame.sprite.spritecollide(projectile, self.current_room.obstacles, False)

            for target in hits:
                if type(target) != Obstacle:
                    self.handle_damage(target, projectile)
                    if projectile.poison_damage > 0:
                        target.taken_poison_damage = projectile.poison_damage
                        target.taken_poison_time = projectile.poison_time
                    if projectile.slowdown_mult > 0:
                        target.taken_slowdown_mult = projectile.slowdown_mult
                        target.taken_slowdown_time = projectile.slowdown_time
                projectile.kill()

    def handle_doors_interaction(self, keys):
        if keys[pygame.K_e]:
            for door in self.current_room.doors:
                if self.player.rect.colliderect(door.rect) and self.current_room.doors_open == True:
                    if door.direction == "exit":
                        self.player.health = self.player.max_health
                        state_manager.change_state(GameState.FOREST)
                        if self.current_area < 5:
                            self.current_area += 1
                            self.add_buttons()
                    else:
                        self.current_room.projectiles = pygame.sprite.Group()
                        self.current_room.visited = True

                        norm_vec = Vector2((door.rect.x - screen_width // 2),
                                           (door.rect.y - screen_height // 2)).normalize()
                        if abs(norm_vec[0]) > abs(norm_vec[1]):
                            self.player.rect.center = (screen_width // 2 - norm_vec[0] * 300, screen_height // 2)
                        else:
                            self.player.rect.center = (screen_width // 2, screen_height // 2 - norm_vec[1] * 180)
                        for ability, state in self.player.abilities.items():
                            match ability:
                                case "1st hit invincibility":
                                    self.player.invincibility = state
                                case "1st shot invisibility":
                                    self.player.invisibility = state
                        if len(self.player.companions) > 0:
                            for companion in self.player.companions:
                                companion.rect.center = (self.player.rect.center[0], self.player.rect.center[1])

                        self.current_room.current = False
                        self.current_room = self.rooms[door.room_id]
                        self.current_room.current = True
                        if (self.current_room.room_type == RoomType.COMBAT or \
                            self.current_room.room_type == RoomType.BOSS) \
                                and self.current_room.cleared == False:
                            self.current_room.toggle_doors(False)

    def handle_player(self, mouse_pos):
        new_projectiles = self.player.update(pygame.key.get_pressed(), mouse_pos)
        for projectile in new_projectiles:
            self.current_room.projectiles.add(projectile)

        self.handle_obstacles(self.player)

        if len(self.player.companions) > 0:
            self.player.companions.draw(screen)
            for companion in self.player.companions:
                match companion.name:
                    case "Муха":
                        new_projectiles = companion.update(self.current_room, self.player.rect.center, mouse_pos)
                        if new_projectiles:
                            self.current_room.projectiles.add(new_projectiles)
                    case "Гусеница" | "Репа":
                        companion.update(self.current_room, self.player.rect.center)

        screen.blit(self.player.image, self.player.rect)

        if self.player.health <= 0:
            state_manager.change_state(GameState.FOREST)

    # ________________________________________________________________________

    def add_buttons(self):
        self.buttons = pygame.sprite.Group()

        match state_manager.current_state():
            case GameState.FOREST:
                self.buttons.add(Button("выход", (125, 125), (screen_width // 16, screen_height - 100)))
                row_x = screen_width // 2 - screen_width // 6.5
                row_y = screen_height // 2 + (screen_height / 150) ** (screen_height / 460)

                for x in range(1, 6):
                    flower_state = "откр"
                    if x > self.current_area:
                        flower_state = "закр"
                    y = 0
                    if x % 2 == 0:
                        y = 200
                    self.buttons.add(MultiStateButton("цветок", f"{flower_state}", f"{x}", (150, 200),
                                                      (row_x + screen_width // 8 * (x - 1), row_y + y)))

                self.buttons.add(Button("улей", (150, 200), (
                    screen_width // 2 - screen_width // 3, 240 + (screen_height / 170) ** (screen_height / 460))))
            case GameState.HIVE:
                self.buttons.add(Button("выход", (125, 125), (screen_width // 16, screen_height - 100)))
                self.buttons.add(Button("мед_получить", (125, 125), (screen_width // 6, screen_height - 100)))

                row_x = screen_width // 1.5
                row_y = screen_height // 7
                print(self.player.current_bag)

                for x in range(1, 6):
                    x_num = x
                    y = row_y
                    bag_state = "неактив"
                    if x - 1 == self.player.current_bag:
                        bag_state = "актив"

                    if x % 2 == 0:
                        row_y += screen_height // 6
                        x -= 1
                        y = row_y + 396 / x
                    self.buttons.add(MultiStateButton("узелок", f"{bag_state}", f"{x_num}",
                                                      (50 * (screen_width // 850), 70 * (screen_height // 520)),
                                                      (row_x + screen_width // 16 * (x - 1), y)))
            case GameState.FLOWER:
                pass
                # self.buttons.add(Button("выход", (90,90), (screen_width//1.03, screen_height-50)))
            case GameState.MAIN_MENU:
                self.buttons.add(Button("выход", (125, 125), (screen_width // 16, screen_height - 100)))
                self.buttons.add(Button("начать", (300, 125), (screen_width // 2, screen_height // 1.3)))
                self.buttons.add(Button("настройки", (75, 85), (screen_width // 1.05, screen_height - 60)))
                self.buttons.add(Button("сохранения", (75, 85), (screen_width // 1.135, screen_height - 60)))
            case GameState.SAVES:
                self.buttons.add(Button("выход", (90, 90), (screen_width // 1.03, screen_height - 50)))
                for button_number in range(-1, 2):
                    x = button_number * 350
                    save_state = save_manager.load_game_data(button_number + 2, ["activated"], ["неактив"])
                    self.buttons.add(MultiStateButton("сохранение", f"{save_state}", f"{button_number + 2}",
                                                      (250 * (screen_width // 850), 275 * (screen_height // 520)),
                                                      (screen_width // 2 + x, screen_height // 1.6)))
                    load_state = "закр"
                    if save_state == "актив":
                        load_state = "откр"
                    self.buttons.add(MultiStateButton("загрузка", f"{load_state}", f"{button_number + 2}",
                                                      (250 * (screen_width // 850), 75 * (screen_height // 520)),
                                                      (screen_width // 2 + x, screen_height // 1.13)))
            case GameState.SETTINGS:
                self.buttons.add(Button("выход", (125, 125), (screen_width // 16, screen_height - 100)))

    def handle_button_hover(self, mouse_pos):
        for button in self.buttons:
            button.highlighted = button.rect.collidepoint(mouse_pos)
            button.update_appearance()
            if button.highlighted:
                match button.button_type:
                    case "узелок":
                        self.draw_artifacts_ui(int(button.button_number[-1:]) - 1,
                                               (button.rect.center[0] - 200, button.rect.center[1] - 100))

    def handle_button_click(self, mouse_pos):
        if self.interaction_ticks > 0:
            self.interaction_ticks -= 1
        elif pygame.mouse.get_pressed()[0] and self.interaction_ticks == 0:
            self.interaction_ticks = self.interaction_cooldown
            for button in self.buttons:
                if button.rect.collidepoint(mouse_pos):
                    match button.button_type:
                        case "цветок":
                            self.current_area = int(button.button_number)
                            self.map_rooms = self.generate_dungeon(self.current_area)
                            self.generate_dungeon_objects()
                            state_manager.change_state(GameState.FLOWER)
                            self.add_buttons()
                        case "улей":
                            state_manager.change_state(GameState.HIVE)
                            self.add_buttons()
                        case "выход":
                            match state_manager.current_state():
                                case GameState.SETTINGS:
                                    state_manager.change_state(GameState.MAIN_MENU)
                                case GameState.SAVES:
                                    state_manager.change_state(GameState.MAIN_MENU)
                                case GameState.MAIN_MENU:
                                    self.running = False
                                case GameState.HIVE:
                                    state_manager.change_state(GameState.FOREST)
                                case GameState.FOREST:
                                    state_manager.change_state(GameState.MAIN_MENU)
                                # case GameState.FLOWER:
                                #     statemanager.change_state(GameState.FOREST)
                            self.add_buttons()
                        case "мед_получить":
                            self.player.honey += int(self.player.pollen // 1.5)
                            self.player.pollen = 0
                        case "начать":
                            state_manager.change_state(GameState.FOREST)
                            self.add_buttons()
                        case "настройки":
                            pass
                            # statemanager.change_state(GameState.SETTINGS)
                            # self.add_buttons()
                        case "сохранения":
                            state_manager.change_state(GameState.SAVES)
                            self.add_buttons()
                        case "узелок":
                            self.player.current_bag = int(button.button_number[-1:]) - 1
                            self.player.set_default_properties()
                            print(self.player.owned_artifacts[self.player.current_bag])
                            for artifact in self.player.owned_artifacts[self.player.current_bag]:
                                self.player.apply_artifact_effects(artifact)
                            self.add_buttons()
                        case "сохранение":
                            save_manager.save_game_data([self.current_area], f"{button.button_number}",
                                                        ["current_area"])
                            for bag_number in range(len(self.player.owned_artifacts)):
                                bag = []
                                for artifact in self.player.owned_artifacts[bag_number]:
                                    bag.append(artifact.type)
                                save_manager.save_game_data([bag], f"{button.button_number}", [f"bag_{bag_number + 1}"])
                                save_manager.save_game_data(["актив"], f"{button.button_number}", ["activated"])
                            self.add_buttons()
                        case "загрузка":
                            for save_button in self.buttons:
                                if save_button.button_type == "сохранение":
                                    if save_button.button_number == button.button_number and save_button.button_state == "актив":
                                        print("LOADING...")
                                        for bag_number in range(len(self.player.owned_artifacts)):
                                            types = save_manager.load_game_data(save_button.button_number,
                                                                                [f"bag_{bag_number + 1}"], [[]])
                                            bag = []
                                            for artifact_type in types:
                                                artifact = Artifact(artifact_type, (0, 0))
                                                bag.append(artifact)
                                            self.player.owned_artifacts[bag_number] = bag
                                        for artifact in self.player.owned_artifacts[self.player.current_bag]:
                                            self.player.apply_artifact_effects(artifact)

                                        self.current_area = save_manager.load_game_data(save_button.button_number,
                                                                                        ["current_area"], [1])

                                        state_manager.change_state(GameState.FOREST)
                                        self.add_buttons()

    def handle_button_interaction(self, mouse_pos):
        self.buttons.draw(screen)
        self.handle_button_hover(mouse_pos)
        self.handle_button_click(mouse_pos)

    def draw_bg_image(self, image):
        bg_image = image
        bg_image = pygame.transform.scale(bg_image, (screen_width, screen_height))
        bg_image_rect = bg_image.get_rect()
        bg_image_rect.center = (screen_width // 2, screen_height // 2)
        screen.blit(bg_image, (0, 0), bg_image_rect)

    def run(self):
        while self.running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            match state_manager.current_state():
                case GameState.MAIN_MENU:
                    bg_image = pygame.image.load("./core/assets/фоны/мэню.png")
                    self.draw_bg_image(bg_image)
                    self.handle_button_interaction(mouse_pos)
                case GameState.SAVES:
                    bg_image = pygame.image.load("./core/assets/фоны/сохранения.png")
                    self.draw_bg_image(bg_image)
                    self.handle_button_interaction(mouse_pos)
                case GameState.HIVE:
                    bg_image = pygame.image.load("./core/assets/фоны/улей фон.png")
                    self.draw_bg_image(bg_image)
                    self.handle_button_interaction(mouse_pos)
                    self.draw_currency_ui()
                case GameState.FOREST:
                    bg_image = pygame.image.load("./core/assets/фоны/фон меню областей.png")
                    self.draw_bg_image(bg_image)
                    self.handle_button_interaction(mouse_pos)
                case GameState.FLOWER:
                    # self.handle_button_interaction(mouse_pos)
                    self.current_room.visited = True
                    self.current_room.current = True
                    screen.fill((30, 30, 30))
                    self.current_room.add_bg_image(self.current_area)
                    screen.blit(self.current_room.image,
                                ((screen_width - room_width) // 2, (screen_height - room_height) // 2),
                                self.current_room.rect)
                    self.current_room.doors.draw(screen)
                    if len(self.current_room.obstacles) > 0:
                        self.current_room.obstacles.draw(screen)
                    self.draw_minimap()
                    self.draw_ui()
                    self.handle_room_interaction()
                    self.handle_player(mouse_pos)

            pygame.display.flip()
            clock.tick(fps_limit)

        pygame.quit()
        sys.exit()
