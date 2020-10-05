import os
import json
import time

import asyncio

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
from random import randint

from core.component.dialog import Dialog

from core.settings import *
from core.menu import Menu
from core.effect.snow import SnowBall
from core.effect.matrix import Matrix
from core.effect.cube import RotatingCube
from core.colors import *

import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=logging.DEBUG)
logger = logging.getLogger(__name__)

from core.utils import Utils

class Main():

    def __init__(self):

        disp_no = os.getenv("DISPLAY")
        if disp_no:
            logger.debug("I'm running under X display = {0}".format(disp_no))

        # Check which frame buffer drivers are available
        # Start with fbcon since directfb hangs with composite output
        drivers = ['fbcon', 'directfb', 'svgalib']
        found = False
        pygame.init()
        pygame.display.init()
        '''
        for driver in drivers:
            # Make sure that SDL_VIDEODRIVER is set
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pygame.display.init()
            except pygame.error:
                logger.debug('Driver: {0} failed.'.format(driver))
                continue
            found = True
            break
        '''
        pygame.font.init()
        pygame.mouse.set_visible(0) #hide mouse
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        #self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption('Menu')
        self.clock = pygame.time.Clock()
        self.running = True
        self.loadAssets()
        logger.debug("launch joystics init...")
        utils = Utils()
        utils.initJoysticks()
        #disable mouse
        pygame.event.set_blocked(pygame.MOUSEMOTION)

    def loadAssets(self):
        self.all_sprites = pygame.sprite.LayeredUpdates()
        with open(os.path.join("resources/menus","main.json")) as jsonMenu:
            menu = json.load(jsonMenu)
            self.menu = Menu(self, menu)
            self.menu.dialog = Dialog(main=self,title="Test revision",message="not final rev.", dialogWidth=180,dialogHeight=160)
            self.menu.keyboard = None
            self.menu.lastMenu = "main"

    async def events(self,event_queue):
        logger.info("in-side events...")
        while self.running:
            logger.debug("while (events)...")
            event = await event_queue.get()
            logger.debug("events!!!")
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
                if event.button == 15:  # button A - enter
                    self.menu.cursor.select(self.screen)
                elif event.button == 14:  # button B - back
                    pass #TODO
                elif event.button == 7:  # start
                    pass #TODO
                elif event.button == 6:  # select
                    pass #TODO
                elif event.button == 11:  # up
                    self.menu.cursor.up()
                elif event.button == 10:  # down
                    self.menu.cursor.down()
                elif event.button == 9:  # left
                    self.menu.cursor.left()
                elif event.button == 8:  # right
                    self.menu.cursor.right()
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
        logger.info("ended... out-side events...")

    def update(self):
        self.all_sprites.update()

    def draw(self):
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        self.menu.items.draw()
        self.menu.status.draw()
        if self.menu and self.menu.dialog:
            self.menu.dialog.draw()




    def pygame_event_loop(self,loop, event_queue):
        logger.info("inside pygame_event_loop...")
        while self.running:
            event = pygame.event.wait()
            asyncio.run_coroutine_threadsafe(event_queue.put(event), loop=loop)

    def run(self):
        logger.info("inside run...")
        self.running = True
        #asyncio.run(self.async_run())
        loop = asyncio.get_event_loop()
        event_queue = asyncio.Queue()

        #main loop
        pygame_task = loop.run_in_executor(None, self.pygame_event_loop, loop, event_queue)
        #events loop
        event_task = asyncio.ensure_future(self.events(event_queue))
        #draw loop
        draw_task = asyncio.ensure_future(self.async_run())

        try:
            loop.run_forever()
        except Exception as exc:
            logger.error(str(exc))
        finally:
            pygame_task.cancel()
            draw_task.cancel()
            event_task.cancel()

        pygame.quit()

    async def async_run(self):
        logger.info("inside async_run...")
        current_time = 0
        try:
            self.screensaver = False #TODO
            self.last = int(round(time.time())*1000)
            while self.running:
                if self.last+SCREENSAVER_TIME < int(round(time.time())*1000):
                    self.screensaver = True
                if self.screensaver:
                    rand = randint(1, 3)
                    if(rand==1):
                        SnowBall().launchSnowBalls()
                    elif (rand == 2):
                        RotatingCube().run()
                    else:
                        Matrix(surface=pygame.display.set_mode((WIDTH,HEIGHT)),clock=pygame.time.Clock()).run()
                    self.last = int(round(time.time())*1000)
                    self.screensaver = False

                #removed old flip with new tick
                #self.clock.tick(FRAMERATE)
                last_time, current_time = current_time, time.time()
                await asyncio.sleep(1 / FRAMERATE - (current_time - last_time))  # tick
                pygame.display.flip()

                #self.events() #removed from this thread
                self.update()
                self.draw()

        except Exception as ex:
            logger.error(str(ex))


main = Main()
#while main.running:
main.run()
pygame.quit()
