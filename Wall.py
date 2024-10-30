import pygame
from Image import Image


class Wall:
    def __init__(self, img, left, top, window, type_wall, size=(30, 30)):

        self.img = Image(img)
        self.img.resize(size)
        self.rect = self.img.img.get_rect()
        self.rect.left = left
        self.rect.top = top
        self.window = window

    def display(self): 
        self.window.blit(self.img.img, self.rect)

    def move(self):
        pass