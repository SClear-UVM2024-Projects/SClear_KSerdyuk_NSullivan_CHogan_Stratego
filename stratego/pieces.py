from __future__ import annotations

import json
import copy

from config import config
from game_object import GameObject


class Piece(GameObject):
    """
    A class to represent a Stratego piece

    Attributes
    ----------
    name : str
        name of the piece
    strength : int
        strength of the piece
    x_pos : None | int
        x coordinate of the piece
    y_pos : None | int
        y coordinate of the piece
    coords : (None | int, None | int)
        tuple representation of piece coordinates
    is_hidden : bool
        status of whether the unit has been found
    is_captured : bool
        status of whether the piece has been captured
    picture : str
        file name
    kill_marshal : bool
        if the piece can kill a marshal (10 strength)
    defuse_bomb : bool
        if the piece can defuse a bomb
    move_limit : None | int
        max number of spaces a piece can move in a turn, None if no limit

    Methods
    -------
    move():
        pass
    attack():
        pass
    """

    def __init__(self, name: str, strength: int, kill_marshal: bool = False, defuse_bombs: bool = False,
                 move_limit: None | int = 1, is_hidden: bool = True, is_captured: bool = False):
        self._name = name
        self._strength = strength
        self._x_pos = None
        self._y_pos = None
        self._is_hidden = is_hidden
        self._is_captured = is_captured
        self._kill_marshal = kill_marshal
        self._defuse_bombs = defuse_bombs
        self._move_limit = move_limit
        self._moves = []

    # PROPERTIES
    @property
    def name(self) -> str:
        return self._name

    @property
    def strength(self) -> int:
        return self._strength

    @property
    def x_pos(self) -> None | int:
        return self._x_pos

    @x_pos.setter
    def x_pos(self, value: int):
        self._x_pos = value

    @property
    def y_pos(self) -> None | int:
        return self._y_pos

    @y_pos.setter
    def y_pos(self, value: int):
        self._y_pos = value

    @property
    def coords(self) -> (None | int, None | int):
        return self.x_pos, self.y_pos

    @property
    def is_hidden(self) -> bool:
        return self._is_hidden

    @is_hidden.setter
    def is_hidden(self, value: bool):
        self._is_hidden = value

    @property
    def is_captured(self) -> bool:
        return self._is_captured

    @is_captured.setter
    def is_captured(self, value: bool):
        self._is_captured = value

    @property
    def kill_marshal(self) -> bool:
        return self._kill_marshal

    @property
    def defuse_bombs(self) -> bool:
        return self._defuse_bombs

    @property
    def move_limit(self) -> None | int:
        return self._move_limit

    @property
    def moves(self) -> list[tuple[int, int]]:
        return self._moves

    @moves.setter
    def moves(self, value: list[tuple[int, int]]):
        self._moves = value

    # METHODS
    def move(self, x_coord: int | None, y_coord: int | None) -> None:
        """
        Moves Piece to a given space.
        Assumes that the given coords represent a valid space on the board to move to.
        :param x_coord: x-coordinate to move to
        :param y_coord: y-coordinate to move to
        :return: Nne
        """
        self.x_pos = x_coord
        self.y_pos = y_coord

    def can_kill(self, opponent: Piece) -> bool:
        """
        Evaluates if able to kill opposing piece. Does not evaluate for self-preservation.
        :param opponent: Piece object to evaluate an attack against
        :return: Boolean describing whether an attack would kill the opponent
        """
        # Spy VS Marshal special case
        if self.kill_marshal and opponent.strength == 10:
            return True
        # Miner VS Bomb special case
        elif self.defuse_bombs and opponent.strength == 11:
            return True
        # Standard case: As strong or stronger strength wins
        elif self.strength >= opponent.strength:
            return True
        else:
            return False

    def attack(self, opponent: Piece) -> None:
        """
        Evaluates and applies the results of an attack on another Piece object
        :param opponent: Piece to evaluate an attack against
        :return: None
        :raises:
            :exception "Stop hitting yourself!": Raised if a Piece attempts to confront the demons within
            (attacks itself)
        """
        # Make sure we aren't kicking our own ass
        if opponent is self:
            # There comes a time when we all are our own opponents
            raise Exception("Stop hitting yourself!")

        # Consult the oracle and see who secures the W
        victor = self.attack_oracle(opponent)

        if victor is self:
            opponent.is_captured = True
            self.is_hidden = False
            self.move(opponent.x_pos, opponent.y_pos)
            opponent.move(None, None)
        elif victor is opponent:
            self.is_captured = True
            opponent.is_hidden = False
            self.move(None, None)
        else:
            self.is_captured = True
            self.move(None, None)
            opponent.is_captured = True
            opponent.move(None, None)

    def attack_oracle(self, opponent: Piece) -> Piece | None:
        """
        Oracle function used to assess which piece, if any, would win a fight
        :param opponent: Opponent to hypothetically attack
        :return: Piece that would win, or None if no winner
        """
        if self.can_kill(opponent) and opponent.can_kill(self):
            # Special case for Spy and Marshal, make sure they aren't both spies
            if self.kill_marshal != opponent.kill_marshal:
                return self
            # Special case for Miner and Bomb, make sure they aren't both miners
            elif self.defuse_bombs != opponent.defuse_bombs:
                return self
            else:
                # Same strength - nobody wins
                return None
        elif self.can_kill(opponent):
            return self
        else:
            return opponent


def initialize() -> list[Piece]:
    # Get unit info
    with open(config['pieces']['data_file'], 'r') as file:
        unit_info = json.load(file)

    # Get unit counts
    unit_counts = config['pieces']['counts']

    # Initialize list of Piece objects
    pieces = []

    # Iterate over dict of units that we need
    for strength in unit_counts:
        # Get unit info
        unit = unit_info[strength]

        # Create piece object
        piece = Piece(unit['name'], strength, unit['kill_marshal'], unit['defuse_bombs'], unit['move_limit'])

        # Add as many Pieces as we need to list
        for _ in range(unit_counts[strength]):
            pieces.append(copy.copy(piece))

    return pieces
