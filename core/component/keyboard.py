import os

import pygame
import pygame.gfxdraw
from pygame.locals import * #Rect f.i.

from core.settings import *

import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, "log.txt"),level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Keyboard(pygame.sprite.Sprite):

    def __init__(self, game):
        self.positionX = 0
        self.positionY = 0

        self.game = game
        self._layer = 6

        game.all_sprites = pygame.sprite.LayeredUpdates()
        pygame.sprite.Sprite.__init__(self, game.all_sprites)
        #font
        self.font = pygame.font.SysFont('Arial', 20)
        #keyboard
        self.image = pygame.Surface((width,height*0.5))
        self.image.fill((0,200,200))

        self.rect = self.image.get_rect()
        self.rect.centery = height - (height / 4)
        self.rect.centerx = width / 2
        self.keys = [
            ["q","w","e","r","t","y","u","i","o","p"],
            ["a","s","d","f","g","h","j","k","l","@"],
            ["z","x","c","v","b","n","m",",",".","-"]
        ]
        self.specials = [
            {
                "name" : "MAYUS"
            },{
                "name" : "SYMB"
            },{
                "name" : "SPACE"
            },{
                "name" : "ENTER"
            },{
                "name" : "EXIT"
            },
        ]



    def draw(self):
        counter = 0
        for x in range(0,len(self.keys)):
            logger.debug("X:")
            counter = 0
            for y in range(0,len(self.keys[0])):
                logger.debug(self.keys[x][y]) #key drawn

                textsurface = self.font.render(self.keys[x][y], True, (255,0,0))

                image = pygame.Surface((30, 30))

                rect = image.get_rect(x=10+(30*y), y=30*x)

                pygame.draw.rect(self.image, (255,255,255), rect, width=1)
                self.image.blit(textsurface, (23+(30*y) , 10+(30*x)))

        #now specials
        for x in range(0,len(self.specials)):

            special = self.specials[x]
            image = pygame.Surface((60, 30))
            rect = image.get_rect(x=10+(60*x), y=90)
            pygame.draw.rect(self.image, (200,200,200), rect, width=1)
            textsurface = self.font.render(special["name"], True, (255,0,0))

            self.image.blit(textsurface, (18+(60*x), 90+10) )
