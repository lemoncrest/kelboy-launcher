import pygame, pygame.image, numpy
from pygame.surfarray import *
from pygame.locals import *
from core.settings import *
RES = (WIDTH,HEIGHT)
FRAMES = int(FRAMERATE/4) #15 times

def take_screenshot(screen):
    screen_copy = screen.copy()
    screen_copy.blit(screen_copy, (0, 0))
    return screen_copy


def pixelate(screen, out=False):
    fpsClock = pygame.time.Clock()
    image = take_screenshot(screen)
    image_buf = pygame.surfarray.array2d(image)
    pixel_chunk = 4
    screen.blit(image, (0, 0))
    if out:
        for i in range(0, FRAMES):
            pixelfade(screen, image_buf, pixel_chunk, 0, 0)
            pygame.display.update()
            fpsClock.tick(FRAMERATE)
            pixel_chunk += 2

    else:
        pixel_chunk = pixel_chunk * FRAMES + 2
        for i in range(0, FRAMES):
            pixelfade(screen, image_buf, pixel_chunk, 0, 0)
            pygame.display.update()
            fpsClock.tick(FRAMERATE)
            pixel_chunk -= 2


def pixelfade(dest, src, size, x_pos, y_pos):
    for y in range(0, RES[1], size):
        for x in range(0, RES[0], size):
            rtile = pygame.Rect([x + x_pos, y + y_pos, size, size])
            colour = src[x][y]
            dest.fill(int(colour), rtile)
