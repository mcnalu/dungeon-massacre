#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Dungeon massacre. A dungeon crawling game

@copyright: 2014 Andrew Conway <nalumc@gmail.com>
@license: TBD

"""

from rdlevel import *
from random import randint
from pygame import Rect, Color



class Game(object):
    """The main game object."""

    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.pressed_key = None
        self.game_over = False
        #several removed lines
        self.sprites = pygame.sprite.RenderUpdates()
        self.use_level(Level())
        self.score = Score(10,10) #self.level.height*MAP_TILE_HEIGHT)
        self.sprites.add(self.score)

    def use_level(self, level):
        """Set the level as the current one."""

        #several removed lines
        self.sprites = pygame.sprite.RenderUpdates()
        self.level = level
        # Populate the game with the level's objects
        for pos, item in level.items.iteritems():
            if item.get("player") in ('true', '1', 'yes', 'on'):
                sprite = Player(self, item, pos)
                self.player = sprite
            else:
                sprite = Sprite(self, item, pos, SPRITE_CACHE[item["sprite"]])
            self.sprites.add(sprite)
            item['sprite_obj']=sprite

        # Render the level map
        self.background = self.level.render()

    def control(self):
        """Handle the controls of the game."""

        keys = pygame.key.get_pressed()

        def pressed(key):
            """Check if the specified key is pressed."""

            return self.pressed_key == key or keys[key]

        def walk(d):
            """Start walking in specified direction."""

            x, y = self.player.pos
            self.player.direction = d
            xnew, ynew = x+DX[d], y+DY[d]
            if not self.level.is_blocking(xnew, ynew):
                self.player.animation = self.player.walk_animation()
                item=self.level.get_item(xnew, ynew)
                if self.take_treasure(item):
                    print 'Found treasure: ', item
                    self.level.remove_item(xnew, ynew)
                    self.sprites.remove(item['sprite_obj'])
        
        def fight():
            x, y = self.player.pos
            d= self.player.direction
            x1, y1 = x+DX[d], y+DY[d]
            item=self.level.get_item(x1, y1)
            if item is not None and 'monster' in item:
                 self.level.remove_item(x1, y1)
                 self.sprites.remove(item['sprite_obj'])               
                    
        if pressed(pg.K_UP):
            walk(0)
        elif pressed(pg.K_DOWN):
            walk(2)
        elif pressed(pg.K_LEFT):
            walk(3)
        elif pressed(pg.K_RIGHT):
            walk(1)
        elif pressed(pg.K_SPACE):
            fight()
        self.pressed_key = None

    def take_treasure(self,item):
        try:
            name,level = item['name'].split('-')
        except:
            return False
        v=[250,500,750,1000]
        self.score.score+=int(level)*v[randint(0,3)]
        print self.score.score
        return True

    def main(self):
        """Run the main loop."""

        clock = pygame.time.Clock()
        # Draw the whole screen initially
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()
        # The main game loop
        while not self.game_over:
            # Clear sprites.
            self.sprites.clear(self.screen, self.background)
            self.sprites.update()
            # If the player's animation is finished, check for keypresses
            if self.player.animation is None:
                self.control()
                self.player.update()
			#lines related to shadows removed
            dirty = self.sprites.draw(self.screen)

            # Update the dirty areas of the screen
            pygame.display.update(dirty)

            
            # Wait for one tick of the game clock
            clock.tick(15)
            # Process pygame events
            for event in pygame.event.get():
                if event.type == pg.QUIT:
                    self.game_over = True
                elif event.type == pg.KEYDOWN:
                    self.pressed_key = event.key
                    
if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((1000, 320))
    Game().main()
