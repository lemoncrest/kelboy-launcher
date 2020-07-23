import os
import json
import time
import pygame

from core.settings import *
from core.menu import Menu
from core.effect.snow import SnowBall
from core.colorpalette import *

import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, "log.txt"),level=logging.DEBUG)
logger = logging.getLogger(__name__)

from core.utils import Utils

class Main():

    def __init__(self):

        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Menu')
        self.rgb = RGBColors()
        self.clock = pygame.time.Clock()
        self.frameRate = frameRate
        self.frameCounter = 0
        self.running = True
        self.loadAssets()
        logger.debug("launch joystics init...")
        utils = Utils()
        utils.initJoysticks()
        #disable mouse
        pygame.event.set_blocked(pygame.MOUSEMOTION)

    def loadAssets(self):
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.menu = Menu(self)
        self.menu.lastMenu = "main"
        with open(os.path.join(os.getcwd(),"resources/menus/main.json")) as jsonMenu:
            menu = json.load(jsonMenu)
            self.menu.items.items = menu
            self.menu.keyboard = None

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                #reset screensaver time to 0
                self.last = int(round(time.time())*1000)
                self.screensaver = False
                if event.key == pygame.K_DOWN:
                    self.menu.cursor.down()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                    self.menu.cursor.up()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.menu.cursor.select(self.screen)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                    self.menu.cursor.left()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                    self.menu.cursor.right()
            elif event.type == pygame.JOYBUTTONDOWN:
                #reset screensaver time to 0
                self.last = int(round(time.time())*1000)
                self.screensaver = False
                if event.button == 1:  # button A - enter
                    self.menu.cursor.select(self.screen)
                elif event.button == 2:  # button B - back
                    pass #TODO back
            elif event.type == pygame.JOYAXISMOTION:
                #reset screensaver time to 0
                self.last = int(round(time.time())*1000)
                self.screensaver = False
                if event.axis == 1:  # up and down
                    if event.value > 0:
                        self.menu.cursor.up()
                    elif event.value < 0:
                        self.menu.cursor.down()
                elif event.axis == 0:  # left and right
                    if event.value > 0:
                        self.menu.cursor.right()
                    elif event.value < 0:
                        self.menu.cursor.left()

    def update(self):
        self.all_sprites.update()

    def draw(self):
        self.screen.fill(self.rgb.black)
        self.all_sprites.draw(self.screen)
        self.menu.items.draw()

    def run(self):
        self.screensaver = False #TODO
        self.last = int(round(time.time())*1000)
        while self.running:
            if self.last+screensaverTime < int(round(time.time())*1000):
                self.screensaver = True
            if self.screensaver:
                SnowBall().launchSnowBalls()
                self.last = int(round(time.time())*1000)
                self.screensaver = False
            self.frameCounter += 1
            self.clock.tick(self.frameRate)
            self.events()
            self.update()
            self.draw()
            pygame.display.flip()
            if self.frameCounter == self.frameRate:
                self.frameCounter = 0

main = Main()
while main.running:
    main.run()
pygame.quit()
