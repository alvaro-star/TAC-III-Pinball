from .obstacle_base import Obstacle


class Target(Obstacle):
    """Alvo fixo que concede bonus de pontuacao ao ser atingido."""
    def __init__(self, x, y, points=50):
        super().__init__(x, y, points)
        self.hit = False

    def on_collide(self, ball):
        self.hit = True
        return self.points

    def draw(self):
        pass
