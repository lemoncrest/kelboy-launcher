import pygame

from core.settings import *

class Keyboard(pygame.sprite.Sprite):

    def __init__(self, game):

        self.game = game
        self.groups = game.all_sprites
        self._layer = 6
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = pygame.Surface((width,height*0.5))
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect()
        self.rect.centery = height - (height / 4)
        self.rect.centerx = width / 2
        self.keys = [
            ["q","w","e","r","t","y","u","i","o","p"],
            ["a","s","d","f","g","h","j","k","l","@"],
            ["z","x","c","v","b","n","m",",",".","-"]
        ]

    def draw(self):
        counter = 0
        for x in range(0,len(self.keys)):
            counter = 0
            for y in range(0,len(self.keys[0])):
                counter += 1
                text_item = self.font.render(self.keys[x][y], False, (255,255,255))
                text_item_rect = text_item.get_rect()
                self.game.screen.blit(text_item, (self.menu.cursor.rect.left * 1.2, self.menu_init_y + (text_item_rect.height * counter)))
