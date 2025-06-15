# managers/save_manager.py
import pickle
import os


class SavesSystem:
    """Manages saving and loading game data."""

    def __init__(self, file_extension: str, saves_folder: str):
        """
        Initializes the SavesSystem.

        Args:
            file_extension: The file extension for save files (e.g., ".save").
            saves_folder: The directory where save files are stored.
        """
        self.file_extension = file_extension
        self.saves_folder = saves_folder

    def save_data(self, data, slot: int, name: str):
        """
        Saves data to a specific save slot and file name.

        Args:
            data: The data to be saved.
            slot: The save slot number.
            name: The name of the file within the save slot.
        """
        slot_folder = os.path.join(self.saves_folder, f"save slot №{slot}")
        os.makedirs(slot_folder, exist_ok=True)
        file_path = os.path.join(slot_folder, f"{name}{self.file_extension}")
        with open(file_path, "wb") as file:
            pickle.dump(data, file)

    def load_data(self, slot: int, name: str):
        """
        Loads data from a specific save slot and file name.

        Args:
            slot: The save slot number.
            name: The name of the file within the save slot.

        Returns:
            The loaded data.
        """
        file_path = os.path.join(self.saves_folder, f"save slot №{slot}", f"{name}{self.file_extension}")
        with open(file_path, "rb") as file:
            data = pickle.load(file)
        return data

    def check_for_file(self, slot: int, name: str) -> bool:
        """
        Checks if a specific save file exists.

        Args:
            slot: The save slot number.
            name: The name of the file within the save slot.

        Returns:
            True if the file exists, False otherwise.
        """
        file_path = os.path.join(self.saves_folder, f"save slot №{slot}", f"{name}{self.file_extension}")
        return os.path.exists(file_path)

    def load_game_data(self, save_slot_number: int, files_to_load: list, default_data: list):
        """
        Loads multiple game data files for a given save slot.

        Args:
            save_slot_number: The save slot number.
            files_to_load: A list of file names to load.
            default_data: A list of default values to use if a file is not found.

        Returns:
            A tuple of loaded data, or a single value if only one file is loaded.
        """
        variables = []
        for index, file_name in enumerate(files_to_load):
            if self.check_for_file(save_slot_number, file_name):
                variables.append(self.load_data(save_slot_number, file_name))
            else:
                variables.append(default_data[index])

        return tuple(variables) if len(variables) > 1 else variables[0] if variables else None