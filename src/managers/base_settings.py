from src.managers.settings_manager import SettingsManager

settings_manager = SettingsManager()

fps_limit = settings_manager.get("fps_limit")
tile_size = settings_manager.get("tile_size")
screen_width = settings_manager.get("screen_width")
screen_height = settings_manager.get("screen_height")
room_width = settings_manager.get("room_width")
room_height = settings_manager.get("room_height")
poison_cooldown = settings_manager.get("poison_cooldown")
