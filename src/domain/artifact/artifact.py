import random

import pygame

from src.constants.artifact_type import ArtifactType


class Artifact(pygame.sprite.Sprite):
    def __init__(self, artifact_type, position):
        super().__init__()
        self.active = False
        self.type = artifact_type
        self.properties = self.get_artifact_properties(self.type)
        for property, value in self.properties.items():
            if property == "image":
                self.image = value
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect(center=(position[0], position[1]))

    def get_artifact_properties(self, artifact_type):
        properties = {
            ArtifactType.MILK: {
                'name': ArtifactType.MILK.value,
                'image': pygame.image.load("./core/assets/артефакты/молоко.png"),
                'projectile_speed': 6,
                'attack_speed_mult': 4,
                'projectile_size': (6, 6),
                'projectile_damage': -6,
                'projectile_texture': pygame.image.load("./core/assets/проджектайлы/слеза молоко.png"),
                'price': 400},
            ArtifactType.FAIRY_WINGS: {
                'name': ArtifactType.FAIRY_WINGS.value,
                'image': pygame.image.load("./core/assets/артефакты/крылья.png"),
                'move_speed': 3,
                'price': 300},
            ArtifactType.STRAWBERRY: {
                'name': ArtifactType.STRAWBERRY.value,
                'image': pygame.image.load("./core/assets/артефакты/клубника.png"),
                'max_hp': 75,
                'price': 350},
            ArtifactType.CATERPILLAR: {
                'name': ArtifactType.CATERPILLAR.value,
                'image': pygame.image.load("./core/assets/артефакты/гусеница.png"),
                'companion': pygame.image.load("./core/assets/артефакты/гусеница.png"),
                # image это иконка, а companion это спрайт для нпс.
                'price': 400},  # Одинаковы потому что картинка имеется только одна. Увы
            ArtifactType.HEDGEHOG: {
                'name': ArtifactType.HEDGEHOG.value,
                'image': pygame.image.load("./core/assets/артефакты/ёж.png"),
                'projectiles_quantity': 2,
                'price': 600},
            ArtifactType.ZEBRA_HOOF: {
                'name': ArtifactType.ZEBRA_HOOF.value,
                'image': pygame.image.load("./core/assets/артефакты/копыто зебры.png"),
                'max_hp': -20,
                'projectile_damage': 4,
                'price': 300},
            ArtifactType.STAR: {
                'name': ArtifactType.STAR.value,
                'image': pygame.image.load("./core/assets/артефакты/звезда.png"),
                'poison_damage': 3.5,
                'poison_time': 300,
                'price': 250},
            ArtifactType.FLY: {
                'name': ArtifactType.FLY.value,
                'image': pygame.image.load("./core/assets/артефакты/муха.png"),
                'companion': pygame.image.load("./core/assets/артефакты/муха.png"),
                'price': 450},
            ArtifactType.AGARIC: {
                'name': ArtifactType.AGARIC.value,
                'image': pygame.image.load("./core/assets/артефакты/мухомор.png"),
                'confusion': 3,
                'price': 500},
            ArtifactType.TURNIP: {
                'name': ArtifactType.TURNIP.value,
                'image': pygame.image.load("./core/assets/артефакты/репа.png"),
                'companion': pygame.image.load("./core/assets/проджектайлы/репа вонь.png"),
                'price': 350},
            ArtifactType.WEB: {
                'boss': True,
                'name': ArtifactType.WEB.value,
                'image': pygame.image.load("./core/assets/артефакты/паутина.png"),
                'projectile_damage': 7,
                'projectile_slowdown_mult': 2,
                'projectile_slowdown_time': 70,
                'projectile_speed': -9,
                'projectiles_quantity': -1,
                'attack_speed_mult': 0.9,
                'projectile_size': (25, 25),
                'projectile_texture': pygame.image.load("./core/assets/проджектайлы/слеза пауко.png")},
            ArtifactType.WASP_STINGER: {
                'boss': True,
                'name': ArtifactType.WASP_STINGER.value,
                'image': pygame.image.load("./core/assets/артефакты/жало.png"),
                'projectile_damage': 20,
                'projectile_size': (25, 25)},
            ArtifactType.SPARROW_QUILL: {
                'boss': True,
                'name': ArtifactType.SPARROW_QUILL.value,
                'image': pygame.image.load("./core/assets/артефакты/перо.png"),
                'ability_name': "1st hit invincibility"},
            ArtifactType.FROG_LEG: {
                'boss': True,
                'name': ArtifactType.FROG_LEG.value,
                'image': pygame.image.load("./core/assets/артефакты/лягушачья лапка.png"),
                'ability_name': "Dash"},
            ArtifactType.RAT_TAIL: {
                'boss': True,
                'name': ArtifactType.RAT_TAIL.value,
                'image': pygame.image.load("./core/assets/артефакты/крысохвост.png"),
                'ability_name': "1st shot invisibility"},
        }[artifact_type]
        return properties

    def get_random_artifact(self, owned_artifacts, dropped_artifacts, position):
        free_list = list(ArtifactType)

        for art_type in list(ArtifactType):
            boss_art = Artifact(art_type, position)
            for property, value in boss_art.properties.items():
                if property == "boss":
                    free_list.remove(boss_art.type)

        for owned_art in owned_artifacts:
            try:
                free_list.remove(owned_art.type)
            except:
                pass

        for dropped_art in dropped_artifacts:
            try:
                free_list.remove(dropped_art.type)
            except:
                pass
        if len(free_list) > 0:
            rand_art = Artifact(random.choice(free_list), position)
            return rand_art
        else:
            return []