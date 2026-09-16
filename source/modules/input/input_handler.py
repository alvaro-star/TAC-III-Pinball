import pygame


class InputHandler():
    """Traduz o teclado em comandos de gameplay: flippers e forca de lancamento (RF2, RF5)."""
    def __init__(self):
        self.left_flipper = False
        self.right_flipper = False
        self.plunger_charge = 0.0

    def update(self, dt):
        keys = pygame.key.get_pressed()

        self.left_flipper = bool(keys[pygame.K_LEFT] or keys[pygame.K_z])
        self.right_flipper = bool(keys[pygame.K_RIGHT] or keys[pygame.K_SLASH])

        if keys[pygame.K_SPACE]:
            self.plunger_charge = min(self.plunger_charge + dt, 1.0)


input_handler = InputHandler()
