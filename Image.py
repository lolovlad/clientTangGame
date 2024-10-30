import pygame
import os


class Image:
    def __init__(self, name_img):
        self.img = None
        self.name_img = name_img
        self._file_position = "files/images/"
        self._load_img()

    def _load_img(self):
        file = self._file_position + self.name_img
        if not os.path.exists(file):
            raise FileNotFoundError
        self.img = pygame.image.load(file)

    def rotate(self, angle):
        self.img = pygame.transform.rotate(self.img, angle)

    def resize(self, resize):
        self.img = pygame.transform.scale(self.img, resize)