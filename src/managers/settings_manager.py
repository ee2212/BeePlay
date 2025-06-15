# managers/settings_manager.py
import pygame
import json
import os


class SettingsManager:
    """Manages game settings, including loading, saving, and updating."""

    def __init__(self, config_path: str = "data/settings.json"):
        """
        Initializes the SettingsManager.

        Args:
            config_path: The path to the settings configuration file.
        """
        self.config_path = config_path
        self.default_settings = {
            "screen_width": 1280,
            "screen_height": 720,
            "fps_limit": 60,
            "tile_size": 64,
            "room_width": 14,
            "room_height": 9,
            "poison_cooldown": 60
        }
        self.default_settings["room_width"] *= self.default_settings["tile_size"]
        self.default_settings["room_height"] *= self.default_settings["tile_size"]

        self.settings = self.default_settings.copy()
        self.load_settings()

    def load_settings(self):
        """Loads settings from the configuration file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                    self.settings.update(data)
                except json.JSONDecodeError:
                    print("⚠️ Ошибка чтения файла конфигурации. Используются настройки по умолчанию.")

    def save_settings(self):
        """Saves current settings to the configuration file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as file:
            json.dump(self.settings, file, indent=4)

    def update_setting(self, key: str, value):
        """
        Updates a specific setting and applies changes if necessary.

        Args:
            key: The key of the setting to update.
            value: The new value for the setting.
        """
        if key in self.settings:
            self.settings[key] = value
            if key in ["screen_width", "screen_height"]:
                pygame.display.set_mode((self.settings["screen_width"], self.settings["screen_height"]))
            self.save_settings()

    def get(self, key: str):
        """
        Retrieves the value of a specific setting.

        Args:
            key: The key of the setting to retrieve.

        Returns:
            The value of the setting.
        """
        return self.settings.get(key)