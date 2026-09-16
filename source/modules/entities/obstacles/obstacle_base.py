import pygame


class Obstacle():
    """Classe abstrata para obstaculos que reagem a colisao com a bola e concedem pontos."""
    def __init__(self, x, y, points=0):
        self.rect = pygame.Rect(x, y, 0, 0)
        self.points = points

    def on_collide(self, ball):
        raise NotImplementedError

    def draw(self):
        raise NotImplementedError
