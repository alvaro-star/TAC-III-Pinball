"""Tabela de melhores pontuações, salva em storage/scores.json."""
import json
from datetime import date
from pathlib import Path


class HighScores:
    LIMIT = 10

    def __init__(self, path=None):
        self.path = Path(path) if path else None
        self.entries = []
        self.load()

    def load(self):
        if not self.path or not self.path.is_file():
            return
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return
        if not isinstance(data, list):
            return
        # Ignora entradas inválidas e completa campos ausentes (arquivo editado à mão).
        for e in data:
            if isinstance(e, dict) and isinstance(e.get('score'), int) and not isinstance(e['score'], bool):
                self.entries.append({'score': e['score'], 'label': str(e.get('label', '-')),
                                     'date': str(e.get('date', '')), 'fase': str(e.get('fase', ''))})
        self.entries.sort(key=lambda e: e['score'], reverse=True)
        del self.entries[self.LIMIT:]

    def save(self):
        if not self.path:
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.entries, indent=2, ensure_ascii=False), encoding='utf-8')
        except OSError as e:
            print('Não foi possível salvar as pontuações:', e)

    def add(self, score, label, fase=''):
        """Registra a pontuação; retorna a entrada criada ou None se não entrou na tabela."""
        if score <= 0:
            return None
        entry = {'score': score, 'label': label, 'date': date.today().strftime('%d/%m/%Y'),
                 'fase': fase}
        self.entries.append(entry)
        self.entries.sort(key=lambda e: e['score'], reverse=True)
        del self.entries[self.LIMIT:]
        self.save()
        return entry if self.rank(entry) else None

    def rank(self, entry):
        """Posição atual da entrada (1 = melhor), ou None se ela saiu da tabela."""
        for i, e in enumerate(self.entries):
            if e is entry:
                return i + 1
        return None

    def best(self, label):
        """Maior pontuação registrada para um jogador (0 se não houver)."""
        return max((e['score'] for e in self.entries if e['label'] == label), default=0)
