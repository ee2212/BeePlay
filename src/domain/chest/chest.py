import pygame

from src.domain.artifact.artifact import Artifact


class Chest(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.size = (100, 80)
        self.image = pygame.image.load("./core/assets/комнаты/сундук закрытый.png")
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(center=position)
        self.opened = False

    def open_chest(self, owned_artifacts, dropped_artifacts, position):
        rand_art = Artifact.get_random_artifact(Artifact, owned_artifacts, dropped_artifacts, position)
        self.opened = True
        return rand_art