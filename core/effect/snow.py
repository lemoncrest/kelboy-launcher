import pygame
import sys
import random
from core.colorpalette import *
from core.settings import *


class SnowBall():
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((width, height))

        self.yPos = 0
        self.xPos = random.randint(5, width-5)

        self.fpsClock = pygame.time.Clock()

    def fall(self):
        self.yPos += 2

    def draw(self):
        color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        #TODO change with rect or triangles with random
        pygame.draw.circle(self.screen, color, (self.xPos, self.yPos), 3, 0)


    def launchSnowBalls(self):

        snowMatrix = []

        exit = False
        while not exit:
            self.screen.fill(RGBColors().black)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    exit = True

            snowMatrix.append(SnowBall())
            for snow in snowMatrix:
                snow.fall()
                snow.draw()
                if snow.yPos > height:
                    snowMatrix.remove(snow)

            pygame.display.update()  # update the display
            self.fpsClock.tick(frameRate)
            #pygame.time.wait(25)
