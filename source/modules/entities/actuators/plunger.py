from .actuator_base import Actuator


class Plunger(Actuator):
    """Canhao de impulso: acumula forca e lanca a bola (RF5)."""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.charge = 0.0
        self.max_force = 1500

    def charge_up(self, dt):
        self.charge = min(self.charge + dt, 1.0)

    def release(self):
        force = self.charge * self.max_force
        self.charge = 0.0
        return force

    def activate(self):
        return self.release()

    def update(self, dt):
        pass

    def draw(self):
        pass
