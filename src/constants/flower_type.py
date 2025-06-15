from enum import Enum


class FlowerType(Enum):
    PURPLE_CLOSED = "цветок_закр_02"
    BLUE_CLOSED = "цветок_закр_01"
    ORANGE_CLOSED = "цветок_закр_03"
    PINK_CLOSED = "цветок_закр_04"
    RED_CLOSED = "цветок_закр_05"

    BLUE_OPEN = "цветок_откр_01"
    PURPLE_OPEN = "цветок_откр_02"
    ORANGE_OPEN = "цветок_откр_03"
    PINK_OPEN = "цветок_откр_04"
    RED_OPEN = "цветок_откр_05"

    BLUE_OPEN_HIGHLIGHT = "цветок_откр_подсвет_01"
    PURPLE_OPEN_HIGHLIGHT = "цветок_откр_подсвет_02"
    ORANGE_OPEN_HIGHLIGHT = "цветок_откр_подсвет_03"
    PINK_OPEN_HIGHLIGHT = "цветок_откр_подсвет_04"
    RED_OPEN_HIGHLIGHT = "цветок_откр_подсвет_05"
