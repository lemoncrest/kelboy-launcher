import os

import pygame
import pygame.gfxdraw
from pygame.locals import * #Rect f.i.

from core.settings import *
from core.colors import *

import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=logging.DEBUG)
logger = logging.getLogger(__name__)

class KeyboardScreen(pygame.sprite.Sprite):
    def __init__(self, main):

        all_sprites = pygame.sprite.LayeredUpdates()

        pygame.sprite.Sprite.__init__(self, main.all_sprites)
        self.image = pygame.Surface((WIDTH, 30))

        self.image.fill(NAVY)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2,HEIGHT/4)
        self.font = pygame.font.Font(FONT_TYPE_KEYBOARDBAR, FONT_SIZE)

    def draw(self,text):
        self.image.fill(BLUE)

        textsurface = self.font.render(text, True, WHITE)
        self.image.blit(textsurface, (2,2) )




class Keyboard(pygame.sprite.Sprite):

    MAYUS = "MAY"
    SYMB = "SYM"
    SPACE = "SPA"
    ENTER = "ENT"
    BACK = "BCK"
    EXIT = "EXT"

    def __init__(self, main, buffer="",loadMenu=True):
        self.show = True
        self.loadMenu = loadMenu
        self.positionX = 0
        self.positionY = 0

        self.buffer = buffer
        self.symb = False
        self.shift = False

        self.main = main
        self._layer = 6

        main.all_sprites = pygame.sprite.LayeredUpdates()
        pygame.sprite.Sprite.__init__(self, main.all_sprites)
        #font
        self.font = pygame.font.Font(FONT_TYPE_KEYBOARD, FONT_SIZE)
        #keyboard
        self.image = pygame.Surface((WIDTH,HEIGHT*0.5))
        self.image.fill(BLUE)

        self.rect = self.image.get_rect()
        self.rect.centery = HEIGHT - (HEIGHT / 4)
        self.rect.centerx = WIDTH / 2
        self.keys = [
            ["q","w","e","r","t","y","u","i","o","p"],
            ["a","s","d","f","g","h","j","k","l","ñ"],
            ["z","x","c","v","b","n","m",",",".","-"]
        ]
        self.mayus = [
            ["Q","W","E","R","T","Y","U","I","O","P"],
            ["A","S","D","F","G","H","J","K","L","Ñ"],
            ["Z","X","C","V","B","N","M",";",":","_"]
        ]
        self.symbols = [
            ["0","1","2","3","4","5","6","7","8","9","+"],
            ["!","\"","·","$","%","&","/","(",")","="],
            ["[","]","\\","|","@","#","<",">","?","¿"]
        ]
        self.specials = [
            {
                "name" : Keyboard.MAYUS
            },{
                "name" : Keyboard.SYMB
            },{
                "name" : Keyboard.SPACE
            },{
                "name" : Keyboard.ENTER
            },{
                "name" : Keyboard.BACK
            },{
                "name" : Keyboard.EXIT
            }
        ]



    def draw(self):
        #refresh
        logger.debug("position: X %s Y %s" % (self.positionX, self.positionY))

        self.image.fill(BLUE)
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
                textsurface = self.font.render(target, True, WHITE)

                image = pygame.Surface((30, 30))

                rect = image.get_rect(x=10+(30*y), y=30*x)

                if y==self.positionX and x == self.positionY:
                    #draw selector
                    rect2 = image.get_rect(x=10+(30*y), y=30*x)
                    pygame.draw.rect(self.image, NAVY, rect2)
                else:
                    pygame.draw.rect(self.image, BLUE, rect) #pygame 1.9.4 has not width=1 param
                self.image.blit(textsurface, (21+(30*y) , 10+(30*x)))


        #now specials
        for x in range(0,len(self.specials)):

            special = self.specials[x]
            image = pygame.Surface((WIDTH/len(self.specials), 30))
            rect = image.get_rect(x=(WIDTH/len(self.specials)*x), y=90)
            pygame.draw.rect(self.image, BLUE, rect) #pygame 1.9.4 has not width=1 param

            if self.positionY>=len(self.keys) and self.positionX > len(self.specials)-1:
                self.positionX = len(self.specials)-1

            if x==self.positionX and 3 == self.positionY:
                #draw selector
                rect2 = image.get_rect(x=(WIDTH/len(self.specials)*x), y=30*3)
                pygame.draw.rect(self.image, NAVY, rect2)


            textsurface = self.font.render(special["name"], True, WHITE)
            self.image.blit(textsurface, ((WIDTH/len(self.specials)*x), 90+10) )
