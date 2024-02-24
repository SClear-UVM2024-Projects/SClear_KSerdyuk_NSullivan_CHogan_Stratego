import random

import arcade
from enum import Enum

from config import config
from stratego_game import game
from sprites import sprite_manager

# Are we running a debug mode?
DEBUG = config['debug']

# Number of loadable presets
PRESET_COUNT = config['presets']['count']

# Which preset should the opponent use
OPPONENT_PRESET = config['opponent']['preset']

# Get screen height/width from config file
SCREEN_HEIGHT = config['window']['height']
SCREEN_WIDTH = config['window']['width']

# Set how many rows and columns we will have
ROW_COUNT = config['board']['rows']
COLUMN_COUNT = config['board']['columns']

# This sets the WIDTH and HEIGHT of each grid location
BOARD_SIZE = config['board']['size']
# The board should fit into the screen even if the screen is smaller
BOARD_SIZE = min(BOARD_SIZE, SCREEN_HEIGHT)

SQUARE_SIZE = int(BOARD_SIZE / ROW_COUNT)

# Margins on the edges of the board
MARGIN_WIDTH = max(0, (SCREEN_WIDTH - BOARD_SIZE) / 2)
MARGIN_HEIGHT = max(0, (SCREEN_HEIGHT - BOARD_SIZE) / 2)

# Position of board on screen
BOARD_BL = (MARGIN_WIDTH, MARGIN_HEIGHT)
BOARD_TR = (BOARD_BL[0] + BOARD_SIZE, BOARD_BL[1] + BOARD_SIZE)


def grid_color(x: int, y: int) -> arcade.color:
    if y % 2 == 0:
        x += 1
    if x % 2 == 0:
        return arcade.color.BONE
    else:
        return arcade.color.MOSS_GREEN


def to_board_coord(x: int, y: int) -> tuple[int, int] | None:
    if x < BOARD_BL[0] or y < BOARD_BL[1] or x > BOARD_TR[0] or y > BOARD_TR[1]:
        return None
    x -= BOARD_BL[0]
    y -= BOARD_BL[1]
    x_pos = int(x // SQUARE_SIZE)
    y_pos = int(y // SQUARE_SIZE)
    return x_pos, y_pos


def to_screen_space(x: int, y: int) -> tuple[int, int]:
    x_pos = int(BOARD_BL[0] + SQUARE_SIZE * x + (SQUARE_SIZE / 2))
    y_pos = int(BOARD_BL[1] + SQUARE_SIZE * y + (SQUARE_SIZE / 2))
    return x_pos, y_pos


class BoardView(arcade.View):
    """
    Class that represents the game board
    """

    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLACK_OLIVE)

        # One dimensional list of all sprites in the two-dimensional sprite list
        self.grid_sprite_list = arcade.SpriteList()
        self.local_grid_sprites: list[list[arcade.Sprite]] = []

        self.piece_object_list = []

        self.last_mouse_pos = (0, 0)
        self.last_mouse_click = None
        self.selected_square = None

        # Debug stuff
        self.debug_msg_count = 0
        self.show_hidden = True

    def setup(self):
        # Constructing board sprites and initializing coordinates for pieces
        self.local_grid_sprites = []
        self.grid_sprite_list = arcade.SpriteList()
        # Create a list of solid-color sprites to represent each grid location
        for x in range(ROW_COUNT):
            self.local_grid_sprites.append([])
            for y in range(COLUMN_COUNT):
                sprite = arcade.SpriteSolidColor(SQUARE_SIZE, SQUARE_SIZE, grid_color(x, y))
                sprite.center_x = BOARD_BL[0] + SQUARE_SIZE * x + (SQUARE_SIZE / 2)
                sprite.center_y = BOARD_BL[1] + SQUARE_SIZE * y + (SQUARE_SIZE / 2)
                self.local_grid_sprites[x].append(sprite)
                self.grid_sprite_list.append(sprite)

        # Resize the sprites
        sprite_manager.resize_sprites(SQUARE_SIZE)

    def on_show_view(self):
        # self.setup()
        pass

    def on_draw(self):
        self.clear()
        self.debug_msg_count = 0
        # Batch draw the grid sprites
        self.grid_sprite_list.draw()

        for piece in filter(lambda p: p.x_pos is not None, game.user.alive_pieces):
            x, y = to_screen_space(piece.x_pos, piece.y_pos)
            sprite = sprite_manager.get_user_sprite(piece.name)
            sprite.center_x = x
            sprite.center_y = y
            sprite.draw()

        for piece in filter(lambda p: p.x_pos is not None, game.opponent.alive_pieces):
            x, y = to_screen_space(piece.x_pos, piece.y_pos)
            name = "Unknown" if piece.is_hidden else piece.name
            # Reveal info in debug mode
            if DEBUG and self.show_hidden:
                name = piece.name
            sprite = sprite_manager.get_opponent_sprite(name)
            sprite.center_x = x
            sprite.center_y = y
            sprite.draw()

        self.debug_msg("Debug:")
        self.debug_msg(f'Mouse pos: {self.last_mouse_pos}')
        self.debug_msg(f'Mouse click: {self.last_mouse_click}')
        self.debug_msg(f'Grid selected: {self.selected_square}')
        board_coord = to_board_coord(self.last_mouse_pos[0], self.last_mouse_pos[1])
        self.debug_msg(f'Grid hovered: {board_coord}')
        self.debug_msg(f'Show hidden: {self.show_hidden}')
        self.debug_msg('Press "Space" to flip')

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        self.last_mouse_click = (x, y)
        self.selected_square = to_board_coord(x, y)
        self.reset_colors()

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.last_mouse_pos = (x, y)

    def reset_colors(self):
        for x in range(ROW_COUNT):
            for y in range(COLUMN_COUNT):
                # I do not know why the default highlight color is white, but it is
                self.local_grid_sprites[x][y].color = arcade.color.WHITE

    def get_sprite(self, coord: tuple[int, int]) -> arcade.Sprite:
        return self.local_grid_sprites[coord[0]][coord[1]]

    def debug_msg(self, message: str):
        # Only show debug info in debug mode
        if not DEBUG:
            return
        arcade.draw_text(message, 10, SCREEN_HEIGHT - 20 * (self.debug_msg_count + 1))
        self.debug_msg_count += 1


class IntroView(BoardView):
    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Welcome to Your Stratego Game!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                         arcade.color.WHITE, font_size=30, anchor_x="center")
        arcade.draw_text("Click to Start", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_mouse_press(self, x, y, button, modifiers):
        game_view = SetupView()
        game_view.setup()
        self.window.show_view(game_view)


class WinView(BoardView):
    def __init__(self):
        super().__init__()

    def on_show(self):
        arcade.set_background_color(arcade.color.MOSS_GREEN)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("YOU WIN", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                         arcade.color.WHITE, font_size=30, anchor_x="center")
        arcade.draw_text("Click to Restart", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_mouse_press(self, x, y, button, modifiers):
        game_view = SetupView()
        game_view.setup()
        self.window.show_view(game_view)


class LoseView(BoardView):
    def __init__(self):
        super().__init__()

    def on_show(self):
        arcade.set_background_color(arcade.color.FIREBRICK)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("YOU LOSE", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                         arcade.color.WHITE, font_size=30, anchor_x="center")
        arcade.draw_text("Click to Restart", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_mouse_press(self, x, y, button, modifiers):
        game_view = SetupView()
        game_view.setup()
        self.window.show_view(game_view)


class StalemateView(BoardView):
    def __init__(self):
        super().__init__()

    def on_show(self):
        arcade.set_background_color(arcade.color.GRAY)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("STALEMATE", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                         arcade.color.WHITE, font_size=30, anchor_x="center")
        arcade.draw_text("Click to Restart", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_mouse_press(self, x, y, button, modifiers):
        game_view = SetupView()
        game_view.setup()
        self.window.show_view(game_view)


class SetupView(BoardView):
    """
    This view handles setting up the board where the user can place their pieces
    """
    def __init__(self):
        super().__init__()
        self.current_index = 0

    def setup(self):
        super().setup()

        # Clear pieces
        game.reset_pieces()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        super().on_mouse_press(x, y, button, modifiers)

        grid_pos = to_board_coord(x, y)
        if grid_pos is not None:
            pieces = game.user.alive_pieces
            if self.current_index < len(pieces):
                if game.board.add_piece(grid_pos[0], grid_pos[1], pieces[self.current_index]):
                    self.current_index += 1
                else:
                    print("Failed to place piece")

                if self.current_index == len(pieces):
                    self.start_game_view()
            else:
                raise Exception("Unreachable!")

    def on_key_press(self, symbol: int, modifiers: int):
        # We already started placing pieces
        if self.current_index != 0:
            return

        for index, key in enumerate(range(arcade.key.KEY_1, arcade.key.KEY_9)):
            if index + 1 > PRESET_COUNT:
                # We have reached the maximum number of supported presets
                break
            if key == symbol:
                game.apply_user_preset(index + 1)
                self.start_game_view()

    def start_game_view(self):
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)

    def on_draw(self):
        super().on_draw()
        pieces = game.user.alive_pieces
        arcade.draw_text(
            f'Current piece:',
            SCREEN_WIDTH - (MARGIN_WIDTH / 2),
            SCREEN_HEIGHT - MARGIN_HEIGHT,
            arcade.color.BONE,
            font_size=16,
            anchor_x="center",
            anchor_y="top"
        )
        if self.current_index < len(pieces):
            piece = pieces[self.current_index]
            sprite = sprite_manager.get_user_sprite(piece.name)
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH - (MARGIN_WIDTH / 2),
                SCREEN_HEIGHT - MARGIN_HEIGHT - 70,
                SQUARE_SIZE * 2,
                SQUARE_SIZE * 1.2,
                arcade.color.BONE
            )
            sprite.center_x = SCREEN_WIDTH - (MARGIN_WIDTH / 2)
            sprite.center_y = SCREEN_HEIGHT - MARGIN_HEIGHT - 70
            sprite.draw()

        arcade.draw_text(
            'Press key [num] to select a preset!',
            SCREEN_WIDTH / 2,
            MARGIN_HEIGHT / 2 + 6,
            arcade.color.BONE,
            font_size=16,
            anchor_x='center'
        )
        preset_label = f'Presets: {" ".join([str(x + 1) for x in range(PRESET_COUNT)])}'
        arcade.draw_text(
            preset_label,
            SCREEN_WIDTH / 2,
            MARGIN_HEIGHT / 2 - 20,
            arcade.color.BONE,
            font_size=14,
            anchor_x='center'
        )


class GameViewState(Enum):
    NO_SELECTION = 0,
    PIECE_SELECTED = 1,
    OPPONENT_TURN = 2,
    USER_WIN = 3,
    OPPONENT_WIN = 4,
    STALEMATE = 5

    def __str__(self):
        return self.name


class GameView(BoardView):

    def __init__(self):
        super().__init__()
        self.selected_piece = None
        self.opponents_turn = False
        self.state = GameViewState.NO_SELECTION

    def setup(self):
        super().setup()
        if OPPONENT_PRESET == -1:
            preset = random.randint(1, PRESET_COUNT)
        else:
            preset = OPPONENT_PRESET

        if DEBUG:
            print(f'Applying opponent preset: {preset}')
        game.apply_opponent_preset(preset)
        game.update_moves()

    def on_update(self, delta_time: float):
        match self.state:
            case GameViewState.OPPONENT_TURN:
                opponent_from, opponent_to = game.opponent_turn()
                if game.user.has_flag and not game.opponent.has_flag:
                    self.state = GameViewState.USER_WIN
                elif not game.user.has_flag and game.opponent.has_flag:
                    self.state = GameViewState.OPPONENT_WIN
                elif not game.user.has_flag and not game.opponent.has_flag:
                    self.state = GameViewState.STALEMATE
                else:
                    # Highlight opponent move
                    if opponent_from and opponent_to:
                        self.get_sprite(opponent_from).color = arcade.color.BLUEBERRY
                        self.get_sprite(opponent_to).color = arcade.color.TANGERINE_YELLOW
                    self.state = GameViewState.NO_SELECTION
            case GameViewState.USER_WIN:
                self.window.show_view(WinView())
            case GameViewState.OPPONENT_WIN:
                self.window.show_view(LoseView())
            case GameViewState.STALEMATE:
                self.window.show_view(StalemateView())

    def on_draw(self):
        super().on_draw()
        if self.selected_piece is not None:
            self.debug_msg(f'Piece: {self.selected_piece.coords}')
        else:
            self.debug_msg(f'Piece: None')
        self.debug_msg(f'Current state:')
        self.debug_msg(f'   {self.state}')

        arcade.draw_text(
            f'Captured pieces:',
            SCREEN_WIDTH - (MARGIN_WIDTH / 2),
            SCREEN_HEIGHT + 5 - MARGIN_HEIGHT,
            arcade.color.BONE,
            font_size=16,
            anchor_x="center",
            anchor_y="bottom"
        )

        pieces_names = sprite_manager.sprite_names
        pieces_counts = []
        for name in pieces_names:
            count = 0
            for piece in game.opponent.captured_pieces:
                if piece.name == name:
                    count += 1
            pieces_counts.append(count)
        list_grow_offset = (SQUARE_SIZE * max(0, len(pieces_counts) - pieces_counts.count(0) - 1))
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH - (MARGIN_WIDTH / 2),
            SCREEN_HEIGHT - MARGIN_HEIGHT - (SQUARE_SIZE * 1.2 / 2) - list_grow_offset / 2,
            SQUARE_SIZE * 2,
            SQUARE_SIZE * 1.2 + list_grow_offset,
            arcade.color.BONE
        )
        list_offset = 0
        for index, count in enumerate(pieces_counts):
            if count == 0:
                continue
            sprite = sprite_manager.get_opponent_sprite(pieces_names[index])
            sprite.center_x = SCREEN_WIDTH - (MARGIN_WIDTH / 2) - (SQUARE_SIZE / 8)
            sprite.center_y = SCREEN_HEIGHT - MARGIN_HEIGHT - (SQUARE_SIZE * 1.2 / 2) - (SQUARE_SIZE * list_offset)
            sprite.draw()
            arcade.draw_text(
                f'x{count}',
                SCREEN_WIDTH - (MARGIN_WIDTH / 2) + (SQUARE_SIZE / 2),
                SCREEN_HEIGHT - MARGIN_HEIGHT - (SQUARE_SIZE * 1.2 / 2) - (SQUARE_SIZE * list_offset),
                arcade.color.BLACK_OLIVE,
                font_size=12,
                anchor_x="center",
                anchor_y="top"
            )
            list_offset += 1

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        super().on_mouse_press(x, y, button, modifiers)
        match self.state:
            case GameViewState.NO_SELECTION:
                if self.selected_square is not None:
                    # Try to focus on the piece that may have been selected
                    self.change_focus()
                    if self.selected_piece is not None:
                        # A valid piece was selected!
                        self.state = GameViewState.PIECE_SELECTED
                else:
                    # We still don't have anything selected
                    pass
            case GameViewState.PIECE_SELECTED:
                # If we cancel our selection
                if self.selected_square is None:
                    self.selected_piece = None
                    self.state = GameViewState.NO_SELECTION
                else:
                    # Try to figure out if we made a move
                    piece = self.selected_piece
                    assert (piece is not None)
                    moves = piece.moves
                    if self.selected_square in moves:
                        # Try to move or attack
                        opponent = game.board.is_occupied(self.selected_square[0], self.selected_square[1])
                        if opponent is None:
                            self.selected_piece.move(self.selected_square[0], self.selected_square[1])
                            self.selected_piece = None
                            self.state = GameViewState.OPPONENT_TURN
                        else:
                            self.selected_piece.attack(opponent)
                            self.selected_piece = None
                            self.state = GameViewState.OPPONENT_TURN
                    else:
                        # We may have selected another piece
                        self.change_focus()
                        if self.selected_piece is None:
                            # We did not select another valid piece
                            self.state = GameViewState.NO_SELECTION

            case GameViewState.OPPONENT_TURN:
                # Do nothing
                pass

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.SPACE:
            self.show_hidden = not self.show_hidden

    def change_focus(self):
        piece = game.board.is_occupied(self.selected_square[0], self.selected_square[1])
        if piece is not None and game.user.is_owner(piece):
            self.selected_piece = piece
            self.get_sprite(self.selected_square).color = arcade.color.BLUEBERRY
            moves = piece.moves

            for move in moves:
                self.get_sprite(move).color = arcade.color.RUBY
        else:
            self.selected_piece = None
