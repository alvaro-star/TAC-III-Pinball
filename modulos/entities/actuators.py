"""Atuadores comuns: flippers e lançador (herdam de Actuator)."""
import math
from ..physics.collision_manager import Vector


class Actuator:
    def activate(self, active=True):
        raise NotImplementedError


class Flipper(Actuator):
    def __init__(self, side, pivot):
        self.side = side
        self.pivot = Vector(*pivot)
        self.length = 94.0
        self.radius = 12.0
        self.rest = 0.32 if side == 'left' else math.pi-0.32
        self.pressed = -0.46 if side == 'left' else math.pi+0.46
        self.angle = self.rest
        self.active = False
        self.angular_velocity = 0.0

    def activate(self, active=True):
        self.active = bool(active)

    def update(self, dt):
        desired = self.pressed if self.active else self.rest
        difference = desired-self.angle
        delta = max(-17.0*dt, min(17.0*dt, difference))
        self.angle += delta
        self.angular_velocity = delta/dt if dt else 0

    @property
    def swinging_up(self):
        """True enquanto o flipper sobe (esquerdo gira no sentido negativo, direito no positivo)."""
        direction = -1 if self.side == 'left' else 1
        return self.angular_velocity*direction > 0.5

    @property
    def tip(self):
        return self.pivot + Vector(math.cos(self.angle), math.sin(self.angle))*self.length

    def moving_at(self, point):
        arm = point-self.pivot
        return Vector(-self.angular_velocity*arm.y, self.angular_velocity*arm.x)


class Plunger(Actuator):
    def __init__(self):
        self.charge = 0.0
        self.active = False

    def activate(self, active=True):
        self.active = bool(active)

    def update(self, dt):
        if self.active:
            self.charge = min(1.0, self.charge + dt/1.45)

    def release(self):
        force = 1010.0 + self.charge*490.0
        self.charge = 0.0
        self.active = False
        return force
