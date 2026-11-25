"""Menu inicial, configurações e tabela de score."""
import pytest
from modulos.config.settings import Settings
from modulos.effects.highscores import HighScores
from modulos.ui.menu import MAIN_ITEMS
from modulos.config.constants import GRAVITY, FIXED_DT
from modulos.entities.ball import Ball


def choose(game, key):
    """Navega no menu principal até a opção `key` e confirma."""
    game.state = 'menu'
    for _ in MAIN_ITEMS:
        if game.menu.main_choice() == key:
            break
        game.menu_action('down')
    assert game.menu.main_choice() == key
    game.menu_action('enter')


def test_menu_tem_as_opcoes_pedidas():
    labels = [label for _, label in MAIN_ITEMS]
    for expected in ('NOVO JOGO', 'SCORE', 'MULTIPLAYER', 'EDITOR DE FASES', 'MUDAR DE JOGADOR', 'CONFIGURAÇÕES'):
        assert expected in labels


def test_jogo_comeca_no_menu_e_navegacao_da_volta(game):
    assert game.state == 'menu'
    for _ in MAIN_ITEMS:
        game.menu_action('down')
    assert game.menu.main_index == 0
    game.menu_action('up')
    assert game.menu.main_choice() == 'sair'


def test_novo_jogo_e_multiplayer(game):
    choose(game, 'novo')
    assert game.state == 'playing' and len(game.players) == 1
    choose(game, 'multi')
    assert game.state == 'playing' and len(game.players) == 2


def test_telas_score_editor_e_sair(game):
    choose(game, 'score')
    assert game.state == 'scores'
    game.menu_action('back')
    assert game.state == 'menu'
    choose(game, 'fases')
    assert game.state == 'levels'
    game.menu_action('back')
    assert game.state == 'menu'
    choose(game, 'sair')
    assert not game.running


def test_configuracoes_ajustam_e_aplicam(game):
    choose(game, 'config')
    assert game.state == 'settings'
    while game.menu.settings_choice() != 'gravity':
        game.menu_action('down')
    game.menu_action('right')
    assert game.settings.gravity == 110
    assert game.trajectory.gravity_scale == pytest.approx(1.1)
    while game.menu.settings_choice() != 'balls_per_player':
        game.menu_action('down')
    game.menu_action('left')
    game.menu_action('back')
    assert game.state == 'menu'
    choose(game, 'novo')
    assert game.players[0].remaining == 2


def test_limites_e_toggle_das_configuracoes():
    s = Settings()
    for _ in range(30):
        s.adjust('music_volume', 1)
    assert s.music_volume == 100
    s.adjust('sound_on', 1)
    assert s.sound_on is False and s.text('sound_on') == 'DESLIGADO'


def test_configuracoes_salvas_em_disco(tmp_path):
    s = Settings(tmp_path/'settings.json')
    s.adjust('gravity', -1)
    s.save()
    assert Settings(tmp_path/'settings.json').gravity == 90


def test_configuracao_invalida_no_arquivo_e_ignorada(tmp_path):
    (tmp_path/'settings.json').write_text('{"gravity": 9999, "sound_on": "sim"}', encoding='utf-8')
    s = Settings(tmp_path/'settings.json')
    assert s.gravity == 150 and s.sound_on is True


def test_velocidade_de_queda_multiplica_gravidade(game):
    game.trajectory.gravity_scale = 1.5
    b = Ball(game.trajectory, 300, 200, ready=False)
    b.update(FIXED_DT)
    assert b.velocity.y == pytest.approx(1.5*GRAVITY*FIXED_DT, rel=0.002)


def test_score_ordena_limita_e_persiste(tmp_path):
    hs = HighScores(tmp_path/'scores.json')
    for value in range(1, 13):
        hs.add(value*100, 'SOLO')
    assert [e['score'] for e in hs.entries][:3] == [1200, 1100, 1000]
    assert len(hs.entries) == HighScores.LIMIT
    assert hs.add(50, 'SOLO') is None  # abaixo do 10º lugar
    assert hs.add(0, 'SOLO') is None
    assert len(HighScores(tmp_path/'scores.json').entries) == HighScores.LIMIT


def test_game_over_registra_score(game):
    choose(game, 'multi')
    game.players[0].score = 500
    game.players[1].score = 800
    for p in game.players:
        p.remaining = 1
    game.lose_last_ball()
    game.lose_last_ball()
    assert game.state == 'gameover'
    assert [e['score'] for e in game.highscores.entries] == [800, 500]
    assert game.highscores.entries[0]['label'] == 'JOGADOR 2'
    assert game.new_records == [(0, 2), (1, 1)]
