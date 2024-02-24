from stratego.board import Board
from stratego.pieces import Piece
from stratego.config import config
from stratego.player import Player
import arcade
import json

import unittest

# Global Constants
ROW_COL_COUNT = 10
UNIT_DATA_FILENAME = "assets/units.json"
INITIAL_ROW_NUMBER = 0
STANDARD_MOVE_DISTANCE = 1
ROW_LENGTH = 10

# Initializing test variables
# This is under the assumption that we will have a full list of pieces, along with two lists accessible somehow for the player and the opponent.
pieces = []
pieces_opponent = []
pieces_user = []
units = json.load(open(UNIT_DATA_FILENAME, "r"))
user = Player("CS 3050 Testing Crew")
opponent = Player("Pulsar")

# Create all pieces lists, with the assumption that the columns 1-9 are filled with scouts, 0 are general, middle rows 4-5 are empty.
for row in range(ROW_COL_COUNT):
    for col in range(ROW_COL_COUNT):
        if col == 0:
            rank = 9
        else:
            rank = 2

        # Initialize piece info for given
        unit_info = units[rank]

        if row >= 6:
            pic_by_user = "assets/sprites/unknown.png"

        else:
            pic_by_user = unit_info["picture"]

        kill_marshal = unit_info.get("kill_marshal")
        defuse_bombs = unit_info.get("defuse_bombs")
        move_limit = unit_info.get("move_limit")

        current_sprite = arcade.Sprite(filename=pic_by_user)
        current_piece = Piece(unit_info.get("name"), rank, current_sprite, kill_marshal, defuse_bombs,
                              move_limit)
        current_piece.x_pos = col
        current_piece.y_pos = row

        # There are no pieces in rows 4 or 5, so only create pieces when they wouldn't be made in these two rows.
        if row < 4: # User's pieces
            # TEMPORARY: Pictures for all pieces in rows 0-3 have "?"
            # pictures representing Hidden, your pieces in rows 6-9 are
            # the general pictures. I will add in the future the ability
            # to see what of your pieces have been seen.
            pieces_user.append(current_piece)
            pieces.append(current_piece)
        elif row > 5: # Opponent's pieces
            pieces_opponent.append(current_piece)
            pieces.append(current_piece)
        # Pieces that are in rows 4 and 5 are not recorded, because the space in empty in the middle of the board.

    new_board = Board(config['board']['rows'], config['board']['columns'], user, opponent, pieces)


class Test_Board_Checkers(unittest.TestCase):

    def test_occupied(self):
        new_board.pieces[0].move(0, 0)
        self.assertEqual(new_board.is_occupied(0, 0), new_board.pieces[0])

    def test_not_occupied(self):
        self.assertEqual(new_board.is_occupied(4, 4), False)

    def test_invalid_occupied(self):
        self.assertEqual(new_board.is_occupied(-1, -1), False)

    def test_move_square(self):
        self.assertEqual(new_board.can_move(0, 3, pieces[20]), True)

    def test_move_many(self):
        self.assertEqual(new_board.can_move(1, 5, pieces[31]), True)

    def test_incorrect_move(self):
        self.assertEqual(new_board.can_move(1, 3, pieces[39]), False)

    def test_move_attack(self):
        self.assertEqual(new_board.can_move(9, 6, pieces[39]), True)


if __name__ == "__main__":
    unittest.main()


