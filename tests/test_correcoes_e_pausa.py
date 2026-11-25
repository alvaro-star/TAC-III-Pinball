"""Regressões dos bugs corrigidos e menu de pausa."""
import json
from modulos.config.constants import FIXED_DT, LEFT, RIGHT, MAX_SPEED
from modulos.physics.collision_manager import Vector
from modulos.effects.highscores import HighScores
from modulos.ui.menu import PAUSE_ITEMS


def put_ball(game, x, y, vx, vy):
    game.start_game()
    ball = game.balls[0]
    ball.ready = False
    ball.position = Vector(x, y)
    ball.velocity = Vector(vx, vy)
    return ball


def test_bola_rapida_nao_atravessa_parede_esquerda(game):
    ball = put_ball(game, LEFT+12, 450, -MAX_SPEED, 0)
    for _ in range(5):
        game.update(FIXED_DT)
        assert ball.position.x >= LEFT


def test_bola_rapida_nao_atravessa_parede_direita(game):
    ball = put_ball(game, RIGHT-12, 450, MAX_SPEED, 0)
    for _ in range(5):
        game.update(FIXED_DT)
        assert ball.position.x <= RIGHT


def test_caso_real_de_tunelamento_nao_perde_vida(game):
    ball = put_ball(game, 116, 421, -1399, 296)
    game.update(FIXED_DT)
    assert ball.position.x >= LEFT


def held_left_flipper(game):
    game.start_game()
    game.input.left = True
    for _ in range(60):
        game.update(FIXED_DT)
    flipper = game.flippers[0]
    assert not flipper.swinging_up
    return flipper


def test_flipper_parado_no_alto_nao_chuta_a_bola(game):
    flipper = held_left_flipper(game)
    mid = flipper.pivot+(flipper.tip-flipper.pivot)*0.5
    ball = game.balls[0]
    ball.ready = False
    ball.position = Vector(mid.x, mid.y-24)
    ball.velocity = Vector(0, 10)
    for _ in range(240):
        game.update(FIXED_DT)
        assert game.balls[0].velocity.y > -700


def test_bola_segura_no_flipper_nao_recebe_empurrao_de_destravar(game):
    flipper = held_left_flipper(game)
    mid = flipper.pivot+(flipper.tip-flipper.pivot)*0.5
    ball = game.balls[0]
    ball.ready = False
    ball.position = Vector(mid.x, mid.y-24)
    for _ in range(int(6/FIXED_DT)):
        game.update(FIXED_DT)
    assert game.balls and game.balls[0].velocity.magnitude() < 200


def test_flipper_subindo_ainda_rebate_a_bola(game):
    game.start_game()
    flipper = game.flippers[0]
    mid = flipper.pivot+(flipper.tip-flipper.pivot)*0.6
    ball = game.balls[0]
    ball.ready = False
    ball.position = Vector(mid.x, mid.y-22)
    ball.velocity = Vector(0, 50)
    game.input.left = True
    best = 0
    for _ in range(12):
        game.update(FIXED_DT)
        best = min(best, game.balls[0].velocity.y)
    assert best <= -780


def test_scores_json_incompleto_nao_derruba(tmp_path):
    path = tmp_path/'scores.json'
    path.write_text(json.dumps([{'score': 100}, {'score': 'x'}, 7, {'score': 300, 'label': 'SOLO'}]),
                    encoding='utf-8')
    hs = HighScores(path)
    assert [e['score'] for e in hs.entries] == [300, 100]
    assert all(isinstance(e['label'], str) and isinstance(e['date'], str) for e in hs.entries)


def test_scores_json_que_nao_e_lista_e_ignorado(tmp_path):
    path = tmp_path/'scores.json'
    path.write_text('{"score": 10}', encoding='utf-8')
    assert HighScores(path).entries == []


def test_empate_no_multiplayer(game):
    game.player_count = 2
    game.start_game()
    game.players[0].score = game.players[1].score = 700
    assert game.result_text() == 'EMPATE!'
    game.players[1].score = 900
    assert game.result_text() == 'MAIOR PONTUAÇÃO: JOGADOR 2'


def pause_and_choose(game, key):
    game.pause()
    assert game.state == 'paused' and game.menu.pause_choice() == 'continuar'
    while game.menu.pause_choice() != key:
        game.menu_action('down')
    game.menu_action('enter')


def test_menu_de_pausa_tem_as_opcoes():
    keys = [k for k, _ in PAUSE_ITEMS]
    assert keys == ['continuar', 'reiniciar', 'config', 'menu', 'sair']


def test_pausa_continuar_e_esc(game):
    game.start_game()
    pause_and_choose(game, 'continuar')
    assert game.state == 'playing'
    game.pause()
    game.menu_action('back')
    assert game.state == 'playing'


def test_pausa_reiniciar(game):
    game.start_game()
    game.players[0].score = 999
    pause_and_choose(game, 'reiniciar')
    assert game.state == 'playing' and game.players[0].score == 0


def test_pausa_configuracoes_volta_para_a_pausa(game):
    game.start_game()
    pause_and_choose(game, 'config')
    assert game.state == 'settings'
    game.menu_action('back')
    assert game.state == 'paused'


def test_pausa_menu_principal_e_sair(game):
    game.start_game()
    pause_and_choose(game, 'menu')
    assert game.state == 'menu' and game.balls == []
    game.start_game()
    pause_and_choose(game, 'sair')
    assert not game.running
