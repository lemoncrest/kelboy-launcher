import pygame
from core.utils import Utils

utils = Utils()
utils.initJoysticks()
start = False
select = False
up = False
down = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 7:  # start
                start = True
            elif event.button == 6:  # select
                select = True
            elif event.button == 11:  # up
                up = True
            elif event.button == 10:  # down
                down = True
        elif event.type == pygame.JOYBUTTONUP:
            if event.button == 7:  # start
                start = False
            elif event.button == 6:  # select
                select = False
            elif event.button == 11:  # up
                up = False
            elif event.button == 10:  # down
                down = False

        print("ev: %s %s %s %s" % (str(start),str(select),str(up),str(down)))

        if select and up:
            print("bundle up")
        if select and down:
            print("bundle down")

        if start and up:
            print("bundle2 up")
        if start and down:
            print("bundle2 down")
