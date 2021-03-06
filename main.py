#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Dungeon massacre. A dungeon crawling game

@copyright: 2014 Andrew Conway <nalumc@gmail.com>
@license: TBD

"""

import pygame
from pygame import Rect, Color
from leveldm import *
from random import randint



class Game(object):
    """The main game object."""

    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.pressed_key = None
        self.game_over = False
        self.use_level(Level(self))
        self.score = Score(10, self.level.height*MAP_TILE_HEIGHT)

    def use_level(self, level):
        """Set the level as the current one."""
        self.level = level
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

            x, y = self.level.player.pos
            self.level.player.direction = d
            xnew, ynew = x+DX[d], y+DY[d]
            if not self.level.is_blocking(xnew, ynew):
                self.level.player.animation = self.level.player.walk_animation()
                item=self.level.get_item(xnew, ynew, 'treasure')
                if item is not None:
                    print 'Found treasure: ', item
                    v=[250,500,750,1000]
                    self.score.score+=int(item['treasure'])*v[randint(0,3)]
                    print self.score.score
                    self.level.remove_item(item)
        
        def fight():
            x, y = self.level.player.pos
            d= self.level.player.direction
            x1, y1 = x+DX[d], y+DY[d]
            monster=self.level.get_item(x1, y1,'monster')
            if monster is not None:
                 self.level.remove_item(monster)
                    
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
        elif pressed(pg.K_p):
            print 'All items:'
            self.level.print_debug()
        elif pressed(pg.K_m):
            print 'Monster items:'
            self.level.print_debug('monster')
        self.pressed_key = None

    def main(self):
        """Run the main loop."""

        clock = pygame.time.Clock()
        # Draw the whole screen initially
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.score.image,self.score.rect)

        pygame.display.flip()
        # The main game loop
        while not self.game_over:
            # Clear sprites.
            self.level.sprites.clear(self.screen, self.background)
            self.level.sprites.update()
            # If the player's animation is finished, check for keypresses
            if self.level.player.animation is None:
                self.control()
                self.level.player.update()
			#lines related to shadows removed
            dirty_rects = self.level.sprites.draw(self.screen)

            # Update the dirty areas of the screen
            if self.score.update():
                self.screen.fill(self.score.background_color,self.score.rect)
                self.screen.blit(self.score.image,self.score.rect)
                dirty_rects.append(self.score.rect)
            pygame.display.update(dirty_rects)
            # Wait for one tick of the game clock
            clock.tick(30)
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
