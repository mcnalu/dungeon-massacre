import ConfigParser
import pygame
import pygame.locals as pg
from graphicsdm import *

class Level(object):
    """Load and store the map of the level, together with all the items."""

    def __init__(self, game, filename="level.map"):
        self.game=game
        self.tileset = ''
        self.map = {}
        self.key = {}
        self.width = 0
        self.height = 0
        self.sprites = pygame.sprite.RenderUpdates()
        items=self.load_file(filename)
        # Populate the game with the level's objects and monsters
        for item in items:
            if item.get("player") in ('true', '1', 'yes', 'on'):
                sprite = Player(game, item)
                self.player = sprite
            else:
                sprite = Sprite(game, item, SPRITE_CACHE[item["sprite"]])
            self.sprites.add(sprite)
            item['sprite_obj']=sprite
            if item['name']=='skeleton':
                self.skelly=sprite

    def load_file(self, filename="level.map"):
        """Load the level from specified file."""

        parser = ConfigParser.ConfigParser()
        parser.read(filename)
        self.tileset = parser.get("level", "tileset")
        smap = parser.get("level", "map").split("\n")
        for section in parser.sections():
            if len(section) == 1:
                desc = dict(parser.items(section))
                self.key[section] = desc
        self.width = len(smap[0])
        self.height = len(smap)
        items = []
        for y, line in enumerate(smap):
            for x, c in enumerate(line):
                self.map[(x, y)]=c
                if not self.is_wall(x, y) and 'sprite' in self.key[c]:
                    item=self.key[c].copy()
                    item['init_pos']=(x, y)
                    items.append(item)
                    self.map[(x, y)]='.'
        return items

    def render(self):
        """Draw the level on the surface."""

        wall = self.is_wall
        tiles = MAP_CACHE[self.tileset]
        image = pygame.Surface((self.width*MAP_TILE_WIDTH, self.height*MAP_TILE_HEIGHT))
        for map_x in range(0, self.width):
            for map_y in range(0, self.height):
                if wall(map_x, map_y):
                    # Draw different tiles depending on neighbourhood
                    if wall(map_x, map_y+1): #wall below
                        if wall(map_x, map_y-1): #wall below and above
                            if wall(map_x+1, map_y) and wall(map_x-1, map_y):
                                tile = 0, 1
                            elif wall(map_x+1, map_y):
                                tile = 0, 0
                            elif wall(map_x-1, map_y):
                                tile = 1, 0
                            else: #walls below and above only
                                tile = 0, 2
                        else: #wall below, no wall above
                            if wall(map_x+1, map_y) and wall(map_x-1, map_y):
                                tile = 1, 1
                            elif wall(map_x-1, map_y):
                                tile = 2, 1
                            elif wall(map_x+1, map_y):
                                tile = 3, 1
                            else: #wall below only
                                tile = 1, 2                       
                    else: #no wall below
                        if wall(map_x, map_y-1): #no wall below, wall above 
                            if wall(map_x+1, map_y) and wall(map_x-1, map_y):
                                tile = 0, 3
                            elif wall(map_x+1, map_y):
                                tile = 2, 0 #need to fix
                            elif wall(map_x-1, map_y):
                                tile = 3, 0 #need to fix                               
                            else: #wall above only
                                tile = 3, 2
                        else: #no wall below, no wall above
                            if wall(map_x+1, map_y) and wall(map_x-1, map_y):
                                tile = 1, 3
                            elif wall(map_x-1, map_y):
                                tile = 2, 3
                            elif wall(map_x+1, map_y):
                                tile = 3, 3
                            else:
                                tile = 2, 2
                else:
                    c = self.map[(map_x, map_y)]
                    try:
                        tile = self.key[c]['tile'].split(',')
                        tile = int(tile[0]), int(tile[1])
                    except (ValueError, KeyError):
                        # Default to ground tile
                        tile = 0, 4
                tile_image = tiles[tile[0]][tile[1]]
                image.blit(tile_image,
                           (map_x*MAP_TILE_WIDTH, map_y*MAP_TILE_HEIGHT))
        return image

    def get_tile(self, x, y):
        """Tell what's at the specified position of the map."""
        item = self.get_item(x, y)
        if item is not None:
            return item
        try:
            char = self.map[(x, y)]
        except IndexError:
            return {}
        try:
            return self.key[char]
        except KeyError:
            return {}

    def get_bool(self, x, y, name):
        """Tell if the specified flag is set for position on the map."""

        value = self.get_tile(x, y).get(name)
        return value in (True, 1, 'true', 'yes', 'True', 'Yes', '1', 'on', 'On')

    def is_wall(self, x, y):
        """Is there a wall?"""
        if x<0 or x>=self.width or y<0 or y>=self.height:
            return True

        return self.get_bool(x, y, 'wall')

    def is_blocking(self, x, y):
        """Is this place blocking movement?"""

        if not 0 <= x < self.width or not 0 <= y < self.height:
            return True
        return self.get_bool(x, y, 'block')

    def get_item(self, x, y):
        """Interacts with an item, if present."""

        for s in self.sprites:
            if s.pos==(x, y):
                return s.item
        return None
            
    def remove_item(self, item):
        self.sprites.remove(item['sprite_obj'])
