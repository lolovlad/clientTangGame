from Image import Image
import pygame


class ObjectMap(pygame.sprite.Sprite):
    def __init__(self, window, image, size, position, type_obj=0):
        super().__init__()
        self.window = window
        self.img = Image(image)
        self.img.resize(size)
        self.rect = self.img.img.get_rect()
        self.rect.left, self.rect.top = position
        self.type_obj = type_obj

    def get_rect(self):
        return self.rect

    def set_position(self, position):
        self.rect.left, self.rect.top = position

    def get_position(self):
        return self.rect.left, self.rect.top

    def display(self):
        self.window.blit(self.img.img, self.rect)



