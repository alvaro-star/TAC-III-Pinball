"""Configurações editáveis pelo menu, salvas em storage/settings.json."""
import json
from pathlib import Path

# (chave, rótulo, mínimo, máximo, passo, sufixo). Sem mínimo = opção liga/desliga.
ITEMS = [
    ('sound_on', 'SOM', None, None, None, ''),
    ('music_volume', 'VOLUME DA MÚSICA', 0, 100, 5, '%'),
    ('sfx_volume', 'VOLUME DOS EFEITOS', 0, 100, 5, '%'),
    ('gravity', 'VELOCIDADE DE QUEDA', 50, 150, 10, '%'),
    ('balls_per_player', 'BOLAS POR JOGADOR', 1, 5, 1, ''),
    ('show_fps', 'MOSTRAR FPS', None, None, None, ''),
]

DEFAULTS = {
    'sound_on': True,
    'music_volume': 15,
    'sfx_volume': 45,
    'gravity': 100,  # % da gravidade padrão (constants.GRAVITY)
    'balls_per_player': 3,
    'show_fps': True,
    'fase': '',  # nome da fase escolhida ('' = padrão); fora de ITEMS, não aparece no menu
}


class Settings:
    def __init__(self, path=None):
        self.path = Path(path) if path else None
        self.values = dict(DEFAULTS)
        self.load()

    def __getattr__(self, key):
        values = self.__dict__.get('values', {})
        if key in values:
            return values[key]
        raise AttributeError(key)

    def load(self):
        if not self.path or not self.path.is_file():
            return
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return
        if not isinstance(data, dict):
            return
        for key, label, low, high, step, _ in ITEMS:
            if key not in data:
                continue
            value = data[key]
            if low is None and isinstance(value, bool):
                self.values[key] = value
            elif low is not None and isinstance(value, int) and not isinstance(value, bool):
                self.values[key] = max(low, min(high, value))
        if isinstance(data.get('fase'), str):
            self.values['fase'] = data['fase']

    def save(self):
        if not self.path:
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.values, indent=2), encoding='utf-8')
        except OSError as e:
            print('Não foi possível salvar as configurações:', e)

    def adjust(self, key, direction):
        """Muda um valor em um passo (direction = -1 ou +1); booleanos alternam."""
        _, _, low, high, step, _ = next(item for item in ITEMS if item[0] == key)
        if low is None:
            self.values[key] = not self.values[key]
        else:
            self.values[key] = max(low, min(high, self.values[key] + step * direction))

    def text(self, key):
        _, _, low, _, _, suffix = next(item for item in ITEMS if item[0] == key)
        value = self.values[key]
        if low is None:
            return 'LIGADO' if value else 'DESLIGADO'
        return f'{value}{suffix}'
