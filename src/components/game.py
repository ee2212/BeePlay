import os
import sys
import random

import pygame

from src.components.buttons.button import Button
from src.components.buttons.multi_state_button import MultiStateButton
from src.domain.artifact.artifact import Artifact
from src.domain.enemy.cockroach import Cockroach
from src.domain.obstacle.obstacle import Obstacle
from src.domain.player.player import Player
from src.domain.projectile.projectile import Projectile


from pygame.math import Vector2

from src.managers.base_settings import screen_width, screen_height, room_width, room_height, fps_limit
from src.managers.save_manager import SavesSystem
from src.managers.game_state_manager import GameStateManager, GameState
from src.managers.generation_manager import GenerateManager
from src.managers.draw_manager import DrawManager

from src.constants.room_type import RoomType

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

save_manager = SavesSystem(".save", "saves")
state_manager = GameStateManager()
generate_manager = GenerateManager()
draw_manager = DrawManager()
# screen_width, screen_height = 1920, 1080
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
pygame.display.set_caption("BeePlay")


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

    def handle_room_interaction(self): # doors processing
        keys = pygame.key.get_pressed()

        self.handle_doors_interaction(keys)

        match self.current_room.room_type:

            case RoomType.COMBAT:
                if self.current_room.cleared == False: 
                    for enemy in self.current_room.enemies:
                        self.handle_combat(enemy)
                    self.current_room.enemies.draw(screen)
                    if len(self.current_room.enemies) == 0:
                        self.player.pollen += random.randint(
                            10 * self.current_area, 25 * self.current_area)
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
                        position = (screen_width // 2 + 100 *
                                    i, screen_height // 2)
                        artl = Artifact.get_random_artifact(Artifact,
                                                            self.player.owned_artifacts[self.player.current_bag],
                                                            self.current_room.artifacts, position) 
                        for property, value in artl.properties.items():
                            if property == "price":
                                self.current_room.prices.append(value)
                                self.current_room.prices_positions.append(
                                    position)
                        self.current_room.artifacts.add(artl)
                    self.current_room.visited = True
                self.draw_prices(self.current_room.prices,
                                 self.current_room.prices_positions, screen, screen_width, screen_height)
                screen.blit(self.current_room.shopkeeper_image,
                            (screen_width // 2 - 35, screen_height // 2 - 125))
                self.current_room.artifacts.draw(screen)
                if keys[pygame.K_e]:  # buying 
                    for artifact in self.current_room.artifacts:
                        for property, value in artifact.properties.items():
                            if property == "price":
                                if value <= self.player.honey:
                                    if self.player.rect.colliderect(artifact.rect):
                                        self.player.honey -= value
                                        self.handle_dropped_artifacts_interaction(
                                            artifact)
                                        
            case RoomType.BOSS:
                self.current_room.obstacles = pygame.sprite.Group()
                self.current_room.bosses.draw(screen)
                self.current_room.artifacts.draw(screen)
                for boss in self.current_room.bosses:
                    self.handle_combat(boss) 
                    if boss.health <= 0: # drop artifact after winning
                        boss.kill()
                        self.player.pollen += boss.pollen
                        self.current_room.artifacts.add(
                            Artifact(boss.artifact, boss.rect.center))
                if len(self.current_room.bosses) == 0: # getting attifact
                    if keys[pygame.K_e]:
                        for artifact in self.current_room.artifacts:
                            if self.player.rect.colliderect(artifact.rect):
                                self.handle_dropped_artifacts_interaction(
                                    artifact)
                    self.current_room.cleared = True
                    self.current_room.toggle_doors(True)

        self.handle_projectiles() # projectiles pprocessing
        self.current_room.projectiles.update()
        self.current_room.projectiles.draw(screen)

    def handle_treasure_chest_interaction(self): # openning chests 
        for chest in self.current_room.chests:
            if self.player.rect.colliderect(chest.rect) and chest.opened == False:
                chest.opened = True
                chest.image = pygame.image.load(
                    "./core/assets/комнаты/сундук открытый.png")
                chest.image = pygame.transform.scale(chest.image, chest.size)
                artl = chest.open_chest(self.player.owned_artifacts[self.player.current_bag],
                                        self.current_room.artifacts, chest.rect.center)
                if type(artl) == Artifact: # generating free artefact
                    self.current_room.artifacts.add(artl)

    def handle_dropped_artifacts_interaction(self, artifact):
        if len(self.player.owned_artifacts[self.player.current_bag]) < 5:
            self.player.owned_artifacts[self.player.current_bag].append( # adding artifact
                artifact)
            self.player.apply_artifact_effects(artifact) # applying effects
            self.current_room.artifacts.remove(artifact) # deleting artifact

    def handle_combat(self, entity):
        new_object = entity.update(self.player.rect.center) # updating condition
        if type(new_object) == list:
            if len(new_object) > 0 and type(new_object[0]) == Projectile:
                self.current_room.projectiles.add(*new_object) # adding projectiles to the room list
        elif type(new_object) == Cockroach: # processing cockroach division
            for i in range(random.randint(1, 1 + self.current_area)): # random quantity 
                self.current_room.enemies.add(
                    Cockroach(new_object.rect, "маленький " + new_object.type))
            entity.kill()

        if entity.rect.colliderect( # processing collision with enemy
                self.player.rect) and entity.attack_ticks == 0 and entity.deal_damage_trigger == True:
            entity.attack_ticks = entity.attack_cooldown
            self.handle_damage(self.player, entity)

        for companion in self.player.companions: # damaging from companion
            if entity.rect.colliderect(companion.rect) and companion.attack_ticks == 0:
                companion.attack_ticks = companion.attack_cooldown
                self.handle_damage(entity, companion)
                if companion.poison_damage > 0: 
                    entity.taken_poison_damage = companion.poison_damage
                    entity.taken_poison_time = companion.poison_time

        self.handle_obstacles(entity)

    def handle_damage(self, target, source): # recieving damage
        if target.invincibility == True:
            target.invincibility = False # first damage make ininvisible
        elif target.invincibility == False:
            target.health -= source.damage
            if source.poison_damage > 0: # poisoning
                target.taken_poison_damage = source.poison_damage
                target.taken_poison_time = source.poison_time

    def handle_obstacles(self, object):
        for obstacle in self.current_room.obstacles:
            if object.rect.colliderect(obstacle.rect): # collision with obstacle
                object.taken_slowdown_mult = obstacle.slowdown_mult # slowing down
                object.taken_slowdown_time = 1

    def handle_projectiles(self):
        for projectile in self.current_room.projectiles:
            hits = [] # list of objects hit by a projectile

            if projectile.source == "player":

                if len(self.current_room.enemies) > 0: # collision with enemy
                    hits = pygame.sprite.spritecollide(
                        projectile, self.current_room.enemies, False)
                    
                elif self.current_room.room_type == RoomType.BOSS: # collision with boss
                    hits = pygame.sprite.spritecollide(
                        projectile, self.current_room.bosses, False)
                    

            elif projectile.source == "enemy" or projectile.source == "boss": # collision with player
                hits = [self.player] if self.player.rect.colliderect(
                    projectile.rect) else []

            if len(self.current_room.obstacles) > 0: # collision with obstacles
                hits += pygame.sprite.spritecollide(
                    projectile, self.current_room.obstacles, False)

            for target in hits:
                if type(target) != Obstacle:
                    self.handle_damage(target, projectile)
                    if projectile.poison_damage > 0:
                        target.taken_poison_damage = projectile.poison_damage # taking damage
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
                        self.add_buttons()
                        
                        if self.current_area < 5:
                            self.current_area += 1
                            

                    else:
                        self.current_room.projectiles = pygame.sprite.Group() # clear projectiles
                        self.current_room.visited = True

                        norm_vec = Vector2((door.rect.x - screen_width // 2),
                                           (door.rect.y - screen_height // 2)).normalize()
                        if abs(norm_vec[0]) > abs(norm_vec[1]): # horizontal displacement
                            self.player.rect.center = (
                                screen_width // 2 - norm_vec[0] * 300, screen_height // 2)
                        else: # vertical displacement
                            self.player.rect.center = (
                                screen_width // 2, screen_height // 2 - norm_vec[1] * 180)
                            
                        for ability, state in self.player.abilities.items():
                            match ability:
                                case "1st hit invincibility":
                                    self.player.invincibility = state
                                case "1st shot invisibility":
                                    self.player.invisibility = state

                        if len(self.player.companions) > 0: # moving the companions to the player
                            for companion in self.player.companions:
                                companion.rect.center = (
                                    self.player.rect.center[0], self.player.rect.center[1])
                                
                        
                                
                        self.current_room.current = False
                        self.current_room = self.rooms[door.room_id]
                        self.current_room.current = True
                        if (self.current_room.room_type == RoomType.COMBAT or
                            self.current_room.room_type == RoomType.BOSS) \
                                and self.current_room.cleared == False:
                            self.current_room.toggle_doors(False) # closing doors

    def handle_player(self, mouse_pos):
        new_projectiles = self.player.update(
            pygame.key.get_pressed(), mouse_pos)
        for projectile in new_projectiles: # adding new projectiles
            self.current_room.projectiles.add(projectile)

        self.handle_obstacles(self.player) # collision with obstacles

        if len(self.player.companions) > 0: # processing companions
            self.player.companions.draw(screen)
            for companion in self.player.companions:
                match companion.name:
                    case "Муха":
                        new_projectiles = companion.update(
                            self.current_room, self.player.rect.center, mouse_pos)
                        if new_projectiles: # if fly shoot
                            self.current_room.projectiles.add(new_projectiles)
                    case "Гусеница" | "Репа":
                        companion.update(self.current_room,
                                         self.player.rect.center)

        screen.blit(self.player.image, self.player.rect) # drawing player

        if self.player.health <= 0: # checking death
            self.player.health = self.player.max_health
            state_manager.change_state(GameState.FOREST)
            self.add_buttons()

    # ________________________________________________________________________

    def add_buttons(self):
        self.buttons = pygame.sprite.Group()

        match state_manager.current_state():
            case GameState.FOREST: # adding button exit in the bottom left
                self.buttons.add(Button("выход", (125, 125),
                                 (screen_width // 16, screen_height - 100)))
                
                row_x = screen_width // 2 - screen_width // 6.5
                row_y = screen_height // 2 + \
                    (screen_height / 150) ** (screen_height / 460)

                for x in range(1, 6): # making 5 flowers in the chess order
                    flower_state = "откр" # default flower-area is open
                    if x > self.current_area:
                        flower_state = "закр"
                    y = 0 # chess order
                    if x % 2 == 0:
                        y = 200
                    self.buttons.add(MultiStateButton("цветок", f"{flower_state}", f"{x}", (150, 200),
                                                      (row_x + screen_width // 8 * (x - 1), row_y + y)))

                self.buttons.add(Button("улей", (150, 200), ( # making hive button
                    screen_width // 2 - screen_width // 3, 240 + (screen_height / 170) ** (screen_height / 460))))
                

            case GameState.HIVE:
                self.buttons.add(Button("выход", (125, 125),
                                 (screen_width // 16, screen_height - 100)))
                self.buttons.add(
                    Button("мед_получить", (125, 125), (screen_width // 6, screen_height - 100)))

                row_x = screen_width // 1.5
                row_y = screen_height // 7
                print(self.player.current_bag)

                for x in range(1, 6):
                    x_num = x
                    y = row_y
                    bag_state = "неактив"
                    if x - 1 == self.player.current_bag: # highliting current bag
                        bag_state = "актив"

                    if x % 2 == 0:
                        row_y += screen_height // 6
                        x -= 1
                        y = row_y + 396 / x
                    self.buttons.add(MultiStateButton("узелок", f"{bag_state}", f"{x_num}", # adaptive for screen ladder order
                                                      (50 * (screen_width // 850),
                                                       70 * (screen_height // 520)),
                                                      (row_x + screen_width // 16 * (x - 1), y)))
            case GameState.FLOWER:
                pass
                # self.buttons.add(Button("выход", (90,90), (screen_width//1.03, screen_height-50)))

            case GameState.MAIN_MENU:
                self.buttons.add(Button("выход", (125, 125),
                                 (screen_width // 16, screen_height - 100)))
                self.buttons.add(Button("начать", (300, 125),
                                 (screen_width // 2, screen_height // 1.3)))
                self.buttons.add(Button("сохранения", (75, 85),
                                 (screen_width // 1.05, screen_height - 60)))
                
            case GameState.SAVES:
                self.buttons.add(
                    Button("выход", (90, 90), (screen_width // 1.03, screen_height - 50)))
                for button_number in range(-1, 2): # 3 saves
                    x = button_number * 350
                    save_state = save_manager.load_game_data(
                        button_number + 2, ["activated"], ["неактив"])
                    self.buttons.add(MultiStateButton("сохранение", f"{save_state}", f"{button_number + 2}",
                                                      (250 * (screen_width // 850),
                                                       275 * (screen_height // 520)),
                                                      (screen_width // 2 + x, screen_height // 1.6)))
                    load_state = "закр"
                    if save_state == "актив": # if is save make button load
                        load_state = "откр"
                    self.buttons.add(MultiStateButton("загрузка", f"{load_state}", f"{button_number + 2}",
                                                      (250 * (screen_width // 850),
                                                       75 * (screen_height // 520)),
                                                      (screen_width // 2 + x, screen_height // 1.13)))
                    

    def handle_button_hover(self, mouse_pos): 
        for button in self.buttons:
            button.highlighted = button.rect.collidepoint(mouse_pos)  # checking cursor position
            button.update_appearance() # making button highlighted
            if button.highlighted:
                match button.button_type:
                    case "узелок":
                        draw_manager.draw_artifacts_ui(int(button.button_number[-1:]) - 1, # drawind artifacts in highlighted bag
                                               (button.rect.center[0] - 200, button.rect.center[1] - 100), self.player, screen)

    def handle_button_click(self, mouse_pos):  # clicking buttons
        if self.interaction_ticks > 0:  # protection against frequent clicks
            self.interaction_ticks -= 1
        elif pygame.mouse.get_pressed()[0] and self.interaction_ticks == 0:
            self.interaction_ticks = self.interaction_cooldown
            for button in self.buttons:
                if button.rect.collidepoint(mouse_pos):  # checking click
                    match button.button_type:
                        case "цветок":
                            self.map_rooms = generate_manager.generate_dungeon(self.current_area)
                            self.rooms = generate_manager.generate_dungeon_objects(self.current_area, self.map_rooms)
                            for (x, y, rtype) in self.map_rooms: # setting start room
                                if rtype == "start":
                                    self.current_room = self.rooms[(x, y)] 
                                    self.player.rect.center = self.current_room.rect.center
                            state_manager.change_state(GameState.FLOWER)
                            self.add_buttons()
                        case "улей":
                            state_manager.change_state(GameState.HIVE)
                            self.add_buttons()
                        case "выход":
                            match state_manager.current_state():
                                case GameState.SETTINGS:
                                    state_manager.change_state(
                                        GameState.MAIN_MENU)

                                case GameState.SAVES:
                                    state_manager.change_state(
                                        GameState.MAIN_MENU)

                                case GameState.MAIN_MENU:
                                    self.running = False  # closing game

                                case GameState.HIVE:
                                    state_manager.change_state(
                                        GameState.FOREST)

                                case GameState.FOREST:
                                    state_manager.change_state(
                                        GameState.MAIN_MENU)
                                # case GameState.FLOWER:
                                #     statemanager.change_state(GameState.FOREST)
                            self.add_buttons()

                        case "мед_получить":
                            self.player.honey += int(self.player.pollen // 1.5)
                            self.player.pollen = 0

                        case "начать":
                            state_manager.change_state(GameState.FOREST)
                            self.add_buttons()

                        case "сохранения":
                            state_manager.change_state(GameState.SAVES)
                            self.add_buttons()

                        case "узелок":
                            self.player.current_bag = int(
                                button.button_number[-1:]) - 1  # choosing bag
                            self.player.set_default_properties()
                            print(
                                self.player.owned_artifacts[self.player.current_bag])

                            # applying artefact effects
                            for artifact in self.player.owned_artifacts[self.player.current_bag]:
                                self.player.apply_artifact_effects(artifact)
                            self.add_buttons()

                        case "сохранение":
                            save_manager.save_game_data([self.current_area], f"{button.button_number}", # saving area
                                                        ["current_area"])
                            for bag_number in range(len(self.player.owned_artifacts)): # saving bags
                                bag = []
                                for artifact in self.player.owned_artifacts[bag_number]:
                                    bag.append(artifact.type) # savig artifact type to the bag
                                save_manager.save_game_data([bag], f"{button.button_number}", [
                                                            f"bag_{bag_number + 1}"])
                                save_manager.save_game_data(
                                    ["актив"], f"{button.button_number}", ["activated"]) # activated condition
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
                                            for artifact_type in types: # making artifact from saving
                                                artifact = Artifact(
                                                    artifact_type, (0, 0))
                                                bag.append(artifact)
                                            self.player.owned_artifacts[bag_number] = bag 

                                        for artifact in self.player.owned_artifacts[self.player.current_bag]: # applying artifact effects
                                            self.player.apply_artifact_effects(
                                                artifact)

                                        self.current_area = save_manager.load_game_data(save_button.button_number, # loading area
                                                                                        ["current_area"], [1])

                                        state_manager.change_state( #loading location
                                            GameState.FOREST) 
                                        self.add_buttons()

    def handle_button_interaction(self, mouse_pos):  # drawing buttons
        self.buttons.draw(screen)
        self.handle_button_hover(mouse_pos)
        self.handle_button_click(mouse_pos)

    def draw_bg_image(self, image):  # drawing game
        bg_image = image
        bg_image = pygame.transform.scale(
            bg_image, (screen_width, screen_height))
        bg_image_rect = bg_image.get_rect()
        bg_image_rect.center = (screen_width // 2, screen_height // 2)
        screen.blit(bg_image, (0, 0), bg_image_rect)

    def run(self):  # running game
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
                    bg_image = pygame.image.load(
                        "./core/assets/фоны/сохранения.png")
                    self.draw_bg_image(bg_image)
                    self.handle_button_interaction(mouse_pos)
                case GameState.HIVE:
                    bg_image = pygame.image.load(
                        "./core/assets/фоны/улей фон.png")
                    self.draw_bg_image(bg_image)
                    self.handle_button_interaction(mouse_pos)
                    draw_manager.draw_currency_ui(screen, self.player)
                case GameState.FOREST:
                    bg_image = pygame.image.load(
                        "./core/assets/фоны/фон меню областей.png")
                    self.draw_bg_image(bg_image)
                    self.handle_button_interaction(mouse_pos)
                case GameState.FLOWER:
                    self.current_room.visited = True
                    self.current_room.current = True
                    screen.fill((30, 30, 30))
                    self.current_room.add_bg_image(self.current_area)
                    screen.blit(self.current_room.image,
                                ((screen_width - room_width) // 2,
                                 (screen_height - room_height) // 2),
                                self.current_room.rect)
                    self.current_room.doors.draw(screen)
                    if len(self.current_room.obstacles) > 0:
                        self.current_room.obstacles.draw(screen)
                    draw_manager.draw_minimap(self.map_rooms, self.rooms, screen)
                    draw_manager.draw_ui(screen, self.current_room, self.player, clock, self.player.current_bag)
                    self.handle_room_interaction()
                    self.handle_player(mouse_pos)

            pygame.display.flip()
            clock.tick(fps_limit)

        pygame.quit()
        sys.exit()
