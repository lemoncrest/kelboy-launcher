import os

import pygame
import pygame.gfxdraw
from pygame.locals import * #Rect f.i.

from core.settings import *
from core.colorpalette import RGBColors

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
        self.image.fill(RGBColors().blue)

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
        #refresh
        logger.debug("position: X %s Y %s" % (self.positionX,self.positionY))

        self.image.fill(RGBColors().blue)
        counter = 0
        for x in range(0,len(self.keys)):
            counter = 0
            for y in range(0,len(self.keys[0])):
                #logger.debug(self.keys[x][y]) #key drawn

                textsurface = self.font.render(self.keys[x][y], True, RGBColors().white)

                image = pygame.Surface((30, 30))

                rect = image.get_rect(x=10+(30*y), y=30*x)

                if y==self.positionX and x == self.positionY:
                    #draw selector
                    rect2 = image.get_rect(x=10+(30*y), y=30*x)
                    pygame.draw.rect(self.image, RGBColors().navy, rect2)


                pygame.draw.rect(self.image, RGBColors().white, rect, width=1)
                self.image.blit(textsurface, (21+(30*y) , 10+(30*x)))


        #now specials
        for x in range(0,len(self.specials)):

            special = self.specials[x]
            image = pygame.Surface((60, 30))
            rect = image.get_rect(x=10+(60*x), y=90)
            pygame.draw.rect(self.image, RGBColors().white, rect, width=1)

            if self.positionY>=len(self.keys) and self.positionX > 4:
                self.positionX = 4

            if x==self.positionX and 3 == self.positionY:
                #draw selector
                rect2 = image.get_rect(x=10+(30*x*2), y=30*3)
                pygame.draw.rect(self.image, RGBColors().navy, rect2)


            textsurface = self.font.render(special["name"], True, RGBColors().white)
            self.image.blit(textsurface, (18+(60*x), 90+10) )
