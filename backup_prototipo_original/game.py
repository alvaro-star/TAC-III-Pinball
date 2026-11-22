"""Regras do pinball - estados, jogo para 1-2 pessoas, pontuação e vidas."""
from .constants import LEFT, RIGHT, TOP, BOTTOM, LAUNCH_X, LAUNCH_Y
from .physics.collision_manager import Vector, CollisionManager
from .physics.trajectory_controller import TrajectoryController
from .entities.ball import Ball
from .entities.actuators import Flipper, Plunger
from .entities.obstacles import Bumper, Target, Hole
from .effects.score import PlayerScore
from .ui.stage import Stage


class Game:
    def __init__(self, inputs, audio, root):
        self.running = True
        self.input = inputs
        self.audio = audio
        self.state = 'menu'
        self.player_count = 1
        self.active_player = 0
        self.players = [PlayerScore()]
        self.cm = CollisionManager()
        self.trajectory = TrajectoryController(self.cm)
        self.stage = Stage(root)
        self.balls = []
        self.flippers = [Flipper('left',(267,782)),Flipper('right',(453,782))]
        self.plunger = Plunger()
        self.bumpers = [Bumper(284,342,33,100,'bumper'),
                        Bumper(444,340,33,100,'bumper'),
                        Bumper(363,257,36,100,'bumper'),
                        Bumper(192,507,24,100,'bumper'),
                        Bumper(524,505,24,100,'bumper')]
        self.targets = [Target(231,215,24,250,'target'),
                        Target(363,196,24,250,'target'),
                        Target(496,216,24,250,'target')]
        self.hole = Hole(360,447,24,300,'hole')
        self.banner = ''
        self.banner_time = 0.0
        self.launch_lane_segments = [
            (Vector(LEFT,TOP),Vector(RIGHT,TOP)),
            (Vector(LEFT,TOP),Vector(LEFT,678)),
            (Vector(RIGHT,TOP),Vector(RIGHT,823)),
            (Vector(LEFT,677),Vector(242,811)),
            (Vector(574,678),Vector(472,811)),
            (Vector(568,339),Vector(568,820)),
        ]
        self.slingshots = [(Vector(164,632),Vector(217,700)),
                           (Vector(518,632),Vector(480,700))]
        self.phase_time = 0.0

    def start_game(self):
        self.players = [PlayerScore() for _ in range(self.player_count)]
        self.active_player = 0
        self.flippers = [Flipper('left',(267,782)),Flipper('right',(453,782))]
        self.plunger = Plunger()
        self.banner = 'BOA SORTE!'
        self.banner_time = 1.8
        self.state = 'playing'
        self.phase_time = 0.0
        self.balls = [Ball(self.trajectory)]
        self.audio.music_start()

    def pause(self):
        if self.state == 'playing':
            self.state='paused'
        elif self.state == 'paused':
            self.state='playing'

    def launch(self):
        if self.state!='playing':
            return
        for b in self.balls:
            if b.ready:
                b.launch(self.plunger.release())
                self.audio.sound('launch')
                break

    def show_message(self, text, seconds=1.3):
        self.banner=text
        self.banner_time=seconds

    def point(self, points, kind):
        scorer = self.players[self.active_player]
        earned,bonus=scorer.add_points(points,kind)
        if bonus:
            self.show_message(bonus,1.9)
            self.audio.sound('bonus')
            if bonus=='MULTIBALL':
                # Bola extra controlada pela mesma pessoa, sem gastar uma vida.
                b = Ball(self.trajectory,362,565,ready=False)
                b.velocity=Vector(-180,-590)
                self.balls.append(b)
                extra=Ball(self.trajectory,387,575,ready=False)
                extra.velocity=Vector(170,-520)
                self.balls.append(extra)
        return earned

    def lose_last_ball(self):
        player=self.players[self.active_player]
        player.remaining=max(0,player.remaining-1)
        self.audio.sound('lose')
        if all(p.remaining<=0 for p in self.players):
            self.balls=[]
            self.state='gameover'
            self.audio.sound('gameover')
            return
        for step in range(1,len(self.players)+1):
            nxt=(self.active_player+step)%len(self.players)
            if self.players[nxt].remaining>0:
                self.active_player=nxt
                break
        self.balls=[Ball(self.trajectory)]
        self.plunger=Plunger()
        self.show_message('PRÓXIMA BOLA',1.5)

    def update(self, dt):
        if self.state!='playing':
            return
        self.phase_time += dt
        self.banner_time=max(0.0,self.banner_time-dt)
        scorer=self.players[self.active_player]
        scorer.update(dt)
        self.plunger.activate(self.input.launch and any(b.ready for b in self.balls))
        self.plunger.update(dt)
        for flipper in self.flippers:
            before=flipper.active
            flipper.activate(self.input.left if flipper.side=='left' else self.input.right)
            flipper.update(dt)
            if flipper.active and not before:
                self.audio.sound('flipper')
        for entity in [*self.targets,*self.bumpers,self.hole]:
            entity.update(dt)
        for ball in list(self.balls):
            ball.update(dt)
            if ball.ready:
                continue
            self.collide_world(ball)
            # Evita que uma bola sem velocidade permaneça travada indefinidamente.
            if ball.velocity.magnitude() < 45:
                ball.seconds_still += dt
                if ball.seconds_still>4:
                    ball.velocity=Vector(120,-430)
                    ball.seconds_still=0
            else:
                ball.seconds_still=0
            if ball.position.y > BOTTOM + 26:
                self.balls.remove(ball)
        if not self.balls:
            self.lose_last_ball()

    def collide_world(self, ball):
        for a,b in self.launch_lane_segments:
            self.cm.circle_segment(ball,a,b,0.81)
        # Flippers - colisão cápsula e impulso dependente do movimento angular.
        for flipper in self.flippers:
            q = Vector(flipper.pivot.x,flipper.pivot.y)
            t = flipper.tip
            raw_radius=ball.radius
            ball.radius = raw_radius + flipper.radius
            moving = flipper.moving_at(q+(t-q)*0.55)
            hit = self.cm.circle_segment(ball,q,t,0.83,moving)
            ball.radius=raw_radius
            if hit and flipper.active and ball.flipper_cooldown<=0:
                # O golpe para cima garante resposta imediata ao comando RF2/RF3.
                ball.velocity.y = min(ball.velocity.y,-780.0)
                ball.velocity.x += (150.0 if flipper.side=='left' else -150.0)
                ball.flipper_cooldown=0.13
                self.audio.sound('flipper')
        # Superfícies com bônus.
        for entity in self.bumpers:
            value=entity.on_collide(ball)
            if value:
                self.point(value,'bumper')
                self.audio.sound('bumper')
        for entity in self.targets:
            value=entity.on_collide(ball)
            if value:
                self.point(value,'target')
                self.audio.sound('target')
        value=self.hole.on_collide(ball)
        if value:
            self.point(value,'hole')
            self.show_message('BÔNUS +300',1.2)
            self.audio.sound('bonus')
        # Slingshot (paredes diagonais próximas aos flippers).
        for a,b in self.slingshots:
            if self.cm.circle_segment(ball,a,b,1.01) and ball.cooldown<=0:
                ball.cooldown=0.16
                self.point(25,'slingshot')
                ball.velocity.y=min(ball.velocity.y,-200)
                self.audio.sound('bumper')
        # Quando a bola passa do limite da mesa, a vida é contabilizada no update.

    def draw(self, surface):
        self.stage.draw_playfield(surface,self)
        if self.state=='menu':
            self.stage.overlay(surface,'PINBALL ARCADE',[
                'Tópicos Avançados em Computação III',
                'A / D: FLIPPERS  |  ESPAÇO: LANÇAR',
                f'JOGADORES: {self.player_count}   (teclas 1 ou 2)',
                'ENTER PARA INICIAR',
                'P / ESC: PAUSA    R: REINÍCIO    M: SOM',
            ])
        elif self.state=='paused':
            self.stage.overlay(surface,'PAUSADO',[
                'PRESSIONE P OU ESC PARA CONTINUAR',
                'R REINICIA A PARTIDA',
                'M ATIVA OU DESATIVA O SOM',
            ])
        elif self.state=='gameover':
            winner=max(range(len(self.players)),key=lambda i:self.players[i].score)+1
            lines=['FIM DE JOGO  -  TODAS AS BOLAS FORAM USADAS']
            if len(self.players)==2:
                lines += [f'JOGADOR 1: {self.players[0].score:07d}',
                          f'JOGADOR 2: {self.players[1].score:07d}',
                          f'MAIOR PONTUAÇÃO: JOGADOR {winner}']
            else:
                lines += [f'PONTUAÇÃO FINAL: {self.players[0].score:07d}']
            lines += ['ENTER PARA JOGAR NOVAMENTE']
            self.stage.overlay(surface,'GAME OVER',lines,(252,95,125))
