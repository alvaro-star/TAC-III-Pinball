"""Mapeamento do teclado e do mouse - menus, editor de fases, flippers, lançador e ações globais."""
import pygame
from modulos.ui.menu import NAV_STATES

# Teclas das telas de menu, traduzidas para ações de Game.menu_action.
MENU_KEYS = {
    pygame.K_UP: 'up', pygame.K_w: 'up',
    pygame.K_DOWN: 'down', pygame.K_s: 'down',
    pygame.K_LEFT: 'left', pygame.K_a: 'left',
    pygame.K_RIGHT: 'right', pygame.K_d: 'right',
    pygame.K_RETURN: 'enter', pygame.K_KP_ENTER: 'enter',
    pygame.K_ESCAPE: 'back', pygame.K_BACKSPACE: 'back',
    # Listas de fases e de jogadores.
    pygame.K_e: 'edit', pygame.K_n: 'new', pygame.K_j: 'play',
    pygame.K_DELETE: 'delete', pygame.K_x: 'delete',
}

# Teclas 1-9 escolhem a peça na paleta do editor.
NUMBER_KEYS = {getattr(pygame, f'K_{i}'): i-1 for i in range(1, 10)}
NUMBER_KEYS.update({getattr(pygame, f'K_KP{i}'): i-1 for i in range(1, 10)})


class InputManager:
    def __init__(self):
        self.left = False
        self.right = False
        self.launch = False
        # Converte a posição do mouse na janela para coordenadas lógicas (definido pelo engine).
        self.to_logical = lambda pos: pos

    def handle(self, event, game):
        if event.type == pygame.QUIT:
            game.running = False
            return
        if game.state == 'text_input':
            self.handle_text(event, game)
            return
        if game.state == 'editing':
            self.handle_editor(event, game)
            return
        if event.type == pygame.KEYDOWN:
            k = event.key
            if k == pygame.K_m:
                game.toggle_sound()
            elif game.state == 'paused' and k == pygame.K_p:
                game.pause()
            elif game.state in NAV_STATES:
                if k in MENU_KEYS:
                    game.menu_action(MENU_KEYS[k])
            elif k in (pygame.K_a, pygame.K_LEFT):
                self.left = True
            elif k in (pygame.K_d, pygame.K_RIGHT):
                self.right = True
            elif k == pygame.K_SPACE:
                self.launch = True
            elif k == pygame.K_ESCAPE and game.state == 'gameover':
                game.back_to_menu()
            elif k in (pygame.K_p, pygame.K_ESCAPE):
                game.pause()
            elif k == pygame.K_r:
                game.start_game()
            elif k in (pygame.K_RETURN, pygame.K_KP_ENTER) and game.state == 'gameover':
                game.start_game()
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_a,pygame.K_LEFT):
                self.left = False
            elif event.key in (pygame.K_d,pygame.K_RIGHT):
                self.right = False
            elif event.key == pygame.K_SPACE:
                self.launch = False
                if game.state == 'playing':
                    game.launch()

    def handle_text(self, event, game):
        if event.type == pygame.TEXTINPUT:
            game.text_type(event.text)
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                game.text_action('enter')
            elif event.key == pygame.K_ESCAPE:
                game.text_action('back')
            elif event.key == pygame.K_BACKSPACE:
                game.text_action('erase')

    def handle_editor(self, event, game):
        if event.type == pygame.MOUSEMOTION:
            game.editor.cursor = self.to_logical(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
            game.editor_click(*self.to_logical(event.pos), event.button)
        elif event.type == pygame.MOUSEWHEEL:
            game.editor_command('cycle', -1 if event.y > 0 else 1)
        elif event.type == pygame.KEYDOWN:
            k = event.key
            if k in NUMBER_KEYS:
                game.editor_command('choose', NUMBER_KEYS[k])
            elif k in (pygame.K_TAB, pygame.K_e):
                game.editor_command('cycle', 1)
            elif k == pygame.K_q:
                game.editor_command('cycle', -1)
            elif k == pygame.K_z:
                game.editor_command('undo')
            elif k == pygame.K_ESCAPE:
                game.editor_command('menu')
            elif k == pygame.K_m:
                game.toggle_sound()
