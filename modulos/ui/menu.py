"""Navegação dos menus (inicial, configurações, pausa, fases, jogadores, editor) sem pygame."""
from modulos.config.settings import ITEMS

MAIN_ITEMS = [
    ('novo', 'NOVO JOGO'),
    ('multi', 'MULTIPLAYER'),
    ('fases', 'EDITOR DE FASES'),
    ('jogador', 'MUDAR DE JOGADOR'),
    ('score', 'SCORE'),
    ('config', 'CONFIGURAÇÕES'),
    ('sair', 'SAIR'),
]

PAUSE_ITEMS = [
    ('continuar', 'CONTINUAR'),
    ('reiniciar', 'REINICIAR PARTIDA'),
    ('config', 'CONFIGURAÇÕES'),
    ('menu', 'MENU PRINCIPAL'),
    ('sair', 'SAIR DO JOGO'),
]

# Menu aberto com Esc dentro do editor de fases.
EDIT_ITEMS = [
    ('continuar', 'CONTINUAR EDITANDO'),
    ('salvar', 'SALVAR E SAIR'),
    ('jogar', 'SALVAR E JOGAR'),
    ('limpar', 'LIMPAR MESA'),
    ('descartar', 'SAIR SEM SALVAR'),
]

# Telas fora da partida (sem placar no HUD).
MENU_STATES = ('menu', 'scores', 'settings', 'levels', 'players',
               'editing', 'editor_menu', 'text_input')
# Telas navegadas com setas/Enter/Esc. 'editing' (mouse) e 'text_input' (digitação)
# têm tratamento próprio em InputManager.
NAV_STATES = ('menu', 'scores', 'settings', 'levels', 'players', 'editor_menu', 'paused')

# Última linha da tela de configurações: volta ao menu.
SETTINGS_BACK = len(ITEMS)


class Menu:
    def __init__(self):
        self.main_index = 0
        self.settings_index = 0
        self.pause_index = 0
        self.levels_index = 0
        self.players_index = 0
        self.edit_index = 0

    def move(self, screen, step, count=None):
        """count: tamanho das listas dinâmicas (fases e jogadores)."""
        if screen == 'menu':
            self.main_index = (self.main_index + step) % len(MAIN_ITEMS)
        elif screen == 'settings':
            self.settings_index = (self.settings_index + step) % (len(ITEMS) + 1)
        elif screen == 'paused':
            self.pause_index = (self.pause_index + step) % len(PAUSE_ITEMS)
        elif screen == 'editor_menu':
            self.edit_index = (self.edit_index + step) % len(EDIT_ITEMS)
        elif screen == 'levels' and count:
            self.levels_index = (self.levels_index + step) % count
        elif screen == 'players' and count:
            self.players_index = (self.players_index + step) % count

    def main_choice(self):
        return MAIN_ITEMS[self.main_index][0]

    def pause_choice(self):
        return PAUSE_ITEMS[self.pause_index][0]

    def edit_choice(self):
        return EDIT_ITEMS[self.edit_index][0]

    def settings_choice(self):
        """Chave da configuração selecionada, ou None na linha VOLTAR."""
        if self.settings_index == SETTINGS_BACK:
            return None
        return ITEMS[self.settings_index][0]
