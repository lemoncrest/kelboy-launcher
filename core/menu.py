import os
import json
import pygame
from core.settings import *
from core.component.keyboard import Keyboard, KeyboardScreen

import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, "log.txt"),level=logging.DEBUG)
logger = logging.getLogger(__name__)

from core.effect.pixelate import pixelate


class MenuBoard(pygame.sprite.Sprite):

    def __init__(self, game):
        self.game = game
        self.loadBackground()

    def loadBackground(self):
        self.groups = self.game.all_sprites
        self._layer = 1
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = pygame.Surface((width,height))
        #self.image.fill((0,255,255))
        self.rect = self.image.get_rect()
        self.rect.centery = height / 2
        self.rect.centerx = width / 2
        logger.debug("loading background...")
        filename = os.path.join(os.getcwd(), "resources/graphics", "background.png")
        picture = pygame.image.load(filename)
        pygame.transform.scale(picture, (width,height))
        self.image.blit(picture, (0, 0))


class MenuCursor(pygame.sprite.Sprite):

    def __init__(self, menu, game, items, board):
        self.board = board
        self.items = items
        self.menu = menu
        self.game = game
        self.loadBackground()

    def loadBackground(self):
        logger.debug("loading CURSOR background...")
        self.groups = self.game.all_sprites
        self._layer = 2
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = pygame.Surface((self.menu.board.rect.width * 0.97, self.menu.items.rect.height))
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
        elif self.menu.keyboard != None and self.menu.keyboard.positionY < 3:
            self.menu.keyboard.positionY += 1
            self.menu.keyboard.draw()


    def up(self):
        if self.menu.keyboard == None and self.selectedItem != 0:
            self.rect.y -= self.rect.height
            self.selectedItem -= 1
        elif self.menu.keyboard != None and self.menu.keyboard.positionY > 0:
            self.menu.keyboard.positionY -= 1
            self.menu.keyboard.draw()

    def left(self):
        if self.menu.keyboard == None:  #TODO
            self.rect.x -= 0
            self.selectedItemX -= 0
        elif self.menu.keyboard.positionX > 0:
            self.menu.keyboard.positionX -= 1
            self.menu.keyboard.draw()


    def right(self):
        if self.menu.keyboard == None: #TODO
            self.rect.y -= 0
            self.selectedItemX -= 0
        elif self.menu.keyboard.positionX < 9:
            self.menu.keyboard.positionX += 1
            self.menu.keyboard.draw()



    def select(self,surface):
        effect = False
        logger.debug(self.items.items[self.selectedItem]["action"])
        if self.items.items[self.selectedItem]["action"] == 'menu' and self.menu.keyboard == None:
            #reload menu with the new items
            self.menu.lastMenu = self.items.items[self.selectedItem]["external"]
            with open(os.path.join(os.getcwd(),"resources/menus/"+self.menu.lastMenu+".json")) as jsonMenu:
                menu = json.load(jsonMenu)
                #for i in range(0,len(self.items.items)):
                #    self.up()
                self.items.items = menu
                #reset trick avoid commented for loop
                self.rect.y = self.menu.items.menu_init_y + self.rect.height
                self.selectedItem = 0
                self.menu.keyboard = None
                self.board.loadBackground()
                self.loadBackground()
                effect = True
        elif self.items.items[self.selectedItem]["action"] == 'param' and self.menu.keyboard == None:
            #save last param name
            self.lastMenuParam = self.items.items[self.selectedItem]["name"]
            logger.debug("storing %s param in memory" % self.lastMenuParam)
            buffer = ""
            with open(os.path.join(os.getcwd(),"resources/menus/"+self.menu.lastMenu+".json")) as jsonMenu:
                menu = json.load(jsonMenu)
                for element in menu:
                    if "name" in element and element["name"] == self.lastMenuParam:
                        buffer = element["value"]

            #keyboard
            self.menu.keyboard = Keyboard(game=self.game,buffer=buffer)
            self.menu.keyboard.draw()
            self.menu.keyboardScreen = KeyboardScreen(self.game)
            self.menu.keyboardScreen.draw(buffer)
            effect = True
        elif self.items.items[self.selectedItem]["action"] == 'command':
            #command
            os.system(self.items.items[self.selectedItem]["external"])
            effect = True
        elif self.menu.keyboard != None:
            if self.menu.keyboard.show:
                if self.menu.keyboard.positionY != 3:
                    self.menu.keyboard.last = self.menu.keyboard.keys[self.menu.keyboard.positionY][self.menu.keyboard.positionX]
                    self.menu.keyboard.buffer += self.menu.keyboard.last
                    logger.debug("buffer is: '%s'" % self.menu.keyboard.buffer)
                else:
                    logger.debug("special keys")
                    key = self.menu.keyboard.specials[self.menu.keyboard.positionX]["name"]
                    if key == "ENTER":
                        buffer = self.menu.keyboard.buffer
                        logger.info("buffer: %s" % buffer)
                        self.menu.keyboard.kill()
                        self.menu.keyboard = None
                        #TODO exit with value
                        logger.debug("return and load last menu...")
                        menu = None
                        with open(os.path.join(os.getcwd(),"resources/menus/"+self.menu.lastMenu+".json")) as jsonMenu:
                            menu = json.load(jsonMenu)
                            for element in menu:
                                if "name" in element and element["name"] == self.lastMenuParam:
                                    element["value"] = buffer

                        with open(os.path.join(os.getcwd(),"resources/menus/"+self.menu.lastMenu+".json"),"w") as jsonMenu:
                            json.dump(menu, jsonMenu, indent=4, sort_keys=True)


                        #for i in range(0,len(self.items.items)):
                        #    self.up()
                        self.items.items = menu
                        #reset trick avoid commented for loop
                        self.rect.y = self.menu.items.menu_init_y + self.rect.height

                        self.selectedItem = 0

                        self.all_sprites = pygame.sprite.LayeredUpdates()
                        self.items.items = menu

                        self.board.loadBackground()
                        self.loadBackground()

                        effect = True
                    elif key == "SYMB":
                        logger.debug("SYMB")
                        self.menu.keyboard.symb = not self.menu.keyboard.symb
                    elif key == "MAYUS":
                        logger.debug("MAYUS")
                        self.menu.keyboard.shift = not self.menu.keyboard.shift
                    elif key == "SPACE":
                        self.menu.keyboard.buffer += " "
                        logger.debug("buffer with 'space' is: '%s'" % self.menu.keyboard.buffer)
                    elif key == "EXIT":
                        self.menu.keyboard.show = False
                        self.menu.keyboard.kill()
                        self.menu.keyboard = None

                        logger.debug("loading last menu...")
                        with open(os.path.join(os.getcwd(),"resources/menus/"+self.menu.lastMenu+".json")) as jsonMenu:
                            menu = json.load(jsonMenu)
                            #for i in range(0,len(self.items.items)):
                            #    self.up()
                            self.items.items = menu
                            #reset trick avoid commented for loop
                            self.rect.y = self.menu.items.menu_init_y + self.rect.height
                            self.selectedItem = 0

                        self.board.loadBackground()
                        self.loadBackground()

                        effect = True
                    else:
                        logger.debug("WHO ARE YOU?")

                if self.menu.keyboard:
                    self.menu.keyboard.draw()
                    self.menu.keyboardScreen.draw(self.menu.keyboard.buffer)
                else:
                    logger.debug("TODO... or not TODO")

        if effect:
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
                self.game.screen.blit(text_item, (self.menu.cursor.rect.left + (margin), self.menu_init_y + (text_item_rect.height * counter)))

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
        self.cursor = MenuCursor(self, game, self.items, self.board)
