"""Testes independentes de driver gráfico e áudio."""
import math
import sys
import types
import importlib
import pytest
from modulos.physics.collision_manager import Vector, CollisionManager
from modulos.physics.trajectory_controller import TrajectoryController
from modulos.entities.ball import Ball
from modulos.entities.actuators import Flipper, Plunger
from modulos.entities.obstacles import Bumper, Target
from modulos.effects.score import PlayerScore
from constants import GRAVITY, FIXED_DT


def test_vector_math():
    assert (Vector(1,2)+Vector(3,4)) == Vector(4,6)
    assert Vector(3,4).magnitude() == 5


def test_gravity_and_semi_implicit_euler():
    b=Ball(TrajectoryController(CollisionManager()),300,200,ready=False)
    before=b.position.y
    b.update(FIXED_DT)
    assert b.velocity.y>0
    assert b.position.y>before
    assert b.velocity.y==pytest.approx(GRAVITY*FIXED_DT,rel=0.002)


def test_ready_ball_remains_in_launch_lane():
    b=Ball(TrajectoryController(CollisionManager()))
    pos=b.position
    b.update(0.5)
    assert b.position==pos


def test_plunger_charge_increases_launch_force():
    p=Plunger()
    p.activate(True)
    p.update(1.2)
    assert p.release()>1000
    assert p.charge==0


def test_ball_launch_uses_strength():
    b=Ball(TrajectoryController(CollisionManager()))
    assert b.launch(1200)
    assert b.velocity.y==-1200
    assert not b.launch(700)


def test_segment_collision_bounces():
    b=Ball(TrajectoryController(CollisionManager()),200,209,ready=False)
    b.velocity=Vector(0,-260)
    assert CollisionManager.circle_segment(b,Vector(100,200),Vector(300,200))
    assert b.velocity.y>0


def test_circle_bumper_kicks_and_awards():
    b=Ball(TrajectoryController(CollisionManager()),210,200,ready=False)
    b.velocity=Vector(-80,0)
    obs=Bumper(190,200,24,100,'bumper')
    assert obs.on_collide(b)==100
    assert obs.on_collide(b)==0


def test_target_scores_without_repeat_per_frame():
    b=Ball(TrajectoryController(CollisionManager()),140,150,ready=False)
    t=Target(140,150,23,250,'target')
    assert t.on_collide(b)==250
    assert t.on_collide(b)==0


def test_flippers_move_and_return():
    f=Flipper('left',(260,780))
    old=f.angle
    f.activate(True);f.update(.04)
    assert f.angle<old
    f.activate(False);f.update(.08)
    assert f.angle==pytest.approx(old)


def test_flippers_independent():
    l=Flipper('left',(260,780));r=Flipper('right',(450,780))
    l.activate(True)
    l.update(.02);r.update(.02)
    assert l.angle!=l.rest and r.angle==r.rest


def test_score_combo_after_six_bumpers():
    p=PlayerScore()
    for _ in range(5):
        _,msg=p.add_points(100,'bumper')
        assert msg is None
    _,msg=p.add_points(100,'bumper')
    assert msg=='COMBO +500'
    assert p.score==1100


def test_multiplier_activates_after_three_targets():
    p=PlayerScore()
    for _ in range(3): p.add_points(250,'target')
    assert p.multiplier()==2
    p.add_points(100,'bumper')
    assert p.score==950
    p.update(13)
    assert p.multiplier()==1


def test_multiball_trigger_after_six_targets():
    p=PlayerScore()
    triggers=[]
    for _ in range(6):
        _,msg=p.add_points(250,'target')
        if msg:triggers.append(msg)
    assert triggers==['PONTUAÇÃO 2X','MULTIBALL']


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
    sys.modules.pop('game',None)
    module=importlib.import_module('game')
    obj=module.Game(FakeInput(),FakeAudio(),'.')
    yield obj
    sys.modules.pop('game',None)


def test_game_starts_with_three_balls(game):
    game.start_game()
    assert game.players[0].remaining==3
    assert len(game.balls)==1 and game.balls[0].ready


def test_pause_and_restart(game):
    game.start_game()
    game.pause()
    assert game.state=='paused'
    game.pause()
    assert game.state=='playing'
    game.players[0].score=999
    game.start_game()
    assert game.players[0].score==0


def test_two_player_alternation(game):
    game.player_count=2
    game.start_game()
    game.lose_last_ball()
    assert game.active_player==1
    assert game.players[0].remaining==2
    game.lose_last_ball()
    assert game.active_player==0
    assert game.players[1].remaining==2


def test_gameover_when_all_lives_used(game):
    game.start_game()
    for _ in range(3): game.lose_last_ball()
    assert game.players[0].remaining==0
    assert game.state=='gameover'


def test_launcher_releases_ball(game):
    game.start_game()
    game.plunger.activate(True)
    game.plunger.update(1.0)
    game.launch()
    assert not game.balls[0].ready
    assert game.balls[0].velocity.y < -900


def test_multiball_uses_extra_balls(game):
    game.start_game()
    game.players[0].targets_hit=5
    game.point(250,'target')
    assert len(game.balls)==3
    assert all(ball.active for ball in game.balls)


def test_score_is_separate_per_player(game):
    game.player_count=2
    game.start_game()
    game.point(250,'target')
    game.lose_last_ball()
    game.point(100,'bumper')
    assert game.players[0].score==250
    assert game.players[1].score==100


def test_teto_circular_mantem_bola_e_deslizamento():
    from constants import ARCH_CENTER_X, ARCH_CENTER_Y, ARCH_RADIUS
    ball=Ball(TrajectoryController(CollisionManager()),ARCH_CENTER_X+200,ARCH_CENTER_Y-200,ready=False)
    ball.velocity=Vector(0,-900)
    assert CollisionManager.circle_inside_arch(ball,ARCH_CENTER_X,ARCH_CENTER_Y,ARCH_RADIUS)
    delta=ball.position-Vector(ARCH_CENTER_X,ARCH_CENTER_Y)
    assert delta.magnitude()==pytest.approx(ARCH_RADIUS-ball.radius)
    assert ball.velocity.dot(delta.normalized())<0
    assert ball.velocity.x<-500


def test_lancamento_forte_sai_do_canal(game):
    game.start_game()
    ball=game.balls[0]
    game.plunger.charge=1.0
    game.launch()
    min_x=ball.position.x
    for _ in range(360):
        game.update(FIXED_DT)
        min_x=min(min_x,ball.position.x)
    assert min_x<500


def test_lancamento_fraco_volta_ao_lancador_sem_perder_vida(game):
    game.start_game()
    ball=game.balls[0]
    ball.ready=False
    ball.position=Vector(590,700)
    ball.velocity=Vector(0,300)
    for _ in range(120):
        game.update(FIXED_DT)
    assert game.balls[0].ready
    assert game.players[0].remaining==3


def test_viewport_centraliza_em_janela_larga_e_alta():
    from display import fit_viewport
    assert fit_viewport(1440,900)==(360,0,720,900)
    assert fit_viewport(720,1100)==(0,100,720,900)


def test_bola_no_centro_passa_entre_flippers_e_perde_vida(game):
    game.start_game()
    ball=game.balls[0]
    ball.ready=False
    ball.position=Vector(360,720)
    ball.velocity=Vector(0,100)
    for _ in range(240):
        game.update(FIXED_DT)
    assert game.players[0].remaining==2
