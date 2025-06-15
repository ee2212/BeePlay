from src.domain.companion.companion import Companion


class Caterpillar(Companion):
    def __init__(self, position, companion_image, companion_name):
        super().__init__(position, companion_image, companion_name)
        self.distance_from_player = 130
        self.damage = 12
        self.attack_cooldown = 50
        self.speed = self.distance_from_player // 18 + 0.2 * self.distance_from_player // 30
        self.rotation_cooldown = self.angle // 4