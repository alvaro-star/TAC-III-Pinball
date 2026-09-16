from .actuator_base import Actuator


class Flipper(Actuator):
    """Um dos 4 flippers do campo (esquerda/direita), acionado via InputHandler."""
    def __init__(self, x, y, side="left"):
        super().__init__(x, y)
        self.side = side
        self.angle = 0
        self.max_angle = 45 if side == "left" else -45
        self.speed = 720  # graus por segundo
        self.active = False

    def activate(self):
        self.active = True

    def release(self):
        self.active = False

    def update(self, dt):
        target = self.max_angle if self.active else 0
        step = self.speed * dt
        if self.angle < target:
            self.angle = min(self.angle + step, target)
        elif self.angle > target:
            self.angle = max(self.angle - step, target)

    def draw(self):
        pass
