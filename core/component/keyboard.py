import os

import pygame
import pygame.gfxdraw
from pygame.locals import * #Rect f.i.

from core.settings import *
from core.colorpalette import RGBColors

import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, "log.txt"),level=logging.DEBUG)
logger = logging.getLogger(__name__)

class KeyboardScreen(pygame.sprite.Sprite):
    def __init__(self, game):

        all_sprites = pygame.sprite.LayeredUpdates()

        pygame.sprite.Sprite.__init__(self, game.all_sprites)
        self.image = pygame.Surface((width, 30))

        self.image.fill(RGBColors().navy)
        self.rect = self.image.get_rect()
        self.rect.center = (width / 2,height/4)
        self.font = pygame.font.SysFont('Consola', 30)

    def draw(self,text):
        self.image.fill(RGBColors().blue)

        textsurface = self.font.render(text, True, RGBColors().white)
        self.image.blit(textsurface, (2,2) )




class Keyboard(pygame.sprite.Sprite):

    def __init__(self, game, buffer=""):
        self.show = True
        self.positionX = 0
        self.positionY = 0

        self.buffer = buffer
        self.symb = False
        self.shift = False

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
            ["a","s","d","f","g","h","j","k","l","ñ"],
            ["z","x","c","v","b","n","m",",",".","-"]
        ]
        self.mayus = [
            ["Q","W","E","R","T","Y","U","I","O","P"],
            ["A","S","D","F","G","H","J","K","L","Ñ"],
            ["Z","X","C","V","B","N","M",",",".","-"]
        ]
        self.symbols = [
            ["!","\"","·","$","%","&","/","(",")","="],
            ["[","]","\\","|","@","#","~","¬","?","¿"],
            ["^","`","*","+","¨","´","{","}","<",">",""]
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
            }
        ]



    def draw(self):
        #refresh
        logger.debug("position: X %s Y %s" % (self.positionX, self.positionY))

        self.image.fill(RGBColors().blue)
        counter = 0
        for x in range(0,len(self.keys)):
            counter = 0
            for y in range(0,len(self.keys[0])):
                #logger.debug(self.keys[x][y]) #key draw
                if self.symb:
                    target = self.symbols[x][y]
                else:
                    if self.shift:
                        target = self.mayus[x][y]
                    else:
                        target = self.keys[x][y]
                textsurface = self.font.render(target, True, RGBColors().white)

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
