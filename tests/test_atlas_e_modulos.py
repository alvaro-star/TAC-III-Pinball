"""Valida o pacote de sprite sheets e as referências de materiais."""
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_sprite_sheet_tem_recortes_validos():
    folder = ROOT / 'assets' / 'pinball'
    data = json.loads((folder/'pinball_atlas.json').read_text(encoding='utf-8'))
    png = folder / data['atlas']
    with png.open('rb') as fh:
        header = fh.read(24)
    assert header[:8] == b'\x89PNG\r\n\x1a\n'
    w, h = struct.unpack('>II', header[16:24])
    assert (w,h) == (data['largura'], data['altura'])
    assert len(data['sprites']) >= 11
    assert set(data['origens'].values()) == {'PINBALL1.png','PINBALL2.png','PINBALL3.png'}
    for name, rect in data['sprites'].items():
        assert 0 <= rect['x'] < w and 0 <= rect['y'] < h, name
        assert rect['x']+rect['w'] <= w and rect['y']+rect['h'] <= h, name


def test_tres_sprite_sheets_originalmente_fornecidas():
    folder = ROOT / 'assets' / 'pinball'
    assert all((folder / f'PINBALL{i}.png').is_file() for i in (1,2,3))


def test_audio_e_separacao_de_modulos():
    assert (ROOT/'modulos/audio/audio_manager.py').is_file()
    assert (ROOT/'modulos/ui/sprite_sheet.py').is_file()
    assert all((ROOT/f'assets/sound/{n}.wav').is_file() for n in ('flipper','launch','bumper','target','bonus','lose','gameover','music'))
