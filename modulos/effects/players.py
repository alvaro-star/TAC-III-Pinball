"""Jogadores cadastrados e jogador ativo, salvos em storage/players.json."""
import json
from pathlib import Path

DEFAULT_PLAYER = 'JOGADOR 1'
MAX_NAME = 12


def clean_name(text):
    """Nome em maiúsculas, sem espaços duplicados e com no máximo MAX_NAME letras."""
    return ' '.join(str(text).upper().split())[:MAX_NAME].strip()


class Players:
    def __init__(self, path=None):
        self.path = Path(path) if path else None
        self.names = [DEFAULT_PLAYER]
        self.active = DEFAULT_PLAYER
        self.load()

    def load(self):
        if not self.path or not self.path.is_file():
            return
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return
        if not isinstance(data, dict):
            return
        names = []
        for n in data.get('jogadores', []):
            name = clean_name(n) if isinstance(n, str) else ''
            if name and name not in names:
                names.append(name)
        if names:
            self.names = names
            active = data.get('ativo')
            self.active = active if active in names else names[0]

    def save(self):
        if not self.path:
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps({'ativo': self.active, 'jogadores': self.names},
                                            indent=2, ensure_ascii=False), encoding='utf-8')
        except OSError as e:
            print('Não foi possível salvar os jogadores:', e)

    def add(self, name):
        """Cadastra e seleciona o jogador; retorna o nome final ou None se vazio/repetido."""
        name = clean_name(name)
        if not name or name in self.names:
            return None
        self.names.append(name)
        self.active = name
        self.save()
        return name

    def select(self, name):
        if name in self.names:
            self.active = name
            self.save()

    def remove(self, name):
        """Remove um jogador; sempre resta pelo menos um cadastrado."""
        if name not in self.names or len(self.names) == 1:
            return False
        self.names.remove(name)
        if self.active == name:
            self.active = self.names[0]
        self.save()
        return True

    def second(self):
        """Adversário no multiplayer: o próximo cadastrado, ou 'JOGADOR 2'."""
        others = [n for n in self.names if n != self.active]
        if others:
            return others[0]
        return 'JOGADOR 2' if self.active != 'JOGADOR 2' else DEFAULT_PLAYER
