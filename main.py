import os
import json
import time
import sys
import traceback

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
from core.effect.lemon import Lemon
from core.colors import *

import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=LOGGING_LEVEL)
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
        #movements and keys init
        self.downPushed = False
        self.upPushed = False
        self.leftPushed = False
        self.rightPushed = False
        self.joyUp = False
        self.joyDown = False
        self.joyLeft = False
        self.joyRight = False
        self.zPressed = False
        self.tPressed = False
        self.screensaver = False

    def loadAssets(self):
        self.all_sprites = pygame.sprite.LayeredUpdates()
        with open(os.path.join("resources/menus","main.json")) as jsonMenu:
            menu = json.load(jsonMenu)
            self.menu = Menu(self, menu)
            self.menu.dialog = Dialog(main=self,title="Launcher",message="Welcome to V1.0", dialogWidth=180,dialogHeight=160)
            self.menu.keyboard = None
            self.menu.lastMenu = "main"


    async def moves(self):
        logger.info("in-side async moves...")
        while self.running:
            await asyncio.sleep(KEY_SLEEP)  # wait until release time
            if self.downPushed:
                logger.debug("down...")
                #self.menu.cursor.down()
            if self.upPushed:
                logger.debug("up...")
                #self.menu.cursor.up()
            if self.zPressed:
                #for i in range(0,MAX_MENU_ITEMS):
                #    self.menu.cursor.up(force=True)
                self.zPressed = False
            if self.tPressed:
                #for i in range(0,MAX_MENU_ITEMS):
                #    self.menu.cursor.down(force=True)
                self.tPressed = False
            if self.leftPushed:
                logger.debug("left...")
                #self.menu.cursor.left()
                self.leftPushed = False
            if self.rightPushed:
                logger.debug("right...")
                #self.menu.cursor.right()
                self.rightPushed = False

            if JOYSTICK_ENABLE:
                if self.joyUp:
                    #self.menu.cursor.up()
                    self.joyUp = False
                if self.joyDown:
                    #self.menu.cursor.down()
                    self.joyDown = False
                if self.joyLeft:
                    #self.menu.cursor.left()
                    self.joyLeft = False
                if self.joyRight:
                    #self.menu.cursor.right()
                    self.joyRight = False
            else:
                self.joyUp = False
                self.joyDown = False
                self.joyLeft = False
                self.joyRight = False

    async def events(self,event_queue):
        logger.info("in-side events...")
        while self.running:
            #logger.debug("while (events)...")
            event = await event_queue.get()
            #logger.debug("events!!! %s" % str(event))
            self.lemon.running = False
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                #reset screensaver time to 0
                self.last = int(round(time.time())*1000)
                self.screensaver = False
                #logger.debug("key down: %s" % str(event.key))
                if event.key == pygame.K_DOWN:
                    self.downPushed = True
                    self.menu.cursor.down()
                elif event.key == pygame.K_UP:
                    self.upPushed = True
                    self.menu.cursor.up()
                elif event.key == pygame.K_RETURN or event.key == 0: #fix for wii motes, all buttons in python are 0 key
                    self.menu.cursor.select(self.screen)
                elif event.key == pygame.K_ESCAPE:
                    self.menu.cursor.back(self.screen)
                elif event.key == pygame.K_LEFT:
                    self.leftPushed = True
                    self.menu.cursor.left()
                elif event.key == pygame.K_RIGHT:
                    self.rightPushed = True
                    self.menu.cursor.right()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    self.downPushed = False
                elif event.key == pygame.K_UP:
                    self.upPushed = False
                elif event.key == pygame.K_LEFT:
                    self.leftPushed = False
                elif event.key == pygame.K_RIGHT:
                    self.rightPushed = False
            elif event.type == pygame.JOYBUTTONUP:
                if event.button == 11:  # up
                    self.upPushed = False
                elif event.button == 10:  # down
                    self.downPushed = False
            elif event.type == pygame.JOYBUTTONDOWN:
                #reset screensaver time to 0
                self.last = int(round(time.time())*1000)
                self.screensaver = False
                if event.button == 15:  # button A - enter
                    self.menu.cursor.select(self.screen)
                elif event.button == 14:  # button B - back
                    self.menu.cursor.back(self.screen)
                elif event.button == 3:  # Z
                    self.zPressed = True
                    for i in range(0,MAX_MENU_ITEMS):
                        self.menu.cursor.up(force=True)
                elif event.button == 2:  # T
                    self.tPressed = True
                    for i in range(0,MAX_MENU_ITEMS):
                        self.menu.cursor.down(force=True)
                elif event.button == 7:  # start
                    pass #TODO
                elif event.button == 6:  # select
                    pass #TODO
                elif event.button == 11:  # up
                    self.upPushed = True
                    self.menu.cursor.up()
                elif event.button == 10:  # down
                    self.downPushed = True
                    self.menu.cursor.down()
                elif event.button == 9:  # left
                    self.leftPushed = True
                    self.menu.cursor.left()
                elif event.button == 8:  # right
                    self.rightPushed = True
                    self.menu.cursor.right()
            elif JOYSTICK_ENABLE and event.type == pygame.JOYAXISMOTION:
                if event.value != 0.0 and (self.menu.keyboard==None or not self.menu.keyboard.show): #discarted joystick with keyboard and dead zone events
                    #reset screensaver time to 0
                    self.last = int(round(time.time())*1000)
                    self.screensaver = False
                    logger.debug("joy: %s value: %s, (%s,%s,%s,%s)" % ( str(event.axis),str(event.value),str(self.joyUp),str(self.joyDown),str(self.joyLeft),str(self.joyRight) ) )
                    if event.axis == 1:  # up and down
                        if event.value > 0.2 and not self.joyUp:
                            self.joyUp = True
                        elif event.value < -0.2 and not self.joyDown:
                            self.joyDown = True
                        else:
                            #reset joys up and down
                            self.joyUp = False
                            self.joyDown = False
                            self.upPushed = False
                            self.downPushed = False
                    elif event.axis == 0:  # left and right
                        if event.value > 0.2 and not self.joyRight:
                            self.joyRight = True
                        elif event.value < -0.2 and not self.joyLeft:
                            self.joyLeft = True
                        else:
                            self.rightPushed = False
                            self.leftPushed = False
                            self.joyLeft = False
                            self.joyRight = False
                else:
                    self.joyUp = False
                    self.joyDown = False
                    self.joyLeft = False
                    self.joyRight = False
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

        loop = asyncio.get_event_loop()
        event_queue = asyncio.Queue()

        #main loop
        pygame_task = loop.run_in_executor(None, self.pygame_event_loop, loop, event_queue)
        #events loop
        event_task = asyncio.ensure_future(self.events(event_queue))
        #draw loop
        draw_task = asyncio.ensure_future(self.async_run())
        #moves loop
        #moves_task = asyncio.ensure_future(self.moves())

        self.lemon = Lemon()

        #lemon_task = asyncio.ensure_future(self.lemon.async_run(self.screen))

        try:
            loop.run_forever()
        except Exception as exc:
            logger.error("1: "+str(exc))
            exc_info = sys.exc_info()
            logger.error(exc_info)
            traceback.print_exception(*exc_info)
        finally:
            self.running = False
            pygame_task.cancel()
            draw_task.cancel()
            event_task.cancel()
            #moves_task.cancel()

        pygame.quit()

    async def async_run(self):
        logger.info("inside async_run...")
        current_time = 0
        try:
            self.screensaver = False #TODO
            self.last = int(round(time.time())*1000)
            logger.debug("LAST time is %s" % str( int(round(time.time())*1000) ) )
            while self.running:
                '''
                if self.last+SCREENSAVER_TIME < int(round(time.time())*1000):
                    self.screensaver = True
                    logger.debug("NOW SCREENSAVER time is %s" % str( int(round(time.time())*1000) ) )
                if self.screensaver:
                    rand = randint(1, 3)
                    if(rand==1):
                        SnowBall().launchSnowBalls()
                    elif (rand == 2):
                        RotatingCube().run()
                    else:
                        Matrix(surface=pygame.display.set_mode((WIDTH,HEIGHT)),clock=pygame.time.Clock()).run()

                    self.lemon.running = True
                    self.last = int(round(time.time())*1000)
                    logger.debug("NEXT LAST time is %s" % str( int(round(time.time())*1000) ) )
                    self.screensaver = False
                '''

                #removed old flip with new tick
                #self.clock.tick(FRAMERATE)
                last_time, current_time = current_time, time.time()
                await asyncio.sleep(1 / FRAMERATE )  # tick
                pygame.display.flip()

                #self.events() #removed from this thread
                self.update()
                self.draw()

        except Exception as ex:
            logger.error("2: "+str(ex))
            exc_info = sys.exc_info()
            logger.error(exc_info)
            traceback.print_exception(*exc_info)
            logger.error(str(exc_info.__traceback__))


main = Main()
#while main.running:
main.run()
pygame.quit()
