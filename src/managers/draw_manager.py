import pygame
from src.constants.room_type import RoomType
from src.managers.base_settings import screen_width, screen_height, room_width, room_height

class DrawManager:

    def draw_ui(self, screen, current_room, player, clock, bag):
        # fps counter
        font = pygame.font.Font(None, 26)
        text = font.render(str(int(clock.get_fps())), True, (255, 0, 0))
        screen.blit(text, (screen_width - 20, 0))

        self.draw_currency_ui(screen, player)
        self.draw_health_ui(screen, player, current_room)
        self.draw_artifacts_ui(bag, (0, screen_height - 60), player, screen)

    def draw_currency_ui(self, screen, player):
        font = pygame.font.Font(None, 36)
        text = [
            f"Пыльца: {player.pollen}",
            f"Мёд: {player.honey}",
        ]
        for i, element in enumerate(text):
            surface = font.render(element, True, (255, 255, 255))
            screen.blit(surface, (10, 10 + i * 30)) # the margin is 30px

    def draw_health_ui(self, screen, player, current_room):
        font = pygame.font.Font(None, 26)
        text = font.render(
            f"Здоровье: {player.health}", True, (255, 255, 255))
        screen.blit(text, (screen_width // 2 - room_width // 2,
                    screen_height // 2 + room_height // 2 + 15))
        player.health_bar.draw(screen, 0) # player health

        if current_room.room_type == RoomType.BOSS:
            bosses_list = list(current_room.bosses)
            for boss in bosses_list:
                boss.health_bar.draw(screen, bosses_list.index(boss)) # boss health
                text = font.render(
                    f"Здоровье: {boss.health}", True, (255, 255, 255))
                screen.blit(text, (screen_width // 2 - room_width // 
                            2, screen_height // 2 - room_height // 2 - 17.5))

    def draw_artifacts_ui(self, bag_number, pos, player, screen):
        artifacts_to_draw = []

        for artifact in player.owned_artifacts[bag_number]: # collecting all images 
            artifacts_to_draw.append(artifact.image)

        for image in artifacts_to_draw:
            mod_image = pygame.transform.scale(image, (50, 50))
            screen.blit(
                mod_image, (pos[0] + artifacts_to_draw.index(image) * 80 + 20, pos[1]), mod_image.get_rect())  # the margin is 30px

    def draw_prices(self, prices, position, screen):
        font = pygame.font.Font(None, 30)
        text = "Артефакты за мёд!"
        surface = font.render(text, True, (255, 255, 255))
        screen.blit(surface, (screen_width // 2 -
                    100, screen_height // 2 - 150))

        for i in range(0, len(prices)): # prices bottom artifacts
            text = [f'{prices[i]}']
            for t, text in enumerate(text):
                surface = font.render(text, True, (255, 255, 255))
                screen.blit(
                    surface, (position[i][0] - 20, screen_height // 2 + 55 + t * 30))

    def draw_minimap(self, map_rooms, rooms, screen):
        base_x = screen_width - 305 # right up
        base_y = -20

        for (x, y, room_type) in map_rooms:

            rs = rooms
            r = rs[(x, y)]
            if r.visited == False: # not visited dark gray
                color = (50, 50, 50)
            else:
                match room_type:
                    case "normal":
                        color = (100, 100, 100) # gray
                    case "boss":
                        color = (205, 0, 0) # red
                    case "treasure":
                        color = (205, 205, 0) # yellow
                    case "shop":
                        color = (205, 105, 0) # orange
                    case "start":
                        color = (150, 200, 150) # green
                if r.current == True:
                    color = (color[0] + 50, color[1] + 50, color[2] + 50) # highlighting current
            px = base_x + x * 30
            py = base_y + y * 30

            s = pygame.Surface((28, 28)) # squares for rooms
            s.set_alpha(128) # translucent
            s.fill((color))
            screen.blit(s, (px, py))

    def draw_bg_image(self, image, screen):  # drawing game
        bg_image = image
        bg_image = pygame.transform.scale(
            bg_image, (screen_width, screen_height))
        bg_image_rect = bg_image.get_rect()
        bg_image_rect.center = (screen_width // 2, screen_height // 2)
        screen.blit(bg_image, (0, 0), bg_image_rect)