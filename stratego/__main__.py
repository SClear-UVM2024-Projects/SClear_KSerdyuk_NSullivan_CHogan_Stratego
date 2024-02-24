import arcade
from views import IntroView
from config import config

window = arcade.Window(config['window']['width'], config['window']['height'], config['window']['title'])
intro_view = IntroView()
window.show_view(intro_view)
arcade.run()
