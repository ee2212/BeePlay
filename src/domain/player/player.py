import pygame
from pygame import Vector2

from src.components.health_bar import HealthBar
from src.constants.artifact_type import ArtifactType
from src.domain.companion.caterpillar import Caterpillar
from src.domain.companion.fly import Fly
from src.domain.companion.turnip import Turnip
from src.domain.projectile.projectile import Projectile
from src.managers.base_settings import screen_width, screen_height, poison_cooldown, room_width, room_height


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("./core/assets/персонажи/ГЛАВНАЯ ПЧОЛА.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height // 2))
        self.pollen = 0
        self.honey = 500

        self.set_default_properties()

        self.invincibility = False
        self.invisibility = False
        self.attack_trigger = False
        self.projectile_counter = 0
        self.deal_damage_trigger = True
        self.taken_slowdown_mult = 0
        self.taken_slowdown_time = 0
        self.taken_poison_damage = 0
        self.taken_poison_time = 0
        self.taken_poison_ticks = poison_cooldown

        self.current_bag = 0
        self.owned_artifacts = [[] for _ in range(5)]

    def set_default_properties(self):
        self.dash_cooldown = 80
        self.dash_ticks = 0
        self.dash_distance = 130
        self._move_speed = 7
        self.move_speed = self._move_speed
        self.abilities = {
            "Dash": False,
            "1st hit invincibility": False,
            "1st shot invisibility": False}
        self.health = 150
        self.max_health = 150
        self.health_bar = HealthBar(screen_width // 2 - room_width // 2, screen_height // 2 + room_height // 2,
                                    room_width, screen_height // 70, \
                                    self.max_health, pygame.Color(123, 255, 77), pygame.Color(79, 79, 79))
        self._attack_cooldown = 40
        self.attack_cooldown = self._attack_cooldown
        self.attack_ticks = self.attack_cooldown
        self.companions = pygame.sprite.Group()
        self.poison_damage = 0
        self.poison_time = 0
        self.projectiles_quantity = 1
        self.projectile_properties = {
            "projectile_damage": 10,
            "projectile_speed": 10,
            "projectile_poison_damage": self.poison_damage,
            "projectile_poison_time": self.poison_time,
            "projectile_texture": pygame.image.load("./core/assets/проджектайлы/слеза по базе.png"),
            "projectile_size": (20, 20),
            "projectile_slowdown_mult": 0,
            "projectile_slowdown_time": 0}

    def apply_artifact_effects(self, artifact):
        for property, value in artifact.properties.items():
            match property:
                case "poison_damage":
                    self.poison_damage = value
                    self.projectile_properties["projectile_" + property] = value
                case "poison_time":
                    self.poison_time = value
                    self.projectile_properties["projectile_" + property] = value
                case "max_hp":
                    self.health = int((self.max_health + value) * (self.health / self.max_health))
                    self.max_health = self.max_health + value
                    self.health_bar = HealthBar(screen_width // 2 - room_width // 2,
                                                screen_height // 2 + room_height // 2, room_width, screen_height // 70, \
                                                self.max_health, pygame.Color(123, 255, 77), pygame.Color(79, 79, 79))
                case "attack_speed_mult":
                    self.attack_cooldown = self._attack_cooldown // value
                    self.attack_ticks = self.attack_cooldown
                case "move_speed":
                    self._move_speed = self.move_speed + value
                    self.move_speed = self._move_speed
                case "projectiles_quantity":
                    self.projectiles_quantity = self.projectiles_quantity + value
                    if self.projectiles_quantity <= 0:
                        self.projectiles_quantity = 1
                case "projectile_damage" | "projectile_speed" | "projectile_slowdown_mult" | "projectile_slowdown_time":
                    self.projectile_properties[property] = self.projectile_properties[property] + value
                case "companion":
                    match artifact.type:
                        case ArtifactType.CATERPILLAR:
                            self.companions.add(Caterpillar(self.rect.center, value, artifact.type.value))
                        case ArtifactType.FLY:
                            self.companions.add(Fly(self.rect.center, value, artifact.type.value))
                        case ArtifactType.TURNIP:
                            self.companions.add(Turnip(self.rect.center, value, artifact.type.value))
                case "projectile_texture" | "projectile_size":
                    self.projectile_properties[property] = value
                case "ability_name":
                    self.abilities[value] = True
            print("После", self.companions, f" {artifact.type}")

    def update(self, keys, mouse_pos):
        self.health_bar.hp = self.health

        if self.taken_poison_time > 0:
            self.taken_poison_time -= 1
            self.inflict_poison_damage()

        self.handle_movement(keys)

        if self.attack_ticks > 0:
            self.attack_ticks -= 1

        bullets = self.handle_shooting(mouse_pos)
        return bullets

    def handle_movement(self, keys):
        if self.taken_slowdown_time > 0:
            self.taken_slowdown_time -= 1
            self.move_speed = self._move_speed / self.taken_slowdown_mult
        elif self.taken_slowdown_time == 0:
            self.taken_slowdown_time = -1
            self.move_speed = self._move_speed

        wall_correct = 50
        self.rect.clamp_ip(pygame.Rect((screen_width - room_width) // 2 + wall_correct * 1.2, \
                                       (screen_height - room_height) // 2 + wall_correct,
                                       room_width - wall_correct * 2.2, room_height - wall_correct * 2))

        if keys[pygame.K_w]: self.rect.y -= self.move_speed
        if keys[pygame.K_s]: self.rect.y += self.move_speed
        if keys[pygame.K_a]: self.rect.x -= self.move_speed
        if keys[pygame.K_d]: self.rect.x += self.move_speed

        if self.abilities["Dash"] == True:
            self.handle_dash(keys)

    def handle_shooting(self, mouse_pos):
        bullets = []
        if pygame.mouse.get_pressed()[0] and self.attack_ticks <= 0 and not self.attack_trigger:
            self.attack_trigger = True
            self.attack_ticks = self.attack_cooldown
            self.projectile_counter = 0
        if self.attack_trigger:
            if self.attack_ticks \
                    == int(self.attack_cooldown / self.projectiles_quantity * (
                    self.projectiles_quantity - self.projectile_counter)):
                direction = Vector2(mouse_pos) - Vector2(self.rect.center)
                if direction.length() > 0:
                    self.projectile_counter += 1
                    bullet = Projectile("player", self.rect.center, direction, self.projectile_properties)
                    bullets.append(bullet)
            if self.projectile_counter + 1 > self.projectiles_quantity:
                self.attack_trigger = False
        return bullets

    def handle_dash(self, keys):
        if self.dash_ticks > 0:
            self.dash_ticks -= 1
        elif self.dash_ticks == 0 and keys[pygame.K_LSHIFT]:
            self.dash_ticks = self.dash_cooldown
            if keys[pygame.K_w]: self.rect.y -= self.dash_distance
            if keys[pygame.K_s]: self.rect.y += self.dash_distance
            if keys[pygame.K_a]: self.rect.x -= self.dash_distance
            if keys[pygame.K_d]: self.rect.x += self.dash_distance

    def inflict_poison_damage(self):
        if self.taken_poison_ticks > 0:
            self.taken_poison_ticks -= 1
        else:
            self.taken_poison_ticks = poison_cooldown
            self.health -= self.taken_poison_damage
