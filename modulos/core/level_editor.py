"""Editor de fases sem dependência de pygame: peça escolhida, posicionar, remover e desfazer."""
import math
from modulos.core.levels import Level, PIECES, PIECE_KEYS, can_place

# Paleta na margem esquerda da tela (fora da mesa): uma peça por espaço.
PALETTE_X = 46
PALETTE_TOP = 158
PALETTE_STEP = 76
PALETTE_SIZE = 44
SHORT = {'bumper_azul': 'AZUL', 'bumper_dourado': 'DOURADO', 'bumper_rosa': 'ROSA',
         'bumper_vermelho': 'VERMELHO', 'bumper_pequeno': 'PEQUENO', 'alvo_10': 'ALVO 10',
         'alvo_25': 'ALVO 25', 'alvo_50': 'ALVO 50', 'buraco': 'BURACO'}


def palette_slot(index):
    """Centro do ícone da peça na paleta."""
    return PALETTE_X, PALETTE_TOP + index * PALETTE_STEP


def palette_hit(x, y):
    """Índice da peça clicada na paleta, ou None."""
    for i in range(len(PIECE_KEYS)):
        cx, cy = palette_slot(i)
        if abs(x - cx) <= PALETTE_STEP / 2 - 4 and abs(y - cy) <= PALETTE_STEP / 2:
            return i
    return None


class LevelEditor:
    def __init__(self, level):
        # Edita uma cópia: só vira arquivo ao salvar.
        self.level = Level(level.name, level.objects, level.path)
        self.piece_index = 0
        self.cursor = None  # posição lógica do mouse
        self.history = []
        self.dirty = False

    @property
    def piece(self):
        return PIECE_KEYS[self.piece_index]

    @property
    def objects(self):
        return self.level.objects

    def choose(self, index):
        if 0 <= index < len(PIECE_KEYS):
            self.piece_index = index

    def cycle(self, step):
        self.piece_index = (self.piece_index + step) % len(PIECE_KEYS)

    def valid_at(self, x, y):
        return can_place(self.objects, self.piece, x, y)

    def place(self, x, y):
        x, y = round(x), round(y)
        if not self.valid_at(x, y):
            return False
        obj = {'piece': self.piece, 'x': x, 'y': y}
        self.objects.append(obj)
        self.history.append(('add', obj))
        self.dirty = True
        return True

    def object_at(self, x, y):
        """Peça sob o ponto (a mais próxima), ou None."""
        hits = [(math.hypot(o['x'] - x, o['y'] - y), i) for i, o in enumerate(self.objects)
                if math.hypot(o['x'] - x, o['y'] - y) <= PIECES[o['piece']][2] + 4]
        return self.objects[min(hits)[1]] if hits else None

    def remove_at(self, x, y):
        obj = self.object_at(x, y)
        if obj is None:
            return False
        index = self.objects.index(obj)
        self.objects.remove(obj)
        self.history.append(('remove', obj, index))
        self.dirty = True
        return True

    def clear(self):
        if not self.objects:
            return
        self.history.append(('clear', list(self.objects)))
        self.objects.clear()
        self.dirty = True

    def undo(self):
        if not self.history:
            return False
        action = self.history.pop()
        if action[0] == 'add':
            self.objects.remove(action[1])
        elif action[0] == 'remove':
            self.objects.insert(action[2], action[1])
        else:
            self.objects[:] = action[1]
        self.dirty = bool(self.history)
        return True
