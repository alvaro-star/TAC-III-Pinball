from ..constants import GRAVITY


class PhysicsEngine():
    """Aplica gravidade, atrito e quique sobre entidades fisicas, ex. Ball (RF3, RF4)."""
    def __init__(self, gravity=GRAVITY, friction=0.98, bounce=0.7):
        self.gravity = gravity
        self.friction = friction
        self.bounce = bounce

    def apply_gravity(self, entity, dt):
        entity.direction.y += self.gravity * dt

    def apply_friction(self, entity):
        entity.direction.x *= self.friction

    def apply_bounce(self, entity, normal):
        entity.direction = entity.direction.reflect(normal) * self.bounce

    def update(self, entity, dt):
        self.apply_gravity(entity, dt)
        self.apply_friction(entity)
        entity.rect.x += entity.direction.x * dt
        entity.rect.y += entity.direction.y * dt


physics_engine = PhysicsEngine()
