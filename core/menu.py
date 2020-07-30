import os
import sys
import json
import subprocess
import pygame
from core.settings import *
from core.colors import *
from core.component.keyboard import Keyboard, KeyboardScreen

import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=logging.DEBUG)
logger = logging.getLogger(__name__)

from core.effect.pixelate import pixelate
from core import menuaction

class MenuBoard(pygame.sprite.Sprite):

    def __init__(self, main):
        self.main = main
        self._layer = 2
        self.loadBackground()

    def loadBackground(self):
        self.groups = self.main.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = pygame.Surface((width,height))
        self.rect = self.image.get_rect()
        self.rect.centery = height / 2
        self.rect.centerx = width / 2
        logger.debug("loading background...")
        filename = os.path.join("resources/graphics", "background.png")
        picture = pygame.image.load(filename)
        pygame.transform.scale(picture, (width,height))
        self.image.blit(picture, (0, 0))

class MenuCursor(pygame.sprite.Sprite):

    def __init__(self, menu, main, items, board):
        self.board = board
        self.items = items
        self.menu = menu
        self.main = main
        self._layer = 2
        self.loadBackground()

    def loadBackground(self):
        logger.debug("loading CURSOR background...")
        self.groups = self.main.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = pygame.Surface((self.menu.board.rect.width * 0.97, self.menu.items.rect.height))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()

        self.rect.y = height / 2 - ((len(self.items.items) / 2)*self.items.rect.height )

        self.rect.centerx = width / 2
        logger.debug("x %s y %s" % (self.rect.x, self.rect.y))
        self.selectedItem = 0
        self.selectedItemX = 0
        self.selectedItemY = 0
        self.menu.keyboard = None

    def down(self):
        if self.menu.keyboard == None and self.menu.dialog == None and self.selectedItem < len(self.menu.items.items) - 1:
            self.rect.y += self.rect.height
            self.selectedItem += 1
        elif self.menu.keyboard != None and self.menu.keyboard.positionY < 3:
            self.menu.keyboard.positionY += 1
            self.menu.keyboard.draw()


    def up(self):
        if self.menu.keyboard == None and self.menu.dialog == None and self.selectedItem != 0:
            self.rect.y -= self.rect.height
            self.selectedItem -= 1
        elif self.menu.keyboard != None and self.menu.keyboard.positionY > 0:
            self.menu.keyboard.positionY -= 1
            self.menu.keyboard.draw()

    def left(self):
        if self.menu.keyboard == None:
            self.rect.x -= 0
            self.selectedItemX -= 0
        elif self.menu.keyboard.positionX > 0:
            self.menu.keyboard.positionX -= 1
            self.menu.keyboard.draw()


    def right(self):
        if self.menu.keyboard == None:
            self.rect.y -= 0
            self.selectedItemX -= 0
        elif self.menu.keyboard.positionX < 9:
            self.menu.keyboard.positionX += 1
            self.menu.keyboard.draw()


    def select(self,surface):
        effect = False
        logger.debug(self.items.items[self.selectedItem]["action"])
        if self.menu.dialog != None:
            self.menu.dialog.kill()
            self.menu.dialog = None
        elif self.items.items[self.selectedItem]["action"] == 'menu' and self.menu.keyboard == None:
            #reload menu with the new items
            self.menu.lastMenu = self.items.items[self.selectedItem]["external"]
            with open(os.path.join("resources/menus/"+self.menu.lastMenu+".json")) as jsonMenu:
                menu = json.load(jsonMenu)
                #destroy sprites
                self.board.kill()
                self.items.kill()
                self.kill()
                #reload menu (rebuil sprites)
                self.menu.load(menu)
                #pixelate
                effect = True
        elif self.items.items[self.selectedItem]["action"] == 'function':
            params = []
            funct = self.items.items[self.selectedItem]["external"]
            logger.debug("function %s",funct)
            #now call to function with params
            dynamicMethod = getattr(menuaction, funct)
            dynamicMethod()
        elif self.items.items[self.selectedItem]["action"] == 'param' and self.menu.keyboard == None:
            #save last param name
            self.lastMenuParam = self.items.items[self.selectedItem]["name"]
            logger.debug("storing %s param in memory" % self.lastMenuParam)
            buffer = ""
            with open(os.path.join("resources/menus/"+self.menu.lastMenu+".json")) as jsonMenu:
                menu = json.load(jsonMenu)
                for element in menu:
                    if "name" in element and element["name"] == self.lastMenuParam:
                        buffer = element["value"]

            #keyboard
            self.menu.keyboard = Keyboard(main=self.main,buffer=buffer)
            self.menu.keyboard.draw()
            self.menu.keyboardScreen = KeyboardScreen(self.main)
            self.menu.keyboardScreen.draw(buffer)
            effect = True
        elif self.items.items[self.selectedItem]["action"] == 'command':
            #command
            pixelate(surface,True)
            os.system(self.items.items[self.selectedItem]["external"])
            effect = True
        elif self.items.items[self.selectedItem]["action"] == 'command-exit':
            #command and exit
            pixelate(surface,True)
            os.system(self.items.items[self.selectedItem]["external"])
            sys.exit()
        elif self.items.items[self.selectedItem]["action"] == 'exit':
            pixelate(surface,True)
            sys.exit()
        elif self.menu.keyboard != None and self.menu.keyboard.show:
            effect = self.manageKeyboard()

        if effect:
            pixelate(surface,False)


    def manageKeyboard(self):
        effect = False

        if self.menu.keyboard.positionY != 3:
            if self.menu.keyboard.shift:
                self.menu.keyboard.last = self.menu.keyboard.mayus[self.menu.keyboard.positionY][self.menu.keyboard.positionX]
            elif self.menu.keyboard.symb:
                self.menu.keyboard.last = self.menu.keyboard.symbols[self.menu.keyboard.positionY][self.menu.keyboard.positionX]
            else:
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
                with open(os.path.join("resources/menus/"+self.menu.lastMenu+".json")) as jsonMenu:
                    menu = json.load(jsonMenu)
                    for element in menu:
                        if "name" in element and element["name"] == self.lastMenuParam:
                            element["value"] = buffer

                with open(os.path.join(os.getcwd(),"resources/menus/"+self.menu.lastMenu+".json"),"w") as jsonMenu:
                    json.dump(menu, jsonMenu, indent=4, sort_keys=True)

                #destroy sprites
                self.board.kill()
                self.items.kill()
                self.kill()
                #reload menu (rebuil sprites)
                self.menu.load(menu)
                #pixelate
                effect = True

                effect = True
            elif key == Keyboard.SYMB:
                logger.debug("SYMB")
                self.menu.keyboard.symb = not self.menu.keyboard.symb
            elif key == Keyboard.MAYUS:
                logger.debug("MAYUS")
                self.menu.keyboard.shift = not self.menu.keyboard.shift
            elif key == Keyboard.SPACE:
                self.menu.keyboard.buffer += " "
                logger.debug("buffer with 'space' is: '%s'" % self.menu.keyboard.buffer)
            elif key == Keyboard.EXIT:
                self.menu.keyboard.show = False
                self.menu.keyboard.kill()
                self.menu.keyboard = None

                logger.debug("loading last menu...")
                with open(os.path.join("resources/menus/"+self.menu.lastMenu+".json")) as jsonMenu:
                    menu = json.load(jsonMenu)
                    #destroy sprites
                    self.board.kill()
                    self.items.kill()
                    self.kill()
                    #reload menu (rebuil sprites)
                    self.menu.load(menu)

                effect = True
            else:
                logger.debug("WHO ARE YOU?")

        if self.menu.keyboard:
            self.menu.keyboard.draw()
            self.menu.keyboardScreen.draw(self.menu.keyboard.buffer)
        else:
            logger.debug("TODO... or not TODO")

        return effect



class MenuItems(pygame.sprite.Sprite):

    def __init__(self, menu, main, items):
        self.menu = menu
        self.main = main
        self.groups = main.all_sprites
        self._layer = 3
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.items = items
        self.font = pygame.font.Font('resources/fonts/times.ttf', FONT_SIZE)
        self.image = self.font.render(' ', False, WHITE)

        self.height = self.font.render('X', False, WHITE).get_rect().height

        self.rect = self.image.get_rect()
        #self.menu_init_y = 40
        self.text_size_y = self.rect.height

        self.image = pygame.Surface((self.menu.board.rect.width * 0.97, self.height * len(self.items)), pygame.SRCALPHA)

    def draw(self):
        #it's need to be recalculated each time, so not put it in builder
        #self.image.set_alpha(0)
        self.rect = self.image.get_rect()
        self.rect.centery = height / 2
        self.rect.centerx = width / 2

        x = 0
        y = 0

        if self.menu.keyboard == None:
            counter = 0
            for item in self.items:
                text_item = self.font.render(item["title"], False, WHITE)
                text_item_rect = text_item.get_rect()
                #self.image.blit(text_item, (self.menu.cursor.rect.left + (margin), self.menu_init_y + (text_item_rect.height * counter)))
                #self.main.screen.blit(text_item, (self.menu.cursor.rect.left + (margin), 0 + (text_item_rect.height * counter)) )
                self.image.blit(text_item, (self.menu.cursor.rect.left + margin, counter*self.height ))
                counter += 1

class MenuStatus(pygame.sprite.Sprite):

    def __init__(self, main):
        self.main = main
        self._layer = 3
        self.groups = main.all_sprites
        self.font = pygame.font.Font('resources/fonts/times.ttf', FONT_SIZE)
        self.image = pygame.Surface((width, 25))
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image.fill(BLACK)
        self.image.set_alpha(150)
        self.rect = self.image.get_rect()
        self.rect.centery = self.image.get_rect().height/2
        self.rect.centerx = width / 2
        self.rect.x = 0
        self.rect.y = 0

    def draw(self):
        #draw battery
        battery = 0 #TODO extract from driver
        charging = False
        command = 'cat /sys/class/power_supply/max1726x_battery/capacity'
        try:
            process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
            battery = int(process.stdout)
        except:
            battery = 0 #"lightning-empty-help"
            level = 0
            pass
        if not charging:
            if(battery>50):
                level = "75"
                if(battery<75):
                    level = "50"
                elif(battery>=95):
                    level = "100"
            elif battery>0:
                level = "25"
        image = pygame.image.load(os.path.join("resources/graphics", "battery-"+str(level)+".png"))
        self.image.blit(image, (width-(image.get_rect().width*1.5),(image.get_rect().width/2)))

        #internet

        #bluetooth



class Menu(MenuBoard, MenuCursor, MenuItems):

    def __init__(self, main, items):
        self.main = main
        self.load(items)

    def load(self,items):
        self.status = MenuStatus(self.main)
        self.board = MenuBoard(self.main)
        self.items = MenuItems(self, self.main, items)
        self.cursor = MenuCursor(self, self.main, self.items, self.board)
        self.dialog = None
        self.keyboard = None
