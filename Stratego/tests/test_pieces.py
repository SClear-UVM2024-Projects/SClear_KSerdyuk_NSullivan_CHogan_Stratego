import unittest

from stratego.pieces import Piece

# TEST VALUES
name = "test"
strength = 47
x_pos = 5
y_pos = 5


# TODO: Update tests

class TestPiece(unittest.TestCase):
    def test_name(self):
        piece = Piece(name, strength)
        self.assertEqual(piece.name, name)

    def test_strength(self):
        piece = Piece(name, strength)
        self.assertEqual(piece.strength, strength)

    def test_get_x_pos(self):
        piece = Piece(name, strength)
        self.assertEqual(piece.x_pos, None)

    def test_set_x_pos(self):
        piece = Piece(name, strength)
        piece.x_pos = x_pos
        self.assertEqual(piece.x_pos, x_pos)

    def test_get_y_pos(self):
        piece = Piece(name, strength)
        self.assertEqual(piece.y_pos, None)

    def test_set_y_pos(self):
        piece = Piece(name, strength)
        piece.y_pos = y_pos
        self.assertEqual(piece.y_pos, y_pos)
