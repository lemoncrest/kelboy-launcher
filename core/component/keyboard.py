import os

import pygame

from core.settings import *

import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, "log.txt"),level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Keyboard(pygame.sprite.Sprite):

    def __init__(self, game):

        self.game = game
        self._layer = 6
        game.all_sprites = pygame.sprite.LayeredUpdates()
        pygame.sprite.Sprite.__init__(self, game.all_sprites)
        self.font = pygame.font.SysFont('Consolas', 30)
        self.image = pygame.Surface((width,height*0.5))
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect()

        self.rect.centery = height - (height / 4)
        self.rect.centerx = width / 2
        self.keys = [
            ["q","w","e","r","t","y","u","i","o","p"],
            ["a","s","d","f","g","h","j","k","l","@"],
            ["z","x","c","v","b","n","m",",",".","-"]
        ]



    def draw(self):
        counter = 0
        for x in range(0,len(self.keys)):
            logger.debug("x")
            counter = 0
            for y in range(0,len(self.keys[0])):
                logger.debug("y")
                counter += 1
                text_item = self.font.render(self.keys[x][y], True, (255,255,255))
                text_item_rect = text_item.get_rect()
                logger.debug(self.keys[x][y])
                self.game.screen.blit(text_item, (self.game.menu.cursor.rect.left * 1.2, self.rect.y + (text_item_rect.height * counter)))
