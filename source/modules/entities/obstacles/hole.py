from .obstacle_base import Obstacle


class Hole(Obstacle):
    """Buraco que captura a bola e troca o ambiente/nivel atual."""
    def __init__(self, x, y, next_level=None):
        super().__init__(x, y, points=0)
        self.next_level = next_level

    def on_collide(self, ball):
        return self.next_level

    def draw(self):
        pass
