from arcade import Sprite
import json

from config import config


class SpriteManager:

    def __init__(self):
        self._opponent_sprites = {}
        self._user_sprites = {}
        with open(config['sprites']['data_file'], 'r') as file:
            unit_info = json.load(file)

        for table in unit_info:
            self._opponent_sprites[table['name']] = Sprite(filename=table['sprite_opponent'])
            self._user_sprites[table['name']] = Sprite(filename=table['sprite_user'])

    def resize_sprites(self, size: int):
        for sprite in self._user_sprites.values():
            sprite.width = size
            sprite.height = size

        for sprite in self._opponent_sprites.values():
            sprite.width = size
            sprite.height = size

    def get_user_sprite(self, name: str) -> Sprite:
        # We only deal with valid sprite names
        assert (name in self._user_sprites)

        return self._user_sprites[name]

    def get_opponent_sprite(self, name: str) -> Sprite:
        assert (name in self._opponent_sprites)
        return self._opponent_sprites[name]

    @property
    def sprite_names(self) -> list[str]:
        return [x for x in self._user_sprites.keys()]


# I love globally constructed classes
sprite_manager = SpriteManager()
