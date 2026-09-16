import pygame
from ..utils import utils
from ..physics.trajectory_controller import TrajectoryController
from ..effects.score.score_manager import score_manager
from ..effects.score.bonus_rules import bonus_rules


class Ball():
    """Bola do pinball: fisica, colisao e renderizacao (item 5 - substitui/renomeia Player)."""
    def __init__(self, x, y, radius=10, mass=1.0):
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, pygame.Color("white"), (radius, radius), radius)
        self.rect = self.image.get_frect(center=(x, y))

        # Converte e guarda o ID da GPU
        self.texture_id = utils.surface_to_texture(self.image)

        self.direction = pygame.math.Vector2(0, 0)
        self.mass = mass

        # Composicao: a bola delega o calculo de trajetoria (forcas/cinematica)
        # e a deteccao de colisoes contra obstaculos ao TrajectoryController
        self.trajectory = TrajectoryController()

    def update(self, dt, colliders=None):
        self.trajectory.update(self, dt, colliders)

    def on_collide(self, obstacle):
        """Processa o resultado de uma colisao contra um obstaculo do stage atual."""
        result = obstacle.on_collide(self)
        if isinstance(result, (int, float)):
            bonus_rules.register_hit()
            score_manager.add_points(bonus_rules.apply(result))
        return result

    def draw(self):
        x, y, w, h = self.rect.x, self.rect.y, self.rect.w, self.rect.h
        utils.draw_textured_quad(self.texture_id, x, y, w, h)
