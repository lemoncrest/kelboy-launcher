import os
import pygame

from core.colors import *
from core.settings import *

import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, "log.txt"),level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Dialog(pygame.sprite.Sprite):

    def __init__(self,menu,main,dialogWidth=0,dialogHeight=0,title="Dialog title",message="Dialog message",options=[],fontSize = 30):

        self.main = main
        self.width = dialogWidth
        self.height = dialogWidth

        self.padding = 10
        self.margin = 50
        self.title = title
        self.message = message

        self._layer = 11

        self.groups = self.main.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(NAVY)
        self.font = pygame.font.SysFont('Arial', fontSize)

        self.rect = self.image.get_rect()
        self.rect.centery = height / 2
        self.rect.centerx = width / 2

        #fix for big title
        if (self.font.size(self.title)[0]) > self.width:
            self.width = (self.font.size(self.title)[0])+(self.padding*2)
        #fix for big message
        if (self.font.size(self.message)[0]) > self.width:
            self.width = (self.font.size(self.message)[0])+(self.padding*2)

        #fix for too litle height
        if (self.font.size(self.title)[1] + self.margin)*3 > self.height:
            self.height = (self.font.size(self.title)[1] + self.margin)*3

        self.options = options
        self.active = False

        self.button_part = self.height/4
        self.button_height = self.button_part-(self.padding*2)

        #calculate centered rectangle
        self.y = (height - self.height) / 2

        self.focus_margin = 3  # TODO calculate


    def draw(self,focus=0):

        self.active = True

        #now title part
        title_height = (self.font.size(self.title)[1])+(self.padding*2)

        dialog_rect = pygame.Rect(self.padding, self.padding, self.width-(self.padding*2), title_height)
        pygame.draw.rect(self.image, GRAY, dialog_rect, 0)

        xT = (self.width/2) - ((self.font.size(self.title)[0]) / 2)
        yT = self.y + (title_height/2)

        txt = self.font.render(self.title, True, BLACK)
        self.image.blit(txt, (xT, yT) )

        yT2 = self.y + (self.height*2/5)
        xT2 = (self.width/2) - ((self.font.size(self.message)[0]) / 2) #TODO, break lines

        txt2 = self.font.render(self.message, True, BLACK)
        self.image.blit(txt2, (xT2, yT2))

        if self.options is not None and len(self.options)>0:
            # draw each option
            for i in range(0,len(self.options)):
                option = self.options[i]
                rectangle = self.drawButton(message=option["title"],max=len(self.options),figure=i+1,focus=(focus==i))
                self.options[i]["rectangle"] = rectangle

        else: #draw an ok
            self.options = []
            self.options[0] = {
                "title" : "ok"
            }
            rectangle = self.drawButton(message=self.options[0]["title"])
            self.options[0]["rectangle"] = rectangle

        return self.options

    def drawButton(self,message,max=1,figure=1,focus=False):

        button_width = self.font.size(message)[1] + (self.margin * 2)

        xT3 = ((((self.width/2) / max)) * figure * 2) - (button_width/2) - ((((self.width/2) / max)) )

        yT3 = self.y + self.height - self.button_part
        button_rect = pygame.Rect(xT3, yT3, button_width, self.button_height)
        pygame.draw.rect(self.image, BLACK, button_rect, 0)

        if focus:
            focus_rect = pygame.Rect(xT3+self.focus_margin, yT3+self.focus_margin, button_width-(self.focus_margin*2), self.button_height-(self.focus_margin*2))
            pygame.draw.rect(self.image, DARK_GRAY, focus_rect, 0)

        txtMessage = self.font.render(message, True, WHITE)
        self.image.blit(txtMessage, (xT3-(self.font.size(message)[0]/2) + (button_width/2) , yT3-(self.font.size(message)[1]/2) + self.button_height/2) )

        return button_rect
