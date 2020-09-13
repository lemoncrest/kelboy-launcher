import pygame
from core.settings import *
from core.colors import *
import string
from random import choice, randint

class Matrix():

    def __init__(self,surface=None,clock=None):

        pygame.display.init()
        pygame.font.init()
        self.fontSize = 8
        self.font = pygame.font.Font(None, self.fontSize)

        self.width = WIDTH
        self.height = HEIGHT

        self.surface = surface
        self.clock = clock

        self.fall = []
        self.sizes = []
        self.waits = []
        for x in range(int(WIDTH/self.fontSize)):

            size = randint(1, 30)
            fall = randint(0, int(HEIGHT/self.fontSize)*2) - int(HEIGHT/self.fontSize)
            wait = randint(0, self.fontSize)
            self.fall.append(fall)
            self.sizes.append(size)
            self.waits.append(wait)


    def matrix(self):
        self.printable = string.ascii_letters + string.digits + string.punctuation
        self.randomString = ''
        for i in range(int(WIDTH/self.fontSize)):
            self.randomString += choice(self.printable)

    def water_fall(self):

        for x in range(int(WIDTH/self.fontSize)):
            y = self.fall[x]
            size = self.sizes[x]
            if self.waits[x] > 0:
                self.waits[x]-=1
                self.sizes[x] += 1
            elif y < (WIDTH/self.fontSize):
                y += 1
            elif y >= (WIDTH/self.fontSize):
                size = randint(1, 50)
                fall = 0 - size #randint(0, int(WINDOW_SIZE[1] / self.fontSize))  # - int(WINDOW_SIZE[1] / self.fontSize)
                wait = randint(0, self.fontSize)
                y = fall
                self.waits[x] = wait

            self.fall[x] = y
            self.sizes[x] = size


    def run(self):
        exit = False
        pygame.event.clear()
        while not exit:
            events = pygame.event.get()
            if len(events) > 0:
                exit = True
            self.clock.tick(FRAMERATE)
            self.surface.fill(BLACK)
            self.water_fall()
            for x in range(0,int(WIDTH/self.fontSize)):

                size = self.sizes[x]
                self.matrix()
                if self.waits[x] > 0:
                    self.sizes[x] += 1
                for y in range(0,int(HEIGHT/self.fontSize)):
                    if y >= self.fall[x] and size>0:
                        txt = self.font.render(self.randomString[y], True,GREEN)
                        self.surface.blit(txt, (x*self.fontSize, y*self.fontSize))
                        size-=1

            pygame.display.flip()
