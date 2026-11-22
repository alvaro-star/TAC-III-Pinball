"""Recorta sprites do atlas em tempo de execução (técnica de sprite sheets)."""
import json
from pathlib import Path
import pygame


class SpriteSheet:
    """Carrega UM PNG e extrai os retângulos descritos no manifesto JSON."""

    def __init__(self, folder):
        folder = Path(folder)
        metadata = json.loads((folder / 'pinball_atlas.json').read_text(encoding='utf-8'))
        self.sheet = pygame.image.load(str(folder / metadata['atlas'])).convert_alpha()
        self.sprites = metadata['sprites']
        self.cache = {}

    def get(self, name):
        if name not in self.cache:
            spec = self.sprites[name]
            bounds = pygame.Rect(spec['x'], spec['y'], spec['w'], spec['h'])
            if not self.sheet.get_rect().contains(bounds):
                raise ValueError('Sprite fora dos limites do atlas: ' + name)
            self.cache[name] = self.sheet.subsurface(bounds).copy()
        return self.cache[name]
