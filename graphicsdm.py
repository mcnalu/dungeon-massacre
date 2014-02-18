
"""

Level loading and tileset code based on qq demo
https://bitbucket.org/thesheep/qq/overview
by Radomir Dopieralski <qq@sheep.art.pl>

@copyright: 2014 Andrew Conway <nalumc@gmail.com>
@license: BSD, see COPYING for details

"""

import pygame
import pygame.locals as pg
from random import randint

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

    def __init__(self, game, item, frames=None):
        super(Sprite, self).__init__()
        self.game=game
        self.item=item
        if frames:
            self.frames = frames
        self.image = self.frames[0][0]
        self.rect = self.image.get_rect()
        self.animation = self.stand_animation()
        self.pos = item['init_pos']
        self.direction=-1
        self.auto_step=0
        self.auto_total=0

    def _get_pos(self):
        """Check the current position of the sprite on the map."""

        return (self.rect.midbottom[0]-12)/24, (self.rect.midbottom[1]-32)/32

    def _set_pos(self, pos):
        """Set the position and depth of the sprite on the map."""

        self.rect.midbottom = pos[0]*24+12, pos[1]*32+32
        self.depth = self.rect.midbottom[1]

    pos = property(_get_pos, _set_pos)

    def auto_move(self):
        if self.direction>=0:
            self.move(3*DX[self.direction], 4*DY[self.direction])
            self.auto_step-=1
            self.auto_total+=1
            if self.auto_step==0:
                self.direction=-1

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
                self.auto_move()
                yield None
                self.auto_move()

    def update(self, *args):
        """Run the current animation."""
        
        self.animation.next()
        if 'monster' in self.item and self.direction==-1:
            d=-1
            p=self.game.level.player
            other_monster=self.game.level.get_item(self.pos[0],self.pos[1], 'monster', [self.item])
            if self.pos==p.pos:
                d=randint(0,3)
            elif other_monster is not None:
                d=randint(0,3)
            elif self.is_adjacent(p):
                self.game.score.health-=1
            elif self.get_distance(p)<6:
                d=self.get_direction_to(p)
            if d>=0:
                xnew, ynew = self.pos[0]+DX[d], self.pos[1]+DY[d]
                if not self.game.level.is_blocking(xnew, ynew):
                    self.direction=d
                    self.auto_step=8
    
    def get_direction_to(self, other):
        if abs(other.pos[0]-self.pos[0])>=abs(other.pos[1]-self.pos[1]):
            if other.pos[0]<self.pos[0]:
                d=3
            else:
                d=1
        else:
            if other.pos[1]<self.pos[1]:
                d=0
            else:
                d=2
        return d
                 
    def get_distance(self, other):
        return abs(other.pos[0]-self.pos[0])+abs(other.pos[1]-self.pos[1])
                
    def is_adjacent(self, other):
        if self.get_distance(other)<=1:
            return True
        else:
            return False

class Player(Sprite):
    """ Display and animate the player character."""

    is_player = True

    def __init__(self, game, item):
        self.frames = SPRITE_CACHE["player.png"]
        Sprite.__init__(self, game, item)
        self.direction = 2
        self.animation = None
        self.image = self.frames[self.direction][0]

    def walk_animation(self):
        """Animation for the player walking."""

        # This animation is hardcoded for 4 frames and 24x32 map tiles
        for frame in range(4):
            self.image = self.frames[self.direction][frame]
            yield None
            self.auto_move()
            yield None
            self.auto_move()

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
        self.x, self.y = x, y
        self.font = pygame.font.Font(None, 20)
        self.color = pygame.Color('white')
        self.background_color = pygame.Color('black')
        self.last_score = -1
        self.score=0
        self.last_health = 100
        self.health= 100
        self.rect=pygame.Rect(x,y,0,0)
        self.update()

    def update(self):
        update=False
        if self.score != self.last_score:
            self.last_score = self.score
            update = True
        if self.health != self.last_health:
            self.last_heath = self.health
            update = True
        if update:
            msg = "Score: %6d   Health: %3d" % (self.score, self.health)
            self.image = self.font.render(msg, 0, self.color,self.background_color)
            self.rect = self.rect.union(self.image.get_rect().move(self.x, self.y))
        return update




                    

