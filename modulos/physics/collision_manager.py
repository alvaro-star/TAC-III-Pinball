"""Detecção de contatos e resolução de colisões sem dependências gráficas."""
import math
from dataclasses import dataclass


@dataclass
class Vector:
    x: float = 0.0
    y: float = 0.0

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, factor):
        return Vector(self.x * factor, self.y * factor)

    __rmul__ = __mul__

    def __truediv__(self, factor):
        return Vector(self.x / factor, self.y / factor)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def magnitude(self):
        return math.hypot(self.x, self.y)

    def normalized(self):
        m = self.magnitude()
        return self / m if m > 1.0e-9 else Vector(0.0, -1.0)


def closest_point(point, a, b):
    """Projeção limitada ao segmento AB."""
    d = b - a
    l2 = d.dot(d)
    t = max(0.0, min(1.0, (point-a).dot(d)/l2)) if l2 else 0.0
    return a + d*t


class CollisionManager:
    @staticmethod
    def circle_circle(ball, cx, cy, radius, restitution=0.90, min_kick=0.0):
        delta = ball.position - Vector(cx, cy)
        dist = delta.magnitude()
        overlap = ball.radius + radius - dist
        if overlap <= 0:
            return False
        n = delta.normalized()
        ball.position = ball.position + n * (overlap + 0.2)
        approach = ball.velocity.dot(n)
        if approach < 0:
            ball.velocity = ball.velocity - n * ((1.0 + restitution) * approach)
        if min_kick and ball.velocity.dot(n) < min_kick:
            ball.velocity = ball.velocity + n * (min_kick - ball.velocity.dot(n))
        return True

    @staticmethod
    def circle_inside_arch(ball, cx, cy, radius, restitution=0.2):
        """Mantém a bola sob um teto semicircular, preservando o deslizamento tangencial."""
        if ball.position.y > cy:
            return False
        delta = ball.position - Vector(cx, cy)
        distance = delta.magnitude()
        limit = radius - ball.radius
        if distance <= limit:
            return False
        n = delta / distance
        ball.position = Vector(cx, cy) + n * limit
        outward = ball.velocity.dot(n)
        if outward > 0:
            ball.velocity = ball.velocity - n * ((1.0 + restitution) * outward)
        return True

    @staticmethod
    def circle_segment(ball, a, b, restitution=0.84, moving=Vector()):
        q = closest_point(ball.position, a, b)
        delta = ball.position - q
        distance = delta.magnitude()
        if distance >= ball.radius:
            return False
        if distance <= 1e-8:
            tangent = (b-a).normalized()
            n = Vector(-tangent.y, tangent.x)
            if (ball.velocity - moving).dot(n) > 0:
                n = n * -1
        else:
            n = delta/distance
        ball.position = ball.position + n * (ball.radius-distance+0.15)
        relative = ball.velocity - moving
        approach = relative.dot(n)
        if approach < 0:
            ball.velocity = ball.velocity - n * ((1.0+restitution)*approach)
        return True
