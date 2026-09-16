import pygame


class Actuator():
    """Classe abstrata para atuadores controlados pelo jogador (flippers, plunger)."""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 0, 0)

    def activate(self):
        raise NotImplementedError

    def update(self, dt):
        raise NotImplementedError

    def draw(self):
        raise NotImplementedError
