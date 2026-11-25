"""Fixture `game`: Game sem janela, sem áudio real e sem gravar em disco."""
import sys
import types
import importlib
import pytest


class FakeInput:
    left=False
    right=False
    launch=False


class FakeAudio:
    muted=False
    def sound(self, name):pass
    def music_start(self):pass


@pytest.fixture
def game(monkeypatch):
    stage_module=types.ModuleType('modulos.ui.stage')
    stage_module.Stage=lambda root: None
    monkeypatch.setitem(sys.modules,'modulos.ui.stage',stage_module)
    # O import dinâmico permite testar o modelo sem exigir placa gráfica.
    sys.modules.pop('modulos.core.game',None)
    module=importlib.import_module('modulos.core.game')
    obj=module.Game(FakeInput(),FakeAudio(),'.')
    yield obj
    sys.modules.pop('modulos.core.game',None)
