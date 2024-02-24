import random

from pieces import Piece
from player import Player


class Board:
    def __init__(self, rows: int, columns: int, player0: Player, player1: Player, pieces: list[Piece] = None):
        self._rows = rows
        self._columns = columns
        self._row_index = rows - 1
        self._column_index = columns - 1
        self._player0 = player0
        self._player1 = player1
        if pieces is None:
            pieces = []
        self._pieces = pieces

    @property
    def pieces(self) -> list[Piece]:
        return self._pieces

    @property
    def alive_pieces(self) -> list[Piece]:
        return [p for p in self.pieces if not p.is_captured]

    @property
    def columns(self) -> int:
        return self._columns

    @property
    def rows(self) -> int:
        return self._rows

    def reset_pieces(self) -> None:
        self._pieces = []

    def can_move(self, x: int, y: int, piece: Piece) -> bool:
        # Movement coordinates
        coords = (x, y)
        # Individual axis differences
        # In the case of a valid move one should always be zero
        x_diff = piece.x_pos - x
        y_diff = piece.y_pos - y

        # POSITIONAL CHECKS

        # Check case: no movement
        if piece.coords == coords:
            return False
        # Check case: not a straight line
        elif piece.x_pos != x and piece.y_pos != y:
            return False
        # Check case: occupied by friendly piece
        elif self.are_friendly(piece, self.is_occupied(x, y)):
            return False
        # Check case: not on board
        elif min(coords) < 0 or max(coords) > self._rows:
            return False

        # MOVE LIMIT CHECKS

        # Check case: outside move limit
        # Excludes pieces with no move limit
        if piece.move_limit:
            if abs(x_diff) > piece.move_limit or abs(y_diff) > piece.move_limit:
                return False
        # Check case: move limit 0
        elif piece.move_limit == 0:
            return False
        # Check case: piece(s) in the way
        else:
            # Put coordinates into range-friendly order
            x_range = sorted((x, piece.x_pos))
            y_range = sorted((y, piece.y_pos))

            x_range[0] = x_range[0] + 1
            y_range[0] = y_range[0] + 1

            if x_diff:
                # Iterate over pieces in between x-axis coords
                for i in range(*x_range):
                    if other := self.is_occupied(i, y):
                        if other is not piece:
                            return False
            elif y_diff:
                # Iterate over pieces in between y-axis coords
                for i in range(*y_range):
                    if other := self.is_occupied(x, i):
                        if other is not piece:
                            return False

        # All checks passed
        return True

    def is_occupied(self, x: int, y: int) -> Piece | None:
        """
        Function to check if a given coordinate has a Piece
        :param x: x-coordinate to check
        :param y: y-coordinate to check
        :return: Returns Piece if present, false otherwise
        """
        for piece in self._pieces:
            if (x, y) == piece.coords:
                return piece
        return None

    def get_moves(self, piece: Piece, update_piece=True) -> list[tuple[int, int]]:
        moves = []
        # Try all positions on board
        for i in range(self._columns):
            for j in range(self._rows):
                if self.can_move(i, j, piece):
                    moves.append((i, j))

        # Handle reporting
        if update_piece:
            piece.moves = moves
        return moves

    def are_friendly(self, piece0: Piece, piece1: Piece) -> bool:
        """
        Checks if two given pieces have the same owner
        :param piece0: First piece to compare
        :param piece1: Second piece to compare
        :return: Boolean indicating if pieces are friendly
        """
        # Logic Explanation:
        # - Takes XOR of player0's ownership of both pieces
        # - If player0 owns one piece but not the other the XOR returns True and the pieces are enemies
        # - If player0 owns either both or neither of the pieces the XOR returns False and the pieces are allied
        # - XOR inverted return to provide boolean consistent with expected behavior
        # Simple as.
        if piece0 is None or piece1 is None:
            # The None type is inherently not friendly
            return False
        else:
            return not self._player0.is_owner(piece0) != self._player0.is_owner(piece1)

    def add_piece(self, x: int, y: int, piece: Piece) -> bool:
        if y >= 4:
            # Don't allow user to place pieces on the 5th rank
            return False
        for board_piece in self._pieces:
            if board_piece.coords == (x, y):
                return False

        piece.move(x, y)
        self._pieces.append(piece)
        return True

    def add_opponent_pieces(self, player: Player):
        pieces = player.alive_pieces.copy()
        random.shuffle(pieces)
        for i in range(self._rows):
            for j in range(6, self._columns):
                piece = pieces.pop()
                piece.move(i, j)
                self._pieces.append(piece)
