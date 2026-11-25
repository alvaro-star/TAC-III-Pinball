"""A posição é calculada usando v_t=v_(t-1)+aΔt; p_t=p_(t-1)+v_tΔt."""
import math
from .collision_manager import Vector
from modulos.config.constants import GRAVITY, DRAG, MAX_SPEED


class TrajectoryController:
    def __init__(self, collision_manager):
        self.collision_manager = collision_manager
        # Multiplicador da gravidade ("velocidade de queda" nas configurações).
        self.gravity_scale = 1.0

    def step(self, ball, dt):
        if not ball.active or ball.ready:
            return
        ball.velocity.y += GRAVITY * self.gravity_scale * dt
        damping = math.exp(-DRAG * dt)
        ball.velocity.x *= damping
        ball.velocity.y *= damping
        speed = ball.velocity.magnitude()
        if speed > MAX_SPEED:
            ball.velocity = ball.velocity * (MAX_SPEED/speed)
        ball.position = ball.position + ball.velocity * dt
        ball.cooldown = max(0.0, ball.cooldown - dt)
        ball.flipper_cooldown = max(0.0, ball.flipper_cooldown-dt)
