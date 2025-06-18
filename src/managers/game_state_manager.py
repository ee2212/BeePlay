# managers/game_state_manager.py
import pygame
from enum import Enum


class GameState(Enum):
    """Enumerates the possible states of the game."""
    MAIN_MENU = 1
    SAVES = 2
    SETTINGS = 3
    FOREST = 4
    HIVE = 5
    FLOWER = 6


class GameStateManager:
    """Manages the current state of the game."""

    def __init__(self):
        """Initializes the GameStateManager with the default state."""
        self.state = GameState.MAIN_MENU

    def change_state(self, new_state: GameState):
        """
        Changes the current game state to the new state.

        Args:
            new_state: The new state to transition to.
        """
        self.state = new_state

    def current_state(self) -> GameState:
        """
        Returns the current game state.

        Returns:
            The current GameState.
        """
        return self.state
    