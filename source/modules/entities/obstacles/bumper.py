from .obstacle_base import Obstacle


class Bumper(Obstacle):
    """Obstaculo que concede bonus de pontuacao ao ser atingido pela bola (RF8)."""
    def __init__(self, x, y, points=100):
        super().__init__(x, y, points)

    def on_collide(self, ball):
        return self.points

    def draw(self):
        pass
