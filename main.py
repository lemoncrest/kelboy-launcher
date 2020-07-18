import os
import pygame
from core.settings import *
from core.menu import Menu
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
        logger.debug("build joystics init...")
        utils = Utils()
        utils.initJoysticks()

    def loadAssets(self):
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.menu = Menu(self)
        self.menu.items.items = [
            {
                "title" : "Launch Emulationstation",
                "action" : "exit",
                "external": "emulationstation"
            },{
                "title" : "Settings",
                "action" : "menu",
                "menu" : "settings"
            },{
                "title" : "Quit",
                "action" : "exit",
                "external": "sudo reboot"
            }
        ]

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                self.menu.cursor.down()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                self.menu.cursor.up()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.menu.cursor.select()

    def update(self):
        self.all_sprites.update()

    def draw(self):
        self.screen.fill(self.rgb.black)
        self.all_sprites.draw(self.screen)
        self.menu.items.draw()

    def run(self):
        while self.running:
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
