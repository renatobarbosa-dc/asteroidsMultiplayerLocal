"""Game scene states."""

from enum import Enum, auto


class SceneState(Enum):
    """Struct that manages game's scene state"""

    MENU = auto()
    PLAY = auto()
    GAME_OVER = auto()
