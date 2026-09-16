import pygame
from ..constants import GRAVITY
from .collision_manager import CollisionManager


class TrajectoryController():
    """Calcula a trajetoria da bola em funcao do tempo, com base em equacoes
    de cinematica (MRUV) e na 2a Lei de Newton (forca = massa x aceleracao).
    Tambem gerencia a deteccao de colisoes contra obstaculos, flippers e tiles
    do stage atual, atraves do seu proprio CollisionManager."""
    def __init__(self, gravity=GRAVITY):
        self.gravity = gravity
        self.elapsed = 0.0

        # Composicao: o controle de trajetoria possui o collision manager do projeto
        self.collision_manager = CollisionManager()

    def acceleration(self, force: pygame.math.Vector2, mass: float):
        # 2a Lei de Newton: a = F / m
        if not mass:
            return pygame.math.Vector2(0, 0)
        return force / mass

    def position(self, p0: pygame.math.Vector2, v0: pygame.math.Vector2, a: pygame.math.Vector2, t: float):
        # Equacao de posicao do MRUV: s = s0 + v0*t + 1/2 * a * t^2
        return p0 + v0 * t + a * 0.5 * (t ** 2)

    def velocity(self, v0: pygame.math.Vector2, a: pygame.math.Vector2, t: float):
        # Equacao de velocidade do MRUV: v = v0 + a*t
        return v0 + a * t

    def update(self, ball, dt, colliders=None):
        """Avanca a trajetoria da bola em dt segundos e resolve colisoes contra colliders."""
        self.elapsed += dt

        # Forca peso: P = m * g (unica forca considerada por enquanto)
        weight_force = pygame.math.Vector2(0, self.gravity * ball.mass)
        a = self.acceleration(weight_force, ball.mass)

        p0 = pygame.math.Vector2(ball.rect.center)
        v0 = ball.direction

        ball.direction = self.velocity(v0, a, dt)
        new_center = self.position(p0, v0, a, dt)
        ball.rect.center = (new_center.x, new_center.y)

        if colliders:
            for obstacle in self.collision_manager.check(ball, colliders):
                ball.on_collide(obstacle)
