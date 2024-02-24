from dataclasses import dataclass
from enum import Enum
from typing import List


class CallBack(Enum):
    KEY_PRESS = 0
    MOUSE_PRESS = 1
    MOUSE_MOTION = 2


key_press = []
mouse_press = []
mouse_motion = []


@dataclass
class GameObject:
    def __init__(self, callbacks: List[CallBack]):
        for callback in callbacks:
            match callback:
                case CallBack.KEY_PRESS:
                    key_press.append(self)
                case CallBack.MOUSE_PRESS:
                    mouse_press.append(self)
                case CallBack.MOUSE_MOTION:
                    mouse_motion.append(self)
                case _:
                    raise Exception(f'Unknown enum callback {callback}')

    def setup(self):
        pass

    def draw(self, width: int, height: int):
        pass

    def on_update(self, delta_time: float):
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        https://api.arcade.academy/en/latest/arcade.key.html
        """
        pass

    def on_key_release(self, symbol: int, modifiers: int):
        """
        Called whenever the user lets off a previously pressed key.
        """
        pass

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        """
        Called whenever the user lets off a previously pressed key.
        """
        pass

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """
        Called when the user presses a mouse button.
        """
        pass

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        """
        Called when a user releases a mouse button.
        """
        pass
