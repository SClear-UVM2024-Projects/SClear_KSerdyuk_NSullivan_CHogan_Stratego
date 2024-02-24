import arcade
CAPTURED_START_X = 362
CAPTURED_START_Y = 620
DEFAULT_FONT_SIZE = 18

if __name__ == "__main__":
    array = ["S", "S", "B"]
    captured = f"Ally Soldiers: {array}"
    # Code for Python Arcade
    arcade.draw_text(captured, CAPTURED_START_X, CAPTURED_START_Y, arcade.color.BLACK_BEAN, DEFAULT_FONT_SIZE,
                     font_name="Kenney Blocks")
    print(captured)
