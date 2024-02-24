"""
Stratego

This class implements the "main" application/Python Arcade class that
manages drawing, windowing, input, etc.
"""
import random
import json

from config import config
from board import Board
from player import Player
from pieces import Piece


class Stratego:
    """
    Main Stratego game class
    This implements the event handling/callbacks
    """

    def __init__(self):
        self.user = Player("CS3050 Testing Team")
        self.opponent = Player("Sarge")
        self.board = Board(config['board']['rows'], config['board']['columns'], self.user, self.opponent)
        self.presets = load_presets(config['presets']['data_file'])

    def reset_pieces(self) -> None:
        self.user.reset_pieces()
        self.opponent.reset_pieces()
        self.board.reset_pieces()

    def update_moves(self):
        # Get moves for each live piece
        for piece in self.board.alive_pieces:
            self.board.get_moves(piece)

    def _apply_preset(self, preset_index: int, pieces: list[any], rows: range):
        preset = self.presets[preset_index]
        for i, piece_name in enumerate(preset):
            good = False
            for j, piece in enumerate(pieces[i:]):
                if piece.name == piece_name:
                    index = j + i
                    # Swap the two pieces
                    pieces[i], pieces[index] = pieces[index], pieces[i]

                    good = True
                    break
            if not good:
                raise Exception(f'Invalid piece preset {preset_index}. Could not find position for {piece_name}, {i}')

        index = 0
        for y in rows:
            for x in range(self.board.columns):
                piece = pieces[index]
                piece.x_pos = x
                piece.y_pos = y
                self.board.pieces.append(piece)
                index += 1

    def apply_user_preset(self, preset_index: int):
        self._apply_preset(preset_index, self.user.alive_pieces, range(0, 4))

    def apply_opponent_preset(self, preset_index: int):
        self._apply_preset(preset_index, self.opponent.alive_pieces, range(9, 5, -1))

    def shortest_path(self, hvt, movable_pieces) -> tuple[Piece, tuple[int, int]] | None:
        """
        BFS-style algorithm that finds a move that brings a Piece closest to an HVT.
        :param hvt: Targeted Piece
        :param movable_pieces: List of movable Pieces
        :return:
        """
        # Initialize temporary variable of path to return to user
        path_to_move = None

        # Only engage if able and if HVT is stronger than a Scout
        if movable_pieces and hvt.strength > 2:

            current_breath = []
            next_breath = []
            invalid_sq = []
            invalid_sq_path = []
            capture_moves = []
            invalid_sq_piece = []
            dist = 1
            move_found = False

            # Add out-of-bounds squares to invalid_sq
            invalid_indices = (-1, 10)
            for y in range(self.board.rows):
                invalid_sq.append((invalid_indices[0], y))
                invalid_sq.append((invalid_indices[1], y))
            for x in range(self.board.columns):
                invalid_sq.append((x, invalid_indices[0]))
                invalid_sq.append((x, invalid_indices[1]))

            # Add all opponent piece coordinates to invalid_sq - can't attack ourselves!
            for piece in self.opponent.alive_pieces:
                invalid_sq.append(piece.coords)

            for c_piece in movable_pieces:
                # Make sure we don't set a path through pieces we can't capture
                for user_piece in self.user.visible_pieces:
                    if user_piece.strength > c_piece.strength:
                        invalid_sq_piece.append(user_piece.coords)

                for move in c_piece.moves:
                    if move == hvt.coords:
                        # Enter move as path, with dist
                        capture_moves.append((c_piece, move, dist))
                    # Can't capture HVT directly, explore moves that lead towards it
                    else:
                        current_breath.append(move)
                        invalid_sq_path.append(move)
                        # Enter loop to evaluate all possible movement from
                        while len(current_breath) > 0 and not move_found:
                            # Increment distance (moves from current piece)
                            dist += 1

                            # Evaluate current layer of attacks (certain distance away)
                            for b_move in current_breath:
                                x_to_check = b_move[0]
                                y_to_check = b_move[1]
                                # Check above coords
                                if (x_to_check, y_to_check + 1) not in (
                                        invalid_sq + invalid_sq_piece + invalid_sq_path):  # If move is not invalid, then append to next_breath.
                                    next_breath.append((x_to_check, y_to_check + 1))
                                    invalid_sq_path.append((x_to_check, y_to_check + 1))
                                # Check below coords
                                if (x_to_check, y_to_check - 1) not in (
                                        invalid_sq + invalid_sq_piece + invalid_sq_path):  # If move is not invalid, then append to next_breath.
                                    next_breath.append((x_to_check, y_to_check - 1))
                                    invalid_sq_path.append((x_to_check, y_to_check - 1))
                                # Check left coords
                                if (x_to_check - 1, y_to_check) not in (
                                        invalid_sq + invalid_sq_piece + invalid_sq_path):  # If move is not invalid, then append to next_breath.
                                    next_breath.append((x_to_check - 1, y_to_check))
                                    invalid_sq_path.append((x_to_check - 1, y_to_check))
                                # Check right coords
                                if (x_to_check + 1, y_to_check) not in (
                                        invalid_sq + invalid_sq_piece + invalid_sq_path):  # If move is not invalid, then append to next_breath.
                                    next_breath.append((x_to_check + 1, y_to_check))
                                    invalid_sq_path.append((x_to_check + 1, y_to_check))

                            # Clear all current breath nodes
                            current_breath.clear()

                            # Search all new nodes to search
                            for nb_move in next_breath:
                                # Check each of the directions
                                if nb_move == hvt.coords:
                                    # Enter move as path, with dist
                                    capture_moves.append((c_piece, move, dist))
                                    move_found = True
                                else:
                                    current_breath.append(nb_move)

                            # Clear current next_breath
                            next_breath.clear()

                    dist = 1
                    current_breath.clear()
                    move_found = False

                    # Wipe all invalid spaces for the path
                    invalid_sq_path.clear()

                # Wipe all invalid spaces for the individual piece
                invalid_sq_piece.clear()

            # If capture_moves is empty, then no path to the high-value-piece could be found, so we exit function.
            if len(capture_moves) > 0:
                current_move = capture_moves[0]
                for move in capture_moves:
                    if move[2] < current_move[2]:
                        current_move = move

                # Queue this move to be taken and end of opponent_move
                path_to_move = (current_move[0], current_move[1])
        return path_to_move

    def opponent_turn(self) -> tuple[tuple[int, int] | None, tuple[int, int] | None]:
        """
        If it's dumb it should at least be threateningly dumb.
            - Sam Clear
        :return: None
        """
        # Generate moves for new board state
        self.update_moves()

        # Create temporary variable for current piece to move's current position
        previous_pos = None

        # Creating variable to place next move
        move_to_take = None

        # Find all the pieces that can be moved by the opponent
        movable_pieces = self.opponent.movable_pieces

        # If we can't move: why bother?
        if not movable_pieces:
            # Do nothing
            return None, None

        # Find the strongest movable piece's strength
        greatest_movable_strength = 1
        for piece in movable_pieces:
            if piece.strength > greatest_movable_strength:
                greatest_movable_strength = piece.strength

        # Find the strongest piece on the user's side that the opponent can capture (and can see)
        # Placeholder variable for strongest piece to-capture
        high_val_target = None

        # Find possible pieces to capture
        viable_targets = self.user.visible_pieces

        # Find the highest-strength piece that we can capture
        for piece in viable_targets:
            # Make sure we aren't comparing against None
            if high_val_target:
                if high_val_target.strength < piece.strength < greatest_movable_strength:
                    high_val_target = piece
            # Make sure we don't select an HVT we can't engage
            else:
                if piece.strength < greatest_movable_strength:
                    high_val_target = piece

        # Find the closest move to HVT or closest attainable piece
        if high_val_target is not None:

            # Find movable pieces that can capture HVT
            capturing_pieces = []
            for piece in movable_pieces:
                if piece.strength > high_val_target.strength:
                    capturing_pieces.append(piece)

            # Return either no move, or a move which the opponent will take
            move_to_take = self.shortest_path(high_val_target, capturing_pieces)
            if move_to_take is not None:
                previous_pos = move_to_take[0].coords

        # Get moves that result in taking the player's piece. Prioritize backstabbing marshals and defusing bombs
        possible_opponent_moves = []
        for piece in movable_pieces:
            for move in piece.moves:
                possible_piece_to_attack = self.board.is_occupied(move[0], move[1])
                if possible_piece_to_attack is not None:
                    if (possible_piece_to_attack not in self.opponent.alive_pieces) and ((piece.strength == 3 and possible_piece_to_attack.strength == 11) or (piece.strength == 1 and possible_piece_to_attack.strength == 10)):
                        move_to_take = (piece, move)
                        previous_pos = piece.coords
                    elif not possible_piece_to_attack.is_hidden:
                        if possible_piece_to_attack.strength <= piece.strength:
                            possible_opponent_moves.append((piece, move))
                    else:
                        possible_opponent_moves.append((piece, move))
                else:
                    possible_opponent_moves.append((piece, move))

        # Currently, pick first scout's move that attacks a new opponent. If there are no scouts, then
        # send moves from marshal to decreasing ranks.
        # Choice #1: Find a scout that can attack another piece
        if move_to_take is None:
            for piece_move in possible_opponent_moves:
                if piece_move[0].move_limit is None:
                    attacked_piece = self.board.is_occupied(piece_move[1][0], piece_move[1][1])
                    if attacked_piece is not None:
                        # Scouting is wasted if the unit is not hidden
                        if attacked_piece.is_hidden:
                            move_to_take = piece_move
                            previous_pos = move_to_take[0].coords

        # Choice #2: Cautious attacking
        if move_to_take is None:
            priority_of_sacrifice = [6, 5, 4, 10, 9, 8, 7, 3, 1, 2]
            iterator_move = 0
            while move_to_take is None and iterator_move < 10:
                for piece_move in possible_opponent_moves:
                    # Moves down board, and is as strong as the move strength limit
                    if piece_move[0].strength == priority_of_sacrifice[iterator_move] and piece_move[0].y_pos > piece_move[1][1]:
                        move_to_take = piece_move
                        previous_pos = move_to_take[0].coords
                iterator_move += 1

        # Choice #3: Make a move
        if move_to_take is None:
            move_to_take = possible_opponent_moves[random.randint(0, len(possible_opponent_moves) - 1)]
            previous_pos = move_to_take[0].coords

        # Determine whether the move requires the user to make an attack or move, then take the move
        user_piece_to_attack = self.board.is_occupied(move_to_take[1][0], move_to_take[1][1])
        if user_piece_to_attack is None:
            move_to_take[0].move(move_to_take[1][0], move_to_take[1][1])
        else:
            move_to_take[0].attack(user_piece_to_attack)

        # Update the board state and return
        self.update_moves()
        return previous_pos, move_to_take[1]


def load_presets(name: str) -> dict[int, list[str]]:
    with open(name, 'r') as file:
        presets_file = json.load(file)

    presets = {}
    for preset in presets_file:
        presets[preset['index']] = preset['layout']

    return presets


game = Stratego()
