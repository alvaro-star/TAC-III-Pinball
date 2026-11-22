"""Mapeamento do teclado - flippers esquerdo/direito, lançador e ações globais."""
import pygame


class InputManager:
    def __init__(self):
        self.left = False
        self.right = False
        self.launch = False

    def handle(self, event, game):
        if event.type == pygame.QUIT:
            game.running = False
            return
        if event.type == pygame.KEYDOWN:
            k = event.key
            if k in (pygame.K_a, pygame.K_LEFT):
                self.left = True
            elif k in (pygame.K_d, pygame.K_RIGHT):
                self.right = True
            elif k == pygame.K_SPACE:
                self.launch = True
            elif k in (pygame.K_p, pygame.K_ESCAPE):
                game.pause()
            elif k == pygame.K_m:
                game.audio.toggle_mute()
            elif k == pygame.K_r:
                game.start_game()
            elif k == pygame.K_RETURN and game.state in ('menu','gameover'):
                game.start_game()
            elif k in (pygame.K_1, pygame.K_2) and game.state == 'menu':
                game.player_count = int(event.unicode) if event.unicode in ('1','2') else (1 if k==pygame.K_1 else 2)
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_a,pygame.K_LEFT):
                self.left = False
            elif event.key in (pygame.K_d,pygame.K_RIGHT):
                self.right = False
            elif event.key == pygame.K_SPACE:
                self.launch = False
                if game.state == 'playing':
                    game.launch()
