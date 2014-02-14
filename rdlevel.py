
"""

Level loading and tileset code based on qq demo
https://bitbucket.org/thesheep/qq/overview
by Radomir Dopieralski <qq@sheep.art.pl>

@copyright: 2014 Andrew Conway <nalumc@gmail.com>
@license: BSD, see COPYING for details

"""

import ConfigParser

import pygame
import pygame.locals as pg

# Dimensions of the map tiles
MAP_TILE_WIDTH, MAP_TILE_HEIGHT = 24, 32

# Motion offsets for particular directions
#     N  E  S   W
DX = [0, 1, 0, -1]
DY = [-1, 0, 1, 0]

class TileCache(object):
    """Load the tilesets lazily into global cache"""

    def __init__(self,  width=32, height=None):
        self.width = width
        self.height = height or width
        self.cache = {}

    def __getitem__(self, filename):
        """Return a table of tiles, load it from disk if needed."""

        key = (filename, self.width, self.height)
        try:
            return self.cache[key]
        except KeyError:
            tile_table = self._load_tile_table(filename, self.width,
                                               self.height)
            self.cache[key] = tile_table
            return tile_table

    def _load_tile_table(self, filename, width, height):
        """Load an image and split it into tiles."""
        try:
            image = pygame.image.load(filename)
        except:
            image = pygame.image.load('missing.png')
        image = image.convert_alpha()
        image_width, image_height = image.get_size()
        tile_table = []
        for tile_x in range(0, image_width/width):
            line = []
            tile_table.append(line)
            for tile_y in range(0, image_height/height):
                rect = (tile_x*width, tile_y*height, width, height)
                line.append(image.subsurface(rect))
        return tile_table

SPRITE_CACHE = TileCache()
MAP_CACHE = TileCache(MAP_TILE_WIDTH, MAP_TILE_HEIGHT)
TILE_CACHE = TileCache(32, 32)

class Sprite(pygame.sprite.Sprite):
    """Sprite for animated items and base class for Player."""

    is_player = False

    def __init__(self, pos=(0, 0), frames=None):
        super(Sprite, self).__init__()
        if frames:
            self.frames = frames
        self.image = self.frames[0][0]
        self.rect = self.image.get_rect()
        self.animation = self.stand_animation()
        self.pos = pos

    def _get_pos(self):
        """Check the current position of the sprite on the map."""

        return (self.rect.midbottom[0]-12)/24, (self.rect.midbottom[1]-32)/32

    def _set_pos(self, pos):
        """Set the position and depth of the sprite on the map."""

        self.rect.midbottom = pos[0]*24+12, pos[1]*32+32
        self.depth = self.rect.midbottom[1]

    pos = property(_get_pos, _set_pos)

    def move(self, dx, dy):
        """Change the position of the sprite on screen."""

        self.rect.move_ip(dx, dy)
        self.depth = self.rect.midbottom[1]

    def stand_animation(self):
        """The default animation."""

        while True:
            # Change to next frame every two ticks
            for frame in self.frames[0]:
                self.image = frame
                yield None
                yield None

    def update(self, *args):
        """Run the current animation."""

        self.animation.next()

class Player(Sprite):
    """ Display and animate the player character."""

    is_player = True

    def __init__(self, pos=(1, 1)):
        self.frames = SPRITE_CACHE["player.png"]
        Sprite.__init__(self, pos)
        self.direction = 2
        self.animation = None
        self.image = self.frames[self.direction][0]

    def walk_animation(self):
        """Animation for the player walking."""

        # This animation is hardcoded for 4 frames and 24x32 map tiles
        for frame in range(4):
            self.image = self.frames[self.direction][frame]
            yield None
            self.move(3*DX[self.direction], 4*DY[self.direction])
            yield None
            self.move(3*DX[self.direction], 4*DY[self.direction])

    def update(self, *args):
        """Run the current animation or just stand there if no animation set."""

        if self.animation is None:
            self.image = self.frames[self.direction][0]
        else:
            try:
                self.animation.next()
            except StopIteration:
                self.animation = None

class Score(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 20)
        #self.font.set_italic(1)
        self.color = pygame.Color('white')
        self.lastscore = -1
        self.score=0
        self.update()
        self.rect = self.image.get_rect().move(x, y)

    def update(self):
        if self.score != self.lastscore:
            self.lastscore = self.score
            msg = "Score: %d" % self.score
            self.image = self.font.render(msg, 0, self.color)


class Level(object):
    """Load and store the map of the level, together with all the items."""

    def __init__(self, filename="level.map"):
        self.tileset = ''
        self.map = []
        self.items = {}
        self.key = {}
        self.width = 0
        self.height = 0
        self.load_file(filename)

    def load_file(self, filename="level.map"):
        """Load the level from specified file."""

        parser = ConfigParser.ConfigParser()
        parser.read(filename)
        self.tileset = parser.get("level", "tileset")
        self.map = parser.get("level", "map").split("\n")
        for section in parser.sections():
            if len(section) == 1:
                desc = dict(parser.items(section))
                self.key[section] = desc
        self.width = len(self.map[0])
        self.height = len(self.map)
        for y, line in enumerate(self.map):
            for x, c in enumerate(line):
                if not self.is_wall(x, y) and 'sprite' in self.key[c]:
                    self.items[(x, y)] = self.key[c]

    def render(self):
        """Draw the level on the surface."""

        wall = self.is_wall
        tiles = MAP_CACHE[self.tileset]
        image = pygame.Surface((self.width*MAP_TILE_WIDTH, self.height*MAP_TILE_HEIGHT))
        for map_y, line in enumerate(self.map):
            for map_x, c in enumerate(line):
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

        try:
            char = self.map[y][x]
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

        if (x, y) in self.items:
            return self.items[(x,y)]
            
    def remove_item(self, x, y):
        del self.items[(x,y)]
                    

