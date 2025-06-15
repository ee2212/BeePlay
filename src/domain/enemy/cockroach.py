import pygame

from src.domain.enemy.enemy import Enemy


class Cockroach(Enemy):
    def __init__(self, spawn_rect, type):
        super().__init__(spawn_rect)
        self.type = type
        match self.type:
            case "обычный":
                self.attack_cooldown = 25
                self.max_health = 20
                self.damage = 6
                self.move_speed = 4
                self.size = (50, 50)
            case "усиленный":
                self.attack_cooldown = 15
                self.max_health = 40
                self.move_speed = 5
                self.damage = 12
                self.size = (60, 60)
            case "маленький обычный":
                self.attack_cooldown = 6
                self.damage = 2.5
                self.max_health = 1
                self.move_speed = 5.5
                self.size = (25, 25)
                self.spawn_shift = -24
            case "маленький усиленный":
                self.attack_cooldown = 9
                self.damage = 4.5
                self.max_health = 10
                self.move_speed = 6
                self.size = (30, 30)
                self.spawn_shift = -29
        self._move_speed = self.move_speed
        self.health = self.max_health
        self.image = pygame.image.load("./core/assets/персонажи/таракан %s.png" % type)
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(center=self.get_rand_pos(self._spawn_rect, self.spawn_shift))

    def update(self, player_pos):
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:
            self.rect.x += dx / distance * self.move_speed
            self.rect.y += dy / distance * self.move_speed

        if self.health <= 0 and self.type[:9] != "маленький":
            return self

        super().update()
