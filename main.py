#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Dungeon massacre. A dungeon crawling game

@copyright: 2014 Andrew Conway <nalumc@gmail.com>
@license: TBD

"""

from rdlevel import *

class Game(object):
    """The main game object."""

    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.pressed_key = None
        self.game_over = False
        #several removed lines
        self.sprites = pygame.sprite.RenderUpdates()
        self.use_level(Level())

    def use_level(self, level):
        """Set the level as the current one."""

        #several removed lines
        self.sprites = pygame.sprite.RenderUpdates()
        self.level = level
        # Populate the game with the level's objects
        for pos, tile in level.items.iteritems():
            if tile.get("player") in ('true', '1', 'yes', 'on'):
                sprite = Player(pos)
                self.player = sprite
            else:
                sprite = Sprite(pos, SPRITE_CACHE[tile["sprite"]])
            self.sprites.add(sprite)

        # Render the level map
        self.background = self.level.render()

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
			#several removed lines
			
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
