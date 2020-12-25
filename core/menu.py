import os
import sys
import json
import subprocess
import threading
import pygame
import math
import re
import time
from core.settings import *
from core.colors import *
from core.component.keyboard import Keyboard, KeyboardScreen
from core.component.dialog import Dialog
import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)

from core.effect.pixelate import pixelate
from core.effect.fade import fade
from core import menuaction

class MenuBoard(pygame.sprite.Sprite):

    def __init__(self, main):
        self.main = main
        self._layer = 2
        self.loadBackground()

    def loadBackground(self):
        self.groups = self.main.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = pygame.Surface((WIDTH,HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.centery = HEIGHT / 2
        self.rect.centerx = WIDTH / 2
        logger.debug("loading background...")
        if BACKGROUND_ENABLE:
            filename = os.path.join("resources/graphics", BACKGROUND_PICTURE)
            picture = pygame.image.load(filename)
            picture = pygame.transform.scale(picture, (WIDTH,HEIGHT))
            self.image.blit(picture, (0, 0))

class MenuCursor(pygame.sprite.Sprite):

    def __init__(self, menu, main, items, board):
        self.board = board
        self.items = items
        self.menu = menu
        self.main = main
        self._layer = 2
        self.loadBackground()
        self.last = pygame.time.get_ticks()
        self.menu.prevMenu = "main" #intanced back to the first

        self.lastUp = pygame.time.get_ticks()
        self.lastDown = pygame.time.get_ticks()
        self.lastLeft = pygame.time.get_ticks()
        self.lastRight = pygame.time.get_ticks()

    def loadBackground(self):
        logger.debug("loading CURSOR background...")
        self.groups = self.main.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = pygame.Surface((self.menu.board.rect.width * 0.97, self.menu.items.rect.height))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()

        lenItems = len(self.items.items)
        if lenItems> MAX_MENU_ITEMS:
            lenItems = MAX_MENU_ITEMS

        self.rect.y = HEIGHT / 2 - ((lenItems / 2)*self.items.rect.height )

        self.rect.centerx = WIDTH / 2
        logger.debug("x %s y %s" % (self.rect.x, self.rect.y))
        self.selectedItem = 0
        self.selectedItemX = 0
        self.selectedItemY = 0
        self.menu.keyboard = None

    def down(self, force=False):
        if (self.lastDown + KEY_WHILE_SLEEP*1000 < pygame.time.get_ticks()) or force:
            self.lastDown = pygame.time.get_ticks()
            if self.menu.keyboard == None and self.menu.dialog == None:
                if self.selectedItem < len(self.menu.items.items) - 1:
                    if self.selectedItem<MAX_MENU_ITEMS-2:
                        self.rect.y += self.rect.height
                    self.selectedItem += 1
                else:
                    logger.debug("limit down")
                    self.selectedItem = 0
                    if len(self.menu.items.items)>MAX_MENU_ITEMS-1:
                        self.rect.y -= (self.rect.height*8)
                    else:
                        self.rect.y -= (self.rect.height*(len(self.menu.items.items)-1))
            elif self.menu.keyboard != None and self.menu.keyboard.positionY < 3:
                self.menu.keyboard.positionY += 1
                self.menu.keyboard.draw()


    def up(self, force=False):
        if (self.lastUp + KEY_WHILE_SLEEP*1000 < pygame.time.get_ticks()) or force:
            self.lastUp = pygame.time.get_ticks()
            if self.menu.keyboard == None and self.menu.dialog == None:
                if self.selectedItem != 0:
                    if self.selectedItem<MAX_MENU_ITEMS-1:
                        self.rect.y -= self.rect.height
                    self.selectedItem -= 1
                else:
                    logger.debug("limit up")
                    self.selectedItem = len(self.menu.items.items) - 1
                    #the last item is first + number of displayed items
                    self.selectedItem = len(self.menu.items.items)-1
                    if len(self.menu.items.items)>8:
                        self.rect.y += (self.rect.height*8)
                        self.selectedItem = len(self.menu.items.items)-1
                    else:
                        self.rect.y += (self.rect.height*(len(self.menu.items.items)-1))
            elif self.menu.keyboard != None and self.menu.keyboard.positionY > 0:
                self.menu.keyboard.positionY -= 1
                self.menu.keyboard.draw()

    def left(self, force=False):
        if (self.lastLeft + KEY_WHILE_SLEEP*1000 < pygame.time.get_ticks()) or force:
            self.lastLeft = pygame.time.get_ticks()
            if self.menu.keyboard == None:
                self.rect.x -= 0
                self.selectedItemX -= 0
            elif self.menu.keyboard.positionX > 0:
                self.menu.keyboard.positionX -= 1
                self.menu.keyboard.draw()


    def right(self, force=False):
        if (self.lastRight + KEY_WHILE_SLEEP*1000 < pygame.time.get_ticks()) or force:
            self.lastRight = pygame.time.get_ticks()
            if self.menu.keyboard == None:
                self.rect.y -= 0
                self.selectedItemX -= 0
            elif self.menu.keyboard.positionX < 9:
                self.menu.keyboard.positionX += 1
                self.menu.keyboard.draw()

    def back(self,surface):
        if (pygame.time.get_ticks() - self.last > EVENT_DELAY_TIME) and not (self.menu.dialog or self.menu.keyboard):
            with open(os.path.join("resources/menus/"+self.menu.prevMenu+".json")) as jsonMenu:
                currentMenu = json.load(jsonMenu)
                #destroy sprites
                self.board.kill()
                self.items.kill()
                self.kill()
                #reload menu (rebuil sprites)
                self.menu.load(currentMenu)

                #update prevMenu and lastMenu (current)
                self.menu.lastMenu = self.menu.prevMenu
                for menu in currentMenu:
                    if "title" in menu and menu["title"].lower() == 'back' and "action" in menu and menu["action"] == 'menu':
                        self.menu.prevMenu = menu["external"]

                pixelate(surface,True)

    def select(self,surface):
        if pygame.time.get_ticks() - self.last > EVENT_DELAY_TIME:
            self.last = pygame.time.get_ticks()
            effect = False
            logger.debug("action: %s" % self.items.items[self.selectedItem]["action"])
            if self.menu.dialog != None:
                self.menu.dialog.kill()
                self.menu.dialog = None
            elif self.items.items[self.selectedItem]["action"] == 'menu' and self.menu.keyboard == None:
                #reload menu with the new items
                self.menu.prevMenu = self.menu.lastMenu #to be used in back button
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
            elif self.items.items[self.selectedItem]["action"] == 'function-text':
                if self.menu.keyboard == None:
                    fade(self.main.screen)
                    self.menu.keyboard = Keyboard(main=self.main,buffer='')
                    self.menu.keyboard.draw()
                    self.menu.keyboardScreen = KeyboardScreen(self.main)
                    self.menu.keyboardScreen.draw('')
                    self.menu.keyboard.loadMenu = False
                    effect = True
                elif self.menu.keyboard.show:
                    logger.debug("continue with show")
                    effect = self.manageKeyboard()
                else:
                    logger.debug("show exits!")
            elif self.items.items[self.selectedItem]["action"] == 'command-message':
                cmd = self.items.items[self.selectedItem]["external"]
                logger.debug('command message is "%s" ' % cmd)
                process = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
                result = process.stdout
                result = re.sub('[^A-Za-z0-9.\-,\ ]+', '', result) #just normal chars
                logger.debug("result is %s" % result)
                self.menu.dialog = Dialog(main=self.main,title="Result",message=result, dialogWidth=160,dialogHeight=140)
            elif self.items.items[self.selectedItem]["action"] == 'function':
                logger.debug("dynamicMethod...")
                #loading effect...
                pixelate(self.main.screen,True)
                params = []
                funct = self.items.items[self.selectedItem]["external"]
                logger.debug("function %s" % funct)
                #now call to function with params
                dynamicMethod = getattr(menuaction, funct)
                params = []
                if "params" in self.items.items[self.selectedItem]:
                    params = self.items.items[self.selectedItem]["params"]
                try:
                    menu = dynamicMethod(params=params)
                    logger.debug("menu: %s " % str(menu))
                    self.last = pygame.time.get_ticks() #refresh time for dynamic methods
                    if menu:
                        if type(menu) is list:
                            logger.debug('list!!')
                            #destroy sprites
                            self.board.kill()
                            self.items.kill()
                            self.kill()
                            #reload menu (rebuil sprites)
                            self.menu.load(menu)
                            #pixelate
                        elif type(menu) is dict:
                            if 'external' in menu:
                                logger.debug('dict!!')
                                #command and exit
                                pixelate(surface,True)
                                pygame.display.quit()
                                pygame.quit()
                                #os.system(self.items.items[self.selectedItem]["external"])
                                text_file = open("command", "w")
                                text_file.write(menu['external'])
                                text_file.close()
                                sys.exit(10)
                            elif 'external-keyboard' in external:
                                function = 'saveWifiPWD'
                                logger.debug("function %s",funct)
                                #now call to function with params
                                #keyboard
                                self.menu.keyboard = Keyboard(main=self.main,buffer=buffer)
                                self.menu.keyboard.draw()
                                self.menu.keyboardScreen = KeyboardScreen(self.main)
                                self.menu.keyboardScreen.draw(buffer)
                                effect = True
                                #dynamicMethod = getattr(menuaction, funct)
                                pass
                        else:
                            logger.debug("else %s" % str(type(menu)))
                except Exception as ex:
                    logger.error(str(ex))

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
                pixelate(self.main.screen,True)
                os.system(self.items.items[self.selectedItem]["external"])
                pygame.event.clear()
                self.last = pygame.time.get_ticks()
                effect = True
            elif self.items.items[self.selectedItem]["action"] == 'command-exit':
                #command and exit
                pixelate(surface,True)
                pygame.display.quit()
                pygame.quit()
                #os.system(self.items.items[self.selectedItem]["external"])
                text_file = open("command", "w")
                text_file.write(self.items.items[self.selectedItem]["external"])
                text_file.close()
                sys.exit(10)
            elif self.items.items[self.selectedItem]["action"] == 'exit':
                pixelate(surface,True)
                pygame.display.quit()
                pygame.quit()
                sys.exit(0)
            elif self.menu.keyboard != None and self.menu.keyboard.show:
                effect = self.manageKeyboard()

            if effect:
                pixelate(surface,False)


    def manageKeyboard(self):
        effect = False

        if self.menu.keyboard.positionY != 3:
            if self.menu.keyboard.shift and not self.menu.keyboard.symb:
                self.menu.keyboard.last = self.menu.keyboard.mayus[self.menu.keyboard.positionY][self.menu.keyboard.positionX]
            elif self.menu.keyboard.symb and not self.menu.keyboard.shift:
                self.menu.keyboard.last = self.menu.keyboard.symbols[self.menu.keyboard.positionY][self.menu.keyboard.positionX]
            elif self.menu.keyboard.shift and self.menu.keyboard.symb:
                self.menu.keyboard.last = self.menu.keyboard.mayusSimbols[self.menu.keyboard.positionY][self.menu.keyboard.positionX]
            else:
                self.menu.keyboard.last = self.menu.keyboard.keys[self.menu.keyboard.positionY][self.menu.keyboard.positionX]
            self.menu.keyboard.buffer += self.menu.keyboard.last
            logger.debug("buffer is: '%s'" % self.menu.keyboard.buffer)
        else:
            logger.debug("special keys")
            key = self.menu.keyboard.specials[self.menu.keyboard.positionX]["name"]
            if key == Keyboard.ENTER:
                buffer = self.menu.keyboard.buffer
                loadMenu = self.menu.keyboard.loadMenu
                logger.info("buffer: %s" % buffer)
                self.menu.keyboard.kill()
                self.menu.keyboard = None
                #TODO exit with value
                if loadMenu:
                    logger.debug("return and load last menu...")
                    menu = None
                    with open(os.path.join("resources/menus/"+self.menu.lastMenu+".json")) as jsonMenu:
                        menu = json.load(jsonMenu)
                        for element in menu:
                            if "name" in element and element["name"] == self.lastMenuParam:
                                element["value"] = buffer

                    with open(os.path.join(os.getcwd(),"resources/menus/"+self.menu.lastMenu+".json"),"w") as jsonMenu:
                        json.dump(menu, jsonMenu, indent=4, sort_keys=True)
                else: #dynamicMethod
                    funct = self.items.items[self.selectedItem]["external"]
                    logger.debug("dynamic function %s",funct)
                    #now call to function with params
                    dynamicMethod = getattr(menuaction, funct)
                    logger.debug(str(self.items.items[self.selectedItem]))
                    params = []
                    if "params" in self.items.items[self.selectedItem]:
                        params = self.items.items[self.selectedItem]["params"]
                    params.append({'text':buffer})
                    menu = dynamicMethod(params=params)
                    pygame.event.clear()
                    self.last = pygame.time.get_ticks() #refresh time for dynamic
                    logger.debug("returning menu: %s " % str(menu))

                #destroy sprites
                self.board.kill()
                self.items.kill()
                self.kill()
                #reload menu (rebuil sprites)
                self.menu.load(menu)
                #pixelate
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
            elif key == Keyboard.BACK:
                self.menu.keyboard.buffer = self.menu.keyboard.buffer[:len(self.menu.keyboard.buffer)-1]
                logger.debug("buffer BACKED is: '%s'" % self.menu.keyboard.buffer)
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
            if self.menu.keyboard:
                self.menu.keyboard.show = False
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
        self.font = pygame.font.Font(FONT_TYPE, FONT_SIZE)
        self.image = self.font.render(' ', False, FONT_COLOR_ITEM)

        self.height = self.font.render('X', False, FONT_COLOR_ITEM).get_rect().height

        self.rect = self.image.get_rect()
        #self.menu_init_y = 40
        self.text_size_y = self.rect.height
        lenItems = len(self.items)
        #too much items in a list, needs to be recalculated
        if lenItems>MAX_MENU_ITEMS:
            lenItems = MAX_MENU_ITEMS
        self.image = pygame.Surface((self.menu.board.rect.width * 0.97, self.height * lenItems), pygame.SRCALPHA)
        self.timer = pygame.time.get_ticks()
        self.lastSelected = 0
        self.movement = 0
        self.refreshTime = HORIZONTAL_MOVEMENT_REFRESH_FACTOR
        self.waitTime = HORIZONTAL_MOVEMENT_WAIT_TIME * (1000/self.refreshTime)

    def draw(self):
        #it's need to be recalculated each time, so not put it in builder
        self.image.fill((255, 255, 255, 0), None) #clean menu
        self.rect = self.image.get_rect()
        self.rect.centery = HEIGHT / 2
        self.rect.centerx = WIDTH / 2

        x = 0
        y = 0

        if self.menu.keyboard == None:
            counter = 0
            counterNew = 0
            for item in self.items:
                title = result = re.sub('[^A-Za-z0-9.\-,\ ]+', '', item["title"]) #just normal chars
                text_item = self.font.render(title, False, FONT_COLOR_ITEM)
                text_item_rect = text_item.get_rect()
                #self.image.blit(text_item, (self.menu.cursor.rect.left + (margin), self.menu_init_y + (text_item_rect.height * counter)))
                #self.main.screen.blit(text_item, (self.menu.cursor.rect.left + (margin), 0 + (text_item_rect.height * counter)) )

                #this movement is used to launch horizontal pixel movement effect in menu
                index = self.menu.cursor.selectedItem

                movement = 0

                if TEXT_MOVEMENT_EFFECT and len(self.items[index]["title"])>20:

                    if self.lastSelected != index or (self.font.size(self.items[index]["title"])[0] + margin - self.movement) < 0:
                        self.lastSelected = index
                        self.timer = pygame.time.get_ticks()
                        self.movement = 0
                        logger.debug("updated timer '%s'!" % self.items[index]["title"])

                    if int(pygame.time.get_ticks() / self.refreshTime) - int(self.timer / self.refreshTime) > self.waitTime:
                        self.movement = int(pygame.time.get_ticks() / self.refreshTime) - int(self.timer / self.refreshTime) - self.waitTime
                        logger.debug("%s %s" % (self.movement-self.waitTime,(margin + self.font.size(title)[0])))


                    else:
                        self.movement = 0

                    if index == counter:
                        movement = self.movement

                if len(self.items)<MAX_MENU_ITEMS:

                    self.image.blit(text_item, (self.menu.cursor.rect.left + margin - movement, counter*self.height ))
                else:
                    if index<MAX_MENU_ITEMS-1:
                        self.image.blit(text_item, (self.menu.cursor.rect.left + margin - movement, counter*self.height ))
                    else:
                        if index-MAX_MENU_ITEMS<counter-1 and counterNew<MAX_MENU_ITEMS-1:
                            self.image.blit(text_item, (self.menu.cursor.rect.left + margin - movement, counterNew*self.height ))
                            counterNew+=1
#                            logger.debug("writting %s with %s and %s with %s" % (title,str(counter),str(counterNew),str(index)))
#                        else:
#                            logger.debug("discarting %s" % str(counter))

                counter += 1
                time.sleep(MENU_ITEM_REFRESH_TIME)


class MenuStatus(pygame.sprite.Sprite):

    def __init__(self, main):
        self.main = main
        self._layer = 3
        self.groups = main.all_sprites
        self.font = pygame.font.Font(FONT_TYPE, FONT_SIZE)
        self.image = pygame.Surface((WIDTH, BARSIZE))
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image.fill(BLACK)
        #self.image.set_alpha(150)
        self.rect = self.image.get_rect()
        self.rect.centery = self.image.get_rect().height/2
        self.rect.centerx = WIDTH / 2
        self.rect.x = 0
        self.rect.y = 0
        self.time = pygame.time.get_ticks()

    def draw(self):
        if pygame.time.get_ticks() - self.time > WIDGET_FRAMETIME:
            self.time = pygame.time.get_ticks()
            try:
                self.drawWidgets()
            except:
                pass

    def drawWidgets(self):
        self.padding = 1
        self.margin = 1

        #draw battery
        battery = 0 #TODO extract from driver
        charging = False
        try:
            process = subprocess.run(BATTERY_PERCENTAGE_CMD, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
            battery = int(process.stdout)
        except Exception as ex:
            battery = 0 #"lightning-empty-help"
            level = 0
            pass
        try:
            process = subprocess.run(FUELGAUGE_CURRENT_CMD, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
            charging = int(process.stdout) > 0
        except Exception as ex:
            charging = False
            pass
        if charging:
            level = "lightning-empty-help"
            if(battery>50):
                level = "lightning-midle"
                if(battery>=95):
                    level = "lightning-full"
            elif battery>15:
                level = "lightning-empty"
        else:
            if(battery>50):
                level = "75"
                if(battery<75):
                    level = "50"
                elif(battery>=95):
                    level = "100"
            elif battery>15:
                level = "25"
            else:
                level = "0"
        image = pygame.image.load(os.path.join("resources/graphics", "battery-"+str(level)+".png"))
        rect1 = (WIDTH-(image.get_rect().width*1.5),BARSIZE/2-(image.get_rect().height/2))
        self.image.fill(BLACK)
        self.image.blit(image, rect1)

        #draw sound
        init = self.drawAudio(start=(image.get_rect().width+25),number=False)

        #internet
        self.drawWifi(start=(image.get_rect().width*2)+34)

        #bluetooth
        #TODO



    def drawAudio(self,start=0,number=False):
        #cmd = "amixer -D pulse sget Master | grep 'Left:' | awk -F'[][]' '{ print $2 }'"
        #cmd = "amixer sget Master | grep 'Left' | awk -F'[][]' '{ print $2 }'"

        cmd = "amixer | grep % | head -n 1 | awk -F'[][]' '{ print $2 }'"
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        level = out.decode("utf-8")
        level = level[:len(level)-2] #remove % character
        rect = None
        if number:
            width = self.font.size("100")[0] + (self.margin * 2) #max sized to be used in background
            height = self.font.size(level)[1] + (self.margin * 2)
            x = WIDTH - width - start
            rect = pygame.Rect(x, 0, width, BARSIZE)
            pygame.draw.rect(self.image,BLACK,rect)
            #self.image.blit(self.bar, rect)
            #pygame.display.update(rect)
            txt = self.font.render(level, True, WHITE)
            x = WIDTH - start
            y = BARSIZE / 2 - (height/2)
            textPoint = (x -self.margin*3 -self.padding*3 - (self.font.size(level)[0])/2, y)
            self.image.blit(txt, textPoint)
        else:
            top = 15
            width = top*2
            height = top
            x = WIDTH - start - top
            y = (BARSIZE - height) / 2
            rect = pygame.Rect(x  - (self.margin*2), 0, top, BARSIZE)
            pygame.draw.rect(self.image, BLACK, rect)

            #first display speaker
            pygame.draw.polygon(self.image,WHITE,( (x+(top/2),y+0),(x+(top/4),y+(top/4)),(x+0,y+(top/4)),(x+0,y+(top*3/4)),(x+(top/4),y+(top*3/4)),(x+(top/2),y+top) ))
            #next display bars
            try:
                bars = int(int(level)/14)
            except:
                bars = 0
                pass

            try:
                level = int(level)
            except:
                logger.debug("couldn't parse level '%s'" % level)
                pass
            barSize = 1
            init = WIDTH - start - (top/2)
            rect2 = pygame.Rect(init, y, barSize+ self.padding*7*2, top)
            pygame.draw.rect(self.image,BLACK,rect2)
            if bars > 0:
                for x in range(bars):
                    rect2 = pygame.Rect(init + self.padding*x*2, y, barSize, top)
                    pygame.draw.rect(self.image,WHITE,rect2)
            if int(level)==0:
                txt = self.font.render("X", True, RED)
                textPoint = (init + self.padding*5, BARSIZE / 2 - (self.font.size("X")[1]/2))
                self.image.blit(txt, textPoint)

        return init


    def drawWifi(self,start=0,totalBars=5,barWidth=3):
        cmd = "awk 'NR==3 {print $4}''' /proc/net/wireless"
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        level = out.decode("utf-8").replace(".","")
        level = out.decode("utf-8").replace(".","")
        try:
            #level = 2*(int(level)+80) #dBm conversion to percentage
            dBm = int(level)
            # dBm to Quality:
            if(dBm <= -100):
                level = 0;
            elif(dBm >= -50):
                level = 100;
            else:
                level = 2 * (dBm + 100)
                #logger.debug(str(level))
        except Exception as ex:
            level = 0 #no signal
            #logger.error("not converted"+str(ex))
            pass

        barHeight = barWidth * 8
        width = (self.padding*2*totalBars) + (barWidth*totalBars) + (self.margin*2)
        #background
        x = WIDTH - start - width
        rect = pygame.Rect(x, 0, width, BARSIZE)
        pygame.draw.rect(self.image, BLACK, rect)

        #bars
        if level==0: #when no signal them display red X
            txt = self.font.render("X", True, RED)
            yP = int((BARSIZE - self.font.size("X")[1])/2)
            x1 = x + self.padding * 2 + (barWidth*0) + self.margin
            x2 = x + self.padding * (totalBars+2) * 2 + (barWidth*(totalBars+1)) + self.margin
            x3 = x2-x1
            xP = x + (x3/2)
            textPointA = (xP, yP)
            self.image.blit(txt, textPointA)
        bars = math.ceil(level*totalBars/100)
        for i in range(0,bars+1,1):
            xP = x + self.padding * (i+1) * 2 + (barWidth*i) + self.margin
            ySize = int(barHeight / totalBars * i) - (self.padding*i*2)
#            if ySize < 1:
#                ySize = 1
            yP = int(BARSIZE) - (ySize) - 5
#            if yP < 1:
#                yP = 1
            if ySize > 0:
                rect = pygame.Rect(xP, yP, barWidth, ySize)
                pygame.draw.rect(self.image, GREEN, rect)
        for i in range(bars,totalBars,1):  # points
            txt = self.font.render(".", True, WHITE)
            xP = x + self.padding * (i+1) * 2 + (barWidth*i) + self.margin + (self.font.size("X")[0]/2)
            #yP = (BARSIZE - barHeight) - (self.font.size(".")[1] / 2)
            yP = int(BARSIZE/2) - 2
            textPointB = (xP, yP)
            self.image.blit(txt, textPointB)
        return rect


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
