import pygame
import time
from pygame.locals import *
from core.settings import *

def fade(screen, out=False, x_pos = 0, y_pos = 0, screenshot=None):
    fpsClock = pygame.time.Clock()
    alphaImg = pygame.image.load('resources/graphics/transparent.png').convert()
    dark_level_out = 256
    dark_level_in = 0
    if out:
        time.sleep(0.5)
        for i in range(0, FRAMES_OUT):
            alphaImg.set_alpha(dark_level_out)
            screen.blit(screenshot, (x_pos, y_pos))
            screen.blit(alphaImg, (x_pos, y_pos))
            pygame.display.update()
            fpsClock.tick(30)
            dark_level_out -= 256 / FRAMES_OUT

    else:
        for i in range(0, FRAMES_IN):
            alphaImg.set_alpha(dark_level_in)
            screen.blit(alphaImg, (x_pos, y_pos))
            pygame.display.update()
            fpsClock.tick(30)
            dark_level_in += 256 / FRAMES_IN
