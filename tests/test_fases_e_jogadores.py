"""Fases em JSON, editor de fases e cadastro de jogadores."""
import json
from modulos.core.levels import (LevelStore, Level, PIECES, DEFAULT_LEVEL_FILE, DEFAULT_NAME,
                                 DEFAULT_OBJECTS, can_place, create_default_level, load_level)
from modulos.core.level_editor import LevelEditor, palette_slot, palette_hit
from modulos.effects.players import Players
from modulos.ui.menu import MAIN_ITEMS


def test_fase_padrao_vem_do_arquivo_json():
    data = json.loads(DEFAULT_LEVEL_FILE.read_text(encoding='utf-8'))
    assert data['type'] == 'pinball' and data['layers'][0]['objects']
    level = load_level(DEFAULT_LEVEL_FILE)
    assert len(level.objects) == len(DEFAULT_OBJECTS)
    bumpers, targets, holes = level.build()
    assert (len(bumpers), len(targets), len(holes)) == (5, 3, 1)


def test_fase_padrao_e_recriada_se_o_arquivo_sumir(tmp_path):
    path = tmp_path/'padrao.json'
    store = LevelStore(None, default_file=path)
    assert store.default().name == DEFAULT_NAME and path.is_file()
    create_default_level(path)
    assert len(load_level(path).objects) == len(DEFAULT_OBJECTS)


def test_jogo_usa_a_mesa_da_fase_padrao(game):
    assert game.level.builtin and len(game.bumpers) == 5 and len(game.holes) == 1


def test_arquivo_de_fase_invalido_e_ignorado(tmp_path):
    (tmp_path/'ruim.json').write_text('{nao e json', encoding='utf-8')
    (tmp_path/'boa.json').write_text(json.dumps(Level('BOA', [
        {'piece': 'buraco', 'x': 300, 'y': 500}, {'piece': 'inexistente', 'x': 1, 'y': 1},
        {'piece': 'alvo_10', 'x': 'a', 'y': 3}]).to_json()), encoding='utf-8')
    store = LevelStore(tmp_path)
    custom = store.custom()
    assert [lv.name for lv in custom] == ['BOA'] and len(custom[0].objects) == 1


def test_regras_de_posicionamento():
    assert can_place([], 'bumper_azul', 330, 450)
    assert not can_place([], 'bumper_azul', 110, 450)       # parede esquerda
    assert not can_place([], 'bumper_azul', 590, 450)       # canal de lançamento
    assert not can_place([], 'bumper_azul', 330, 700)       # zona dos flippers
    assert not can_place([], 'bumper_azul', 130, 140)       # fora do teto em arco
    other = [{'piece': 'bumper_azul', 'x': 330, 'y': 450}]
    assert not can_place(other, 'alvo_10', 350, 460)        # sobreposição


def test_editor_coloca_remove_desfaz():
    editor = LevelEditor(Level('T'))
    editor.choose(5)
    assert editor.piece == 'alvo_10'
    assert editor.place(330, 450)
    assert not editor.place(335, 455)
    assert editor.remove_at(332, 452) and editor.objects == []
    assert editor.undo() and len(editor.objects) == 1
    editor.clear()
    assert editor.objects == []
    editor.undo()
    assert len(editor.objects) == 1


def test_paleta_lista_todas_as_pecas():
    for i in range(len(PIECES)):
        assert palette_hit(*palette_slot(i)) == i
    assert palette_hit(360, 450) is None


def go_levels(game):
    game.state = 'menu'
    while game.menu.main_choice() != 'fases':
        game.menu_action('down')
    game.menu_action('enter')
    assert game.state == 'levels'


def create_level(game, name):
    go_levels(game)
    game.menu_action('new')
    assert game.state == 'text_input'
    game.text_type(name)
    game.text_action('enter')
    assert game.state == 'editing'


def test_criar_editar_salvar_e_jogar_fase(game):
    create_level(game, 'minha fase')
    assert game.editor.level.name == 'MINHA FASE' and game.bumpers == []
    game.editor_click(330, 450, 1)
    game.editor_command('choose', 8)
    game.editor_click(250, 300, 1)
    game.editor_click(20, palette_slot(0)[1], 1)     # clique na paleta
    assert game.editor.piece == 'bumper_azul'
    assert len(game.holes) == 1 and len(game.bumpers) == 1
    game.editor_command('menu')
    assert game.state == 'editor_menu'
    while game.menu.edit_choice() != 'jogar':
        game.menu_action('down')
    game.menu_action('enter')
    assert game.state == 'playing' and game.level.name == 'MINHA FASE'
    assert len(game.bumpers) == 1 and len(game.holes) == 1
    # Novo jogo continua usando a fase escolhida.
    game.back_to_menu()
    game.start_game()
    assert game.level.name == 'MINHA FASE' and len(game.bumpers) == 1


def test_escolher_fase_na_lista_e_voltar_para_padrao(game):
    create_level(game, 'B')
    game.editor_command('menu')
    while game.menu.edit_choice() != 'salvar':
        game.menu_action('down')
    game.menu_action('enter')
    assert game.state == 'levels' and game.selected_level().name == 'B'
    game.menu_action('enter')
    assert game.state == 'menu' and game.level.name == 'B' and game.bumpers == []
    go_levels(game)
    game.menu.levels_index = 0
    game.menu_action('enter')
    assert game.level.builtin and len(game.bumpers) == 5


def test_nome_repetido_e_fase_padrao_somente_leitura(game):
    go_levels(game)
    game.menu_action('new')
    game.text_type('padrão')
    game.text_action('enter')
    assert game.state == 'text_input' and game.text['error']
    game.text_action('back')
    assert game.state == 'levels'
    game.menu.levels_index = 0
    game.menu_action('edit')                 # editar a padrão = criar cópia
    game.text_type('copia')
    game.text_action('enter')
    assert game.state == 'editing' and len(game.editor.objects) == len(DEFAULT_OBJECTS)


def test_descartar_e_apagar_exige_confirmacao(game):
    create_level(game, 'TEMP')
    game.editor_command('menu')
    while game.menu.edit_choice() != 'salvar':
        game.menu_action('down')
    game.menu_action('enter')
    game.menu_action('delete')
    assert game.confirm_delete == 'TEMP' and game.levels.find('TEMP')
    game.menu_action('delete')
    assert game.levels.find('TEMP') is None


def test_fases_sao_gravadas_em_disco(tmp_path):
    store = LevelStore(tmp_path)
    store.save(Level('NOVA FASE', [{'piece': 'buraco', 'x': 300, 'y': 500}]))
    assert (tmp_path/'nova_fase.json').is_file()
    again = LevelStore(tmp_path).find('NOVA FASE')
    assert again.objects == [{'piece': 'buraco', 'x': 300, 'y': 500}]
    assert store.delete(again) and LevelStore(tmp_path).custom() == []


def test_menu_tem_mudar_de_jogador():
    assert ('jogador', 'MUDAR DE JOGADOR') in MAIN_ITEMS


def test_jogadores_persistem(tmp_path):
    path = tmp_path/'players.json'
    p = Players(path)
    assert p.names == ['JOGADOR 1'] and p.active == 'JOGADOR 1'
    assert p.add('  ana  maria ') == 'ANA MARIA'
    assert p.add('ana maria') is None
    again = Players(path)
    assert again.names == ['JOGADOR 1', 'ANA MARIA'] and again.active == 'ANA MARIA'
    again.select('JOGADOR 1')
    assert Players(path).active == 'JOGADOR 1'
    assert again.remove('ANA MARIA') and not again.remove('JOGADOR 1')


def test_trocar_jogador_e_score_por_nome(game):
    game.state = 'menu'
    while game.menu.main_choice() != 'jogador':
        game.menu_action('down')
    game.menu_action('enter')
    assert game.state == 'players'
    game.menu_action('new')
    game.text_type('alvaro')
    game.text_action('enter')
    assert game.state == 'players' and game.roster.active == 'ALVARO'
    game.back_to_menu()
    game.start_game()
    game.players[0].score = 1500
    game.players[0].remaining = 1
    game.lose_last_ball()
    entry = game.highscores.entries[0]
    assert entry['label'] == 'ALVARO' and entry['fase'] == 'PADRÃO'
    assert game.highscores.best('ALVARO') == 1500 and game.highscores.best('JOGADOR 1') == 0
    # Multiplayer: o adversário é outro jogador cadastrado.
    game.player_count = 2
    game.start_game()
    assert game.player_names == ['ALVARO', 'JOGADOR 1']
