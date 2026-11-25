"""Multiplayer LAN com sockets reais em 127.0.0.1 (porta livre escolhida pelo sistema)."""
import sys
import time
import importlib
import pytest
from conftest import FakeInput, FakeAudio
from modulos.network.protocol import LineDecoder, encode, MAX_LINE
from modulos.network.lan import LANClient
from modulos.core.levels import Level


@pytest.fixture
def pair(game):
    """Anfitrião (game) e um segundo computador (outro Game) já em partida."""
    module = sys.modules['modulos.core.game']
    guest = module.Game(FakeInput(), FakeAudio(), '.')
    guest.roster.add('ANA')
    game.input = FakeInput()
    assert game.host_lan(port=0)
    assert game.state == 'lan_lobby'
    assert guest.join_lan('127.0.0.1', game.lan_server.port)
    wait(lambda: game.state == 'playing' and guest.state == 'playing', game, guest)
    yield game, guest
    guest.leave_lan()
    game.leave_lan()


def wait(condition, *games, timeout=4.0):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        for g in games:
            g.poll_lan()
        if condition():
            return
        time.sleep(0.01)
    raise AssertionError('tempo esgotado esperando a rede')


def test_protocolo_junta_pedacos_e_ignora_lixo():
    d = LineDecoder()
    data = encode({'type': 'a', 'n': 1}) + b'nao json\n' + b'[1,2]\n' + encode({'type': 'b'})
    assert d.feed(data[:7]) == []
    msgs = d.feed(data[7:])
    assert [m['type'] for m in msgs] == ['a', 'b']
    with pytest.raises(ValueError):
        LineDecoder().feed(b'x' * (MAX_LINE + 1))


def test_dois_computadores_entram_e_a_partida_comeca(pair):
    host, guest = pair
    assert host.lan_player_id == 0 and guest.lan_player_id == 1
    assert host.player_names == guest.player_names == ['JOGADOR 1', 'ANA']
    assert host.remote_mode and guest.remote_mode
    wait(lambda: guest.balls and len(guest.players) == 2, host, guest)
    assert guest.current_level_name == host.level.name
    assert len(guest.bumpers) == len(host.bumpers)


def test_controles_isolados_por_turno(pair):
    host, guest = pair
    # Vez do jogador 1 (anfitrião): o flipper não obedece ao convidado.
    guest.input.left = True
    guest.send_input()
    time.sleep(0.2)
    wait(lambda: guest.balls, host, guest)
    assert not guest.flippers[0].active
    host.input.left = True
    host.send_input()
    wait(lambda: guest.flippers[0].active and host.flippers[0].active, host, guest)


def test_so_o_jogador_da_vez_lanca(pair):
    host, guest = pair
    wait(lambda: guest.balls and guest.balls[0].ready, host, guest)
    guest.launch()
    time.sleep(0.2)
    wait(lambda: True, host, guest)
    assert guest.balls[0].ready
    host.launch()
    wait(lambda: guest.balls and not guest.balls[0].ready, host, guest)


def test_saida_de_um_jogador_avisa_o_outro(pair):
    host, guest = pair
    guest.leave_lan()
    wait(lambda: host.state == 'lan_menu', host)
    assert not host.remote_mode and 'SAIU' in host.lan_message


def test_terceiro_computador_recebe_sala_cheia(pair):
    host, guest = pair
    third = LANClient().connect('127.0.0.1', host.lan_server.port)
    end = time.monotonic() + 3
    msgs = []
    while time.monotonic() < end and not msgs:
        msgs = third.poll()
        time.sleep(0.01)
    third.close()
    assert msgs and msgs[0] == {'type': 'error', 'message': 'SALA CHEIA'}


def test_conectar_em_ip_sem_servidor_mostra_erro(game):
    game.ask_text('IP', 'ip', 'lan_menu', 40)
    game.text_type('127.0.0.1')
    game.lan_address = ''
    import modulos.core.game as module
    assert not game.join_lan('127.0.0.1', 1)
    assert game.state != 'lan_lobby' and 'CONECTAR' in game.lan_message


def test_fim_de_partida_grava_score_do_jogador_local(game):
    game.remote_mode = True
    game.lan_player_id = 1
    game.lan_level = Level('MESA')
    game.player_names = ['ANA', 'JOGADOR 1']
    snap = {'type': 'snapshot', 'state': 'gameover', 'active': 1,
            'players': [{'score': 900, 'remaining': 0}, {'score': 400, 'remaining': 0}],
            'balls': [], 'flippers': [[0.32, False], [2.8, False]], 'plunger': 0,
            'banner': '', 'banner_time': 0, 'flashes': [[], [], []], 'sounds': ['gameover', 'xx']}
    game.apply_snapshot(snap)
    game.apply_snapshot(snap)
    assert game.state == 'gameover'
    assert [(e['label'], e['score'], e['fase']) for e in game.highscores.entries] == \
        [('JOGADOR 1', 400, 'MESA (LAN)')]


def test_menu_lan_e_pausa_local(game):
    game.state = 'menu'
    while game.menu.main_choice() != 'lan':
        game.menu_action('down')
    game.menu_action('enter')
    assert game.state == 'lan_menu'
    game.menu_action('down')
    game.menu_action('enter')
    assert game.state == 'text_input' and game.text['purpose'] == 'ip'
    game.text_action('back')
    assert game.state == 'lan_menu'
    game.remote_mode = True
    game.state = game.remote_state = 'playing'
    game.pause()
    assert game.state == 'lan_pause'
    game.menu_action('back')
    assert game.state == 'playing'
