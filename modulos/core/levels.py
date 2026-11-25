"""Fases do pinball em JSON (mesmo formato de mapa do protótipo: data/level1.json).

A fase padrão fica em data/fases/padrao.json e é gerada por create_default_level()
quando o arquivo não existe, como Level1.create_first_map() fazia com level1.json.
As fases criadas no editor usam o mesmo formato e ficam em storage/fases/.
"""
import json
import math
import re
from pathlib import Path
from modulos.config.constants import (WIDTH, HEIGHT, LEFT, LANE_LEFT, TOP,
                                      ARCH_CENTER_X, ARCH_CENTER_Y, ARCH_RADIUS)
from modulos.entities.obstacles import Bumper, Target, Hole

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LEVEL_FILE = ROOT / 'data' / 'fases' / 'padrao.json'
DEFAULT_NAME = 'PADRÃO'
LAYER = 'Obstáculos'

# Catálogo de peças que o editor pode posicionar:
# chave -> (rótulo, classe, raio, pontos, sprite do atlas).
PIECES = {
    'bumper_azul': ('BUMPER AZUL', Bumper, 33, 100, 'bumper_blue'),
    'bumper_dourado': ('BUMPER DOURADO', Bumper, 33, 100, 'bumper_gold'),
    'bumper_rosa': ('BUMPER ROSA GRANDE', Bumper, 36, 100, 'bumper_pink'),
    'bumper_vermelho': ('BUMPER VERMELHO', Bumper, 24, 100, 'bumper_red'),
    'bumper_pequeno': ('BUMPER AZUL PEQUENO', Bumper, 24, 100, 'bumper_blue'),
    'alvo_10': ('ALVO 10', Target, 24, 250, 'target10'),
    'alvo_25': ('ALVO 25', Target, 24, 250, 'target25'),
    'alvo_50': ('ALVO 50', Target, 24, 250, 'target50'),
    'buraco': ('BURACO BÔNUS', Hole, 24, 300, None),
}
PIECE_KEYS = list(PIECES)

DEFAULT_OBJECTS = [
    ('alvo_25', 237, 222), ('alvo_10', 363, 196), ('alvo_50', 483, 222),
    ('bumper_azul', 284, 342), ('bumper_dourado', 444, 340), ('bumper_rosa', 363, 257),
    ('bumper_vermelho', 192, 507), ('bumper_pequeno', 524, 505),
    ('buraco', 360, 447),
]

# Área livre para peças: acima dos slingshots e fora do canal de lançamento.
PLACE_BOTTOM = 600
MARGIN = 4


class Level:
    def __init__(self, name, objects=None, path=None, builtin=False):
        self.name = name
        self.objects = [dict(o) for o in objects or []]  # {'piece','x','y'}
        self.path = Path(path) if path else None
        self.builtin = builtin

    def to_json(self):
        return {
            'height': HEIGHT, 'width': WIDTH,
            'layers': [{'name': LAYER, 'objects': self.objects, 'opacity': 1,
                        'visible': True, 'x': 0, 'y': 0}],
            'name': self.name, 'orientation': 'orthogonal', 'type': 'pinball', 'version': '1.0',
        }

    @classmethod
    def from_json(cls, data, path=None, builtin=False):
        if not isinstance(data, dict):
            raise ValueError('fase inválida')
        objects = []
        for layer in data.get('layers', []):
            if not isinstance(layer, dict):
                continue
            for o in layer.get('objects', []):
                # Peças desconhecidas ou sem coordenadas numéricas são ignoradas.
                if (isinstance(o, dict) and o.get('piece') in PIECES and
                        all(isinstance(o.get(k), (int, float)) and not isinstance(o.get(k), bool)
                            for k in ('x', 'y'))):
                    objects.append({'piece': o['piece'], 'x': round(o['x']), 'y': round(o['y'])})
        name = str(data.get('name') or (path.stem if path else 'FASE'))
        return cls(name, objects, path, builtin)

    def build(self):
        """Cria as entidades da mesa: (bumpers, targets, holes)."""
        bumpers, targets, holes = [], [], []
        for o in self.objects:
            label, kind, radius, points, sprite = PIECES[o['piece']]
            entity = kind(o['x'], o['y'], radius, points, o['piece'], sprite)
            {Bumper: bumpers, Target: targets, Hole: holes}[kind].append(entity)
        return bumpers, targets, holes


def default_level():
    return Level(DEFAULT_NAME, [{'piece': p, 'x': x, 'y': y} for p, x, y in DEFAULT_OBJECTS],
                 DEFAULT_LEVEL_FILE, builtin=True)


def create_default_level(path=DEFAULT_LEVEL_FILE):
    """Gera o arquivo da fase padrão (equivalente a Level1.create_first_map)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(default_level().to_json(), indent=4, ensure_ascii=False),
                    encoding='utf-8')


def load_level(path, builtin=False):
    path = Path(path)
    return Level.from_json(json.loads(path.read_text(encoding='utf-8')), path, builtin)


def can_place(objects, piece, x, y, ignore=None):
    """True se a peça cabe na mesa, longe das paredes, do canal e das outras peças."""
    radius = PIECES[piece][2]
    if x - radius < LEFT + MARGIN or x + radius > LANE_LEFT - MARGIN:
        return False
    if y - radius < TOP + MARGIN or y + radius > PLACE_BOTTOM:
        return False
    if y < ARCH_CENTER_Y and math.hypot(x - ARCH_CENTER_X, y - ARCH_CENTER_Y) > ARCH_RADIUS - radius - MARGIN:
        return False
    for o in objects:
        if o is ignore:
            continue
        if math.hypot(o['x'] - x, o['y'] - y) < radius + PIECES[o['piece']][2] + MARGIN:
            return False
    return True


def slug(name):
    text = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
    return text or 'fase'


class LevelStore:
    """Lista, carrega e grava fases: a padrão (somente leitura) e as do editor."""

    def __init__(self, folder=None, default_file=DEFAULT_LEVEL_FILE):
        self.folder = Path(folder) if folder else None
        self.default_file = Path(default_file)
        self.memory = []  # fases criadas sem pasta de gravação (testes)

    def default(self):
        try:
            if not self.default_file.is_file():
                create_default_level(self.default_file)
            level = load_level(self.default_file, builtin=True)
            level.name = DEFAULT_NAME
            return level
        except (OSError, ValueError):
            return default_level()

    def custom(self):
        if not self.folder:
            return list(self.memory)
        levels = []
        for path in sorted(self.folder.glob('*.json')):
            try:
                levels.append(load_level(path))
            except (OSError, ValueError):
                print('Fase ignorada (arquivo inválido):', path.name)
        return levels

    def all(self):
        return [self.default(), *self.custom()]

    def find(self, name):
        return next((lv for lv in self.all() if lv.name == name), None)

    def name_taken(self, name):
        return any(lv.name.upper() == name.upper() for lv in self.all())

    def save(self, level):
        if level.builtin:
            raise ValueError('a fase padrão não pode ser alterada')
        if not self.folder:
            self.memory = [lv for lv in self.memory if lv is not level and lv.name != level.name]
            self.memory.append(level)
            return
        if level.path is None:
            base = slug(level.name)
            path = self.folder / f'{base}.json'
            n = 2
            while path.exists():
                path = self.folder / f'{base}_{n}.json'
                n += 1
            level.path = path
        self.folder.mkdir(parents=True, exist_ok=True)
        level.path.write_text(json.dumps(level.to_json(), indent=4, ensure_ascii=False),
                              encoding='utf-8')

    def delete(self, level):
        if level.builtin:
            return False
        if not self.folder:
            before = len(self.memory)
            self.memory = [lv for lv in self.memory if lv.name != level.name]
            return len(self.memory) < before
        try:
            level.path.unlink()
            return True
        except (OSError, AttributeError):
            return False
