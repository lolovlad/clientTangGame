import pygame
from math import cos, sin


class Muzzle:
    def __init__(self, window, direction, position_muzzle, position_tank, size):
        self.window = window
        self._direction = direction
        self.rect = pygame.rect.Rect(0, 0, size, size)
        self.rect.center = position_muzzle.x, position_muzzle.y
        self.position = pygame.math.Vector2(self.rect.center)

        self._rect_pivot = pygame.rect.Rect(0, 0, 5, 5)
        self._rect_pivot.center = position_tank.x, position_tank.y

        self._angle = 180

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, val):
        self._direction = pygame.math.Vector2(val)

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, val):
        if -360 <= self._angle + val <= 360:
            self._angle += val
        else:
            self._angle = 0
        self.rotate(self._angle)

    @property
    def rect_pivot(self):
        return self._rect_pivot

    @rect_pivot.setter
    def rect_pivot(self, val):
        self._rect_pivot = val

    def display(self):
        pygame.draw.rect(self.window, (255, 0, 0), self.rect)

    def move(self):
        self.position += (self._direction * self.speed)
        self.rect.center = round(self.position.x), round(self.position.y)

    def rotate(self, angle):
        angle = angle * (3.14 / 180)
        '''
        X = (x — x0) * cos(alpha) — (y — y0) * sin(alpha) + x0;
        Y = (x — x0) * sin(alpha) + (y — y0) * cos(alpha) + y0;
        '''
        centerx = (self.position.x - self.rect_pivot.centerx) * cos(angle) - (self.position.y - self.rect_pivot.centery) * sin(angle) + self.rect_pivot.centerx
        centery = (self.position.x - self.rect_pivot.centerx) * sin(angle) - (self.position.y - self.rect_pivot.centery) * cos(angle) + self.rect_pivot.centery
        self.rect.center = int(centerx), int(centery)