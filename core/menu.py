import os
import json
import pygame
from core.settings import *
from core.component.keyboard import Keyboard

import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, "log.txt"),level=logging.DEBUG)
logger = logging.getLogger(__name__)

from core.effect.pixelate import pixelate


class MenuBoard(pygame.sprite.Sprite):

    def __init__(self, game):
        self.game = game
        self.groups = game.all_sprites
        self._layer = 1
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = pygame.Surface((width,height))
        self.image.fill((0,255,255))
        self.rect = self.image.get_rect()
        self.rect.centery = height / 2
        self.rect.centerx = width / 2
        filename = os.path.join(os.getcwd(), "resources/graphics", "background.png")
        picture = pygame.image.load(filename)
        pygame.transform.scale(picture, (width,height))
        self.image.blit(picture, (0, 0))


class MenuCursor(pygame.sprite.Sprite):

    def __init__(self, menu, game, items):
        self.items = items
        self.menu = menu
        self.game = game
        self.groups = game.all_sprites
        self._layer = 2
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = pygame.Surface((self.menu.board.rect.width * 0.97,
                                self.menu.items.rect.height))
        self.image.fill((0,0,255))
        self.rect = self.image.get_rect()
        self.rect.y = self.menu.items.menu_init_y + self.rect.height
        self.rect.centerx = width / 2
        self.selectedItem = 0
        self.selectedItemX = 0
        self.selectedItemY = 0
        self.menu.keyboard = None

    def down(self):
        if self.menu.keyboard == None and self.selectedItem < len(self.menu.items.items) - 1:
            self.rect.y += self.rect.height
            self.selectedItem += 1
        else:
            self.selectedItemY = 0 #TODO

    def up(self):
        if self.menu.keyboard == None and self.selectedItem != 0:
            self.rect.y -= self.rect.height
            self.selectedItem -= 1
        else:
            self.selectedItemY = 0 #TODO

    def left(self):
        if self.menu.keyboard != None and self.selectedItemX>0:  #TODO
            self.rect.x -= 0
            self.selectedItemX -= 0

    def right(self):
        if self.menu.keyboard != None and self.selectedItemY < len(self.menu.keyboard.keys[self.selectedItemX]): #TODO
            self.rect.y -= 0
            self.selectedItemX -= 0


    def select(self,surface):
        logger.debug(str(self.selectedItem))
        logger.debug(self.items.items[self.selectedItem]["action"])
        if self.items.items[self.selectedItem]["action"] == 'menu':
            #reload menu with the new items
            with open(os.path.join(os.getcwd(),"resources/menus/"+self.items.items[self.selectedItem]["external"]+".json")) as jsonMenu:
                menu = json.load(jsonMenu)
                #for i in range(0,len(self.items.items)):
                #    self.up()
                self.items.items = menu
                #reset trick avoid commented for loop
                self.rect.y = self.menu.items.menu_init_y + self.rect.height
                self.selectedItem = 0
        elif self.items.items[self.selectedItem]["action"] == 'param':
            #keyboard
            self.menu.keyboard = Keyboard(self.game)

        elif self.items.items[self.selectedItem]["action"] == 'param':
            #command
            os.system(self.items.items[self.selectedItem]["external"])
        pixelate(surface,False)


class MenuItems(pygame.sprite.Sprite):

    def __init__(self, menu, game):
        self.menu = menu
        self.game = game
        self.groups = game.all_sprites
        self._layer = 3
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.items = []
        self.font = pygame.font.SysFont('Consolas', 30)
        self.image = self.font.render('', False, (255,255,255))
        self.rect = self.image.get_rect()
        self.menu_init_y = 40
        self.text_size_y = self.rect.height

    def draw(self):
        if self.menu.keyboard == None:
            counter = 0
            for item in self.items:
                counter += 1
                text_item = self.font.render(item["title"], False, (255,255,255))
                text_item_rect = text_item.get_rect()
                self.game.screen.blit(text_item, (self.menu.cursor.rect.left + (10), self.menu_init_y + (text_item_rect.height * counter)))

class MenuStatus(pygame.sprite.Sprite):

    def __init__(self, game):
        self.game = game

    def draw(self):

        pass


class Menu(MenuBoard, MenuCursor, MenuItems):

    def __init__(self, game):
        self.status = MenuStatus(game)
        self.board = MenuBoard(game)
        self.items = MenuItems(self, game)
        self.cursor = MenuCursor(self, game, self.items)
