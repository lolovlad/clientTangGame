from Image import Image

import pygame


class Bullet(pygame.sprite.Sprite):
    def __init__(self, obj: dict, window):
        super().__init__()
        self.img = Image('bullet.png')
        self.img.resize((20, 20))
        self.rect = self.img.img.get_rect()
        self.rect.center = (obj["position"]["x"], obj["position"]["y"])
        self.window = window
        self.position = pygame.math.Vector2(self.rect.centerx, self.rect.centery)

    def display(self):
        self.window.blit(self.img.img, self.rect)

    def set_new_position(self, data: dict):
        self.position.x, self.position.y = data["position"]["x"], data["position"]["y"]
        self.rect.center = round(self.position.x), round(self.position.y)
