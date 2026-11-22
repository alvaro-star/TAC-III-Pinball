"""Obstáculos: círculo/pino e alvos com respostas diferentes para colisões."""
from ..physics.collision_manager import CollisionManager


class Obstacle:
    def __init__(self, x, y, radius, points, label):
        self.x, self.y, self.radius = float(x),float(y),float(radius)
        self.points, self.label = int(points),label
        self.flash = 0.0

    def update(self, dt):
        self.flash = max(0.0, self.flash-dt)

    def on_collide(self, ball):
        raise NotImplementedError


class Bumper(Obstacle):
    def on_collide(self, ball):
        collided = CollisionManager.circle_circle(ball,self.x,self.y,self.radius,
                                                   restitution=0.98,min_kick=500)
        if collided and ball.cooldown <= 0:
            self.flash = 0.16
            ball.cooldown = 0.14
            return self.points
        return 0


class Target(Obstacle):
    def on_collide(self, ball):
        collided = CollisionManager.circle_circle(ball,self.x,self.y,self.radius,
                                                   restitution=0.78,min_kick=130)
        if collided and ball.cooldown <= 0:
            self.flash = 0.22
            ball.cooldown = 0.18
            return self.points
        return 0


class Hole(Obstacle):
    def on_collide(self, ball):
        collided = CollisionManager.circle_circle(ball,self.x,self.y,self.radius,
                                                   restitution=0.75,min_kick=360)
        if collided and ball.cooldown <= 0:
            self.flash = 0.4
            ball.cooldown = 0.3
            return self.points
        return 0
