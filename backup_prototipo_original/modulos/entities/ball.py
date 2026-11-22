"""Bola: usa TrajectoryController em vez de implementar sua física internamente."""
from ..constants import BALL_RADIUS, LAUNCH_X, LAUNCH_Y
from ..physics.collision_manager import Vector


class Ball:
    def __init__(self, trajectory, x=LAUNCH_X, y=LAUNCH_Y, ready=True):
        self.trajectory = trajectory
        self.position = Vector(float(x), float(y))
        self.velocity = Vector()
        self.radius = BALL_RADIUS
        self.ready = ready
        self.active = True
        self.cooldown = 0.0
        self.flipper_cooldown = 0.0
        self.seconds_still = 0.0

    def launch(self, force):
        if not self.ready:
            return False
        self.ready = False
        self.velocity = Vector(-45.0, -float(force))
        return True

    def update(self, dt):
        self.trajectory.step(self, dt)
