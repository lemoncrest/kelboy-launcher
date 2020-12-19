import pygame as p, random as r, time as t
import asyncio
import os

from core.settings import *

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=LOGGING_LEVEL)

class Lemon():

    async def async_run(self,screen):
        width, height = WIDTH, HEIGHT
        pos, vel = [0, 0], [1, 1]
        rectWidth, rectHeight = 130, 100

        pos[0], pos[1] = r.randint(200, 400), r.randint(200, 400)
        self.running = True
        while True:
            t.sleep(1.0/FRAMERATE)
            if self.running:
                pos[0] += vel[0]
                pos[1] += vel[1]
                if pos[0] > width or pos[0] < rectWidth: vel[0] = -vel[0]
                if pos[1] > height or pos[1] < rectHeight: vel[1] = -vel[1]
                screen.fill((0, 0, 0))
                screen.fill((255, 0, 0), (pos[0] - rectWidth, pos[1] - rectHeight, rectWidth, rectHeight))
                p.display.flip()
