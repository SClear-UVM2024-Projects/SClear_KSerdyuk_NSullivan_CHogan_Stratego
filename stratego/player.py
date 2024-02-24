import pieces
from pieces import Piece


class Player:
    """
    A class to represent a Player
    
    Attributes
    ----------
    name : str
        Player Name
    pieces: list[Piece]
        List of pieces owned by this player
    """

    def __init__(self, name: str):
        self._name = name
        self._pieces = pieces.initialize()

    def is_owner(self, piece: Piece) -> bool:
        for p in self._pieces:
            if piece is p:
                return True
        # No hits
        return False

    def reset_pieces(self) -> None:
        self._pieces = pieces.initialize()

    @property
    def has_flag(self) -> bool:
        return bool([p for p in self.alive_pieces if p.strength == 0])

    @property
    def alive_pieces(self) -> list[Piece]:
        return [p for p in self._pieces if not p.is_captured]

    @property
    def captured_pieces(self) -> list[Piece]:
        return [p for p in self._pieces if p.is_captured]

    @property
    def movable_pieces(self) -> list[Piece]:
        return [p for p in self.alive_pieces if p.moves]

    @property
    def visible_pieces(self) -> list[Piece]:
        return [p for p in self.alive_pieces if not p.is_hidden]
