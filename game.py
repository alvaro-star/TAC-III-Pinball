"""Regras do pinball - estados, jogo para 1-2 pessoas, pontuação e vidas."""
from constants import (LEFT, RIGHT, BOTTOM, LAUNCH_X, LAUNCH_Y, LANE_LEFT,
                       ARCH_CENTER_X, ARCH_CENTER_Y, ARCH_RADIUS)
from modulos.physics.collision_manager import Vector, CollisionManager
from modulos.physics.trajectory_controller import TrajectoryController
from modulos.entities.ball import Ball
from modulos.entities.actuators import Flipper, Plunger
from modulos.entities.obstacles import Bumper, Target, Hole
from modulos.effects.score import PlayerScore
from modulos.ui.stage import Stage
from modulos.levels import Level, LevelRepository, ObstacleFactory
from modulos.editor import LevelEditor
from modulos.config.settings import SettingsRepository
from modulos.network.lan import LANClient, LANServer
from modulos.network.protocol import PORT


class Game:
    def __init__(self, inputs, audio, root, load_stage=True):
        self.root = root
        self.settings_repo = SettingsRepository(root)
        self.settings = self.settings_repo.load()
        self.level_repo = LevelRepository(root)
        self.level = self.level_repo.load('classica')
        self.selected_level = 'classica'
        self.editor = LevelEditor(self.level_repo)
        self.ui_index = 0
        self.level_index = 0
        self.lan_address = '192.168.1.'
        self.lan_server = None
        self.lan_client = None
        self.lan_message = ''
        self.lan_player_id = None
        self.remote_mode = False
        self.running = True
        self.input = inputs
        self.audio = audio
        self.state = 'menu'
        self.player_count = self.settings.players
        self.active_player = 0
        self.players = [PlayerScore()]
        self.cm = CollisionManager()
        self.trajectory = TrajectoryController(self.cm)
        self.stage = Stage(root) if load_stage else None
        if hasattr(self.audio,'set_volumes'):
            self.audio.set_volumes(self.settings.music_volume/100,self.settings.sfx_volume/100)
        self.balls = []
        self.flippers = [Flipper('left',(240,782)),Flipper('right',(480,782))]
        self.plunger = Plunger()
        self.load_level(self.level)
        self.banner = ''
        self.banner_time = 0.0
        self.launch_lane_segments = [
            (Vector(LEFT,ARCH_CENTER_Y),Vector(LEFT,678)),
            (Vector(RIGHT,ARCH_CENTER_Y),Vector(RIGHT,823)),
            (Vector(LEFT,677),Vector(240,782)),
            (Vector(LANE_LEFT,683),Vector(480,782)),
            (Vector(LANE_LEFT,339),Vector(LANE_LEFT,820)),
        ]
        self.slingshots = [(Vector(164,632),Vector(217,700)),
                           (Vector(518,632),Vector(480,700))]
        self.phase_time = 0.0

    def start_game(self):
        self.ui_index=0
        self.load_level(self.level)
        self.players = [PlayerScore() for _ in range(self.player_count)]
        self.active_player = 0
        self.flippers = [Flipper('left',(240,782)),Flipper('right',(480,782))]
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
            self.ui_index=0
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
        for entity in [*self.targets,*self.bumpers,*([self.hole] if self.hole else [])]:
            entity.update(dt)
        for ball in list(self.balls):
            ball.update(dt)
            if ball.ready:
                continue
            self.collide_world(ball)
            # Lançamento fraco: a bola volta ao lançador sem custar uma vida.
            if ball.position.x>LANE_LEFT and ball.position.y>=LAUNCH_Y and ball.velocity.y>0:
                ball.position=Vector(LAUNCH_X,LAUNCH_Y)
                ball.velocity=Vector()
                ball.ready=True
                continue
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
        self.cm.circle_inside_arch(ball,ARCH_CENTER_X,ARCH_CENTER_Y,ARCH_RADIUS)
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
        value=self.hole.on_collide(ball) if self.hole else 0
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
        if self.stage is None:
            return
        if self.state == 'editor':
            self.stage.draw_editor(surface,self.editor)
            return
        self.stage.draw_playfield(surface,self)
        if self.state == 'menu':
            self.stage.draw_menu(surface,'PINBALL TAC III',self.menu_items(),self.ui_index,
                ['SETA CIMA/BAIXO: escolher | ENTER: abrir','Mouse também habilitado'])
        elif self.state == 'new_game':
            self.stage.draw_menu(surface,'NOVO JOGO',self.menu_items(),self.ui_index,
                ['ESQUERDA/DIREITA: modificar | ENTER: jogar','ESC: menu principal'])
        elif self.state == 'settings':
            self.stage.draw_menu(surface,'CONFIGURAÇÕES',self.menu_items(),self.ui_index,
                ['ESQUERDA/DIREITA: ajustar | ESC: salvar e voltar'])
        elif self.state == 'lan_menu':
            self.stage.draw_menu(surface,'MULTIPLAYER LAN',self.menu_items(),self.ui_index,
                ['Mesma rede Wi-Fi ou cabo | porta TCP 50505','ESC: menu principal'])
        elif self.state == 'lan_address':
            self.stage.draw_menu(surface,'CONECTAR POR IP',self.menu_items(),0,
                ['Digite o IPv4 do computador que hospeda',
                 'ENTER: conectar | BACKSPACE: apagar | ESC: voltar',
                 self.lan_message])
        elif self.state == 'lan_lobby':
            self.stage.draw_menu(surface,'SALA LAN',self.menu_items(),0,
                ['Dois computadores na mesma rede local',
                 'A partida começa automaticamente com 2 jogadores',
                 'ESC: desconectar'])
        elif self.state == 'paused':
            self.stage.draw_menu(surface,'PAUSADO',self.menu_items(),self.ui_index,
                ['P ou ESC: continuar'])
        elif self.state == 'gameover':
            winner=max(range(len(self.players)),key=lambda i:self.players[i].score)+1
            lines=[f'JOGADOR {i+1}: {p.score:07d}' for i,p in enumerate(self.players)]
            if len(self.players)==2:lines.append(f'MAIOR PONTUAÇÃO: JOGADOR {winner}')
            self.stage.draw_menu(surface,'GAME OVER',self.menu_items(),self.ui_index,lines)

    def load_level(self,level):
        """Converte JSON validado em entidades com Factory, sem alterar a física."""
        self.level=Level.from_dict(level.as_dict())
        objects=[ObstacleFactory.create(o) for o in self.level.objects]
        self.bumpers=[o for o in objects if isinstance(o,Bumper)]
        self.targets=[o for o in objects if isinstance(o,Target)]
        self.hole=next((o for o in objects if isinstance(o,Hole)),None)

    def menu_items(self):
        if self.state=='menu':
            return ['Novo jogo','Editor de fases','Configurações','Multiplayer LAN','Sair']
        if self.state=='new_game':
            return [f'Jogadores locais: {self.player_count}',
                    f'Fase: {self.level.name}','Iniciar partida','Voltar']
        if self.state=='settings':
            st=self.settings
            return [f'Efeitos sonoros: {st.sfx_volume}%',f'Música: {st.music_volume}%',
                    f'Mostrar FPS: {"sim" if st.show_fps else "não"}',
                    f'Jogadores padrão: {st.players}','Salvar e voltar']
        if self.state=='lan_menu':
            return ['Hospedar partida','Conectar a servidor','Voltar']
        if self.state=='lan_address':
            return [f'IP: {self.lan_address}']
        if self.state=='lan_lobby':
            return [self.lan_message or 'Conectando...',
                    f'Jogador local: {self.lan_player_id+1}' if self.lan_player_id is not None else 'Aguardando identificação',
                    'ESC: desconectar']
        if self.state=='paused':
            return ['Continuar','Reiniciar','Menu principal']
        if self.state=='gameover':
            return ['Voltar ao menu' if self.remote_mode else 'Jogar novamente','Menu principal']
        return []

    def go_menu(self):
        self.leave_lan()
        self.state='menu'
        self.ui_index=0
        self.balls=[]

    def enter_editor(self):
        self.leave_lan()
        self.editor.load(self.selected_level)
        self.state='editor'

    def choose_level(self,step):
        available=self.level_repo.names()
        try:i=available.index(self.selected_level)
        except ValueError:i=0
        self.selected_level=available[(i+step)%len(available)]
        self.load_level(self.level_repo.load(self.selected_level))

    def ui_action(self,action):
        """Menu controller: centraliza transições sem acoplar teclado à física."""
        items=self.menu_items()
        if action in ('up','down') and items and self.state not in ('lan_address','lan_lobby'):
            self.ui_index=(self.ui_index+(-1 if action=='up' else 1))%len(items)
            return
        if self.state=='lan_lobby':
            if action=='back':self.go_menu()
            return
        if self.state=='lan_address':
            if action=='back':self.state='lan_menu';self.ui_index=1
            elif action=='enter':self.join_lan(self.lan_address)
            return
        if self.state=='new_game':
            if action in ('left','right') and self.ui_index==0:
                self.player_count=1 if self.player_count==2 else 2
                return
            if action in ('left','right') and self.ui_index==1:
                self.choose_level(-1 if action=='left' else 1)
                return
        if self.state=='settings':
            if action in ('left','right') and self.ui_index<4:
                sign=-1 if action=='left' else 1
                if self.ui_index==0:self.settings.sfx_volume=max(0,min(100,self.settings.sfx_volume+sign*10))
                elif self.ui_index==1:self.settings.music_volume=max(0,min(100,self.settings.music_volume+sign*10))
                elif self.ui_index==2:self.settings.show_fps=not self.settings.show_fps
                elif self.ui_index==3:self.settings.players=1 if self.settings.players==2 else 2
                if hasattr(self.audio,'set_volumes'):
                    self.audio.set_volumes(self.settings.music_volume/100,self.settings.sfx_volume/100)
                return
            if action=='back':
                self.settings_repo.save(self.settings)
                self.player_count=self.settings.players
                self.state='menu';self.ui_index=0
                return
        if action=='back':
            if self.state=='paused':self.pause()
            else:self.state='menu';self.ui_index=0
            return
        if action!='enter':return
        if self.state=='menu':
            if self.ui_index==0:self.state='new_game'
            elif self.ui_index==1:self.enter_editor()
            elif self.ui_index==2:self.state='settings'
            elif self.ui_index==3:self.state='lan_menu'
            else:self.running=False
            self.ui_index=0
        elif self.state=='new_game':
            if self.ui_index==0:self.player_count=1 if self.player_count==2 else 2
            elif self.ui_index==1:self.choose_level(1)
            elif self.ui_index==2:self.start_game()
            else:self.go_menu()
        elif self.state=='settings':
            if self.ui_index==4:self.ui_action('back')
            else:self.ui_action('right')
        elif self.state=='lan_menu':
            if self.ui_index==0:self.host_lan()
            elif self.ui_index==1:self.state='lan_address';self.ui_index=0
            else:self.go_menu()
        elif self.state=='paused':
            if self.ui_index==0:self.pause()
            elif self.ui_index==1:self.start_game()
            else:self.go_menu()
        elif self.state=='gameover':
            if self.remote_mode or self.ui_index==1:self.go_menu()
            else:self.start_game()

    def ui_pointer(self,x,y):
        if self.state not in ('menu','new_game','settings','lan_menu','paused','gameover'):return
        # Matches Stage.draw_menu, panel begins at 230 and items at 322.
        idx=int((y-322)//52)
        if 0<=idx<len(self.menu_items()) and 322<=y<322+52*len(self.menu_items()):
            self.ui_index=idx;self.ui_action('enter')

    def editor_action(self,action,unicode=''):
        ed=self.editor
        if ed.editing_name:
            if action=='enter':
                ed.editing_name=False
            elif action=='backspace':
                ed.level.name=ed.level.name[:-1]
                ed.dirty=True
            elif action=='char' and len(unicode)==1 and unicode.isprintable() and len(ed.level.name)<40:
                ed.level.name+=unicode;ed.dirty=True
            elif action=='escape':
                ed.editing_name=False
            return
        if action=='escape':self.state='menu';self.ui_index=0
        elif action in ('v','b','t','h'):
            ed.choose({'v':'select','b':'bumper','t':'target','h':'hole'}[action])
        elif action=='save':
            try:
                self.selected_level=ed.save()
                self.load_level(ed.level)
            except (OSError,ValueError) as exc:ed.notice='Falha ao salvar: '+str(exc)[:55]
        elif action=='new':ed.fresh()
        elif action=='load':
            try:ed.load(self.selected_level)
            except (OSError,ValueError) as exc:ed.notice=str(exc)[:75]
        elif action=='rename':
            ed._remember()
            ed.editing_name=True
        elif action=='undo':ed.undo()
        elif action=='delete':ed.delete()
        elif action=='grow':ed.adjust('radius',2)
        elif action=='shrink':ed.adjust('radius',-2)
        elif action=='points_up':ed.adjust('points',25)
        elif action=='points_down':ed.adjust('points',-25)
        elif action=='test':
            try:
                self.load_level(ed.level)
                self.start_game()
                self.show_message('TESTE DA FASE - ESC: PAUSAR',2)
            except ValueError as exc:ed.notice=str(exc)

    def editor_pointer(self,x,y,button=1,move=False,release=False):
        if release:self.editor.release()
        elif move:self.editor.move(x,y)
        else:self.editor.click(x,y,button)

    def host_lan(self):
        self.leave_lan()
        try:
            self.lan_server=LANServer(self.root,self.level).start()
            self.lan_client=LANClient().connect('127.0.0.1',self.lan_server.port)
            self.remote_mode=True
            self.state='lan_lobby'
            self.lan_message=f'Hospedando: porta {self.lan_server.port} | verifique seu IP no ipconfig'
        except (OSError,ValueError) as exc:
            self.lan_message='Falha ao hospedar: '+str(exc)[:64]
            self.leave_lan()
            self.state='lan_menu'

    def join_lan(self,address):
        self.leave_lan()
        try:
            self.lan_client=LANClient().connect(address,PORT)
            self.remote_mode=True
            self.state='lan_lobby'
            self.lan_message=f'Conectado a {address}:{PORT} - aguardando oponente'
        except (OSError,ValueError) as exc:
            self.lan_message='Falha de conexão: '+str(exc)[:65]
            self.state='lan_address'

    def leave_lan(self):
        if self.lan_client:self.lan_client.close();self.lan_client=None
        if self.lan_server:self.lan_server.stop();self.lan_server=None
        self.lan_player_id=None
        self.remote_mode=False

    def poll_lan(self):
        if not self.lan_client:return
        for msg in self.lan_client.poll():
            if msg['type']=='welcome':self.lan_player_id=msg['player_id']
            elif msg['type']=='lobby':
                self.state='lan_lobby'
                self.lan_message=f'Aguardando jogadores: {msg.get("connected",0)}/2'
            elif msg['type']=='snapshot':
                self.apply_snapshot(msg)
            elif msg['type']=='error':self.lan_message=msg.get('message','Erro de rede')
            elif msg['type']=='disconnected':
                self.lan_message=msg.get('message','Desconectado')
                self.leave_lan()
                self.state='lan_menu'
                self.ui_index=0

    def apply_snapshot(self,msg):
        """Cliente replica apenas a VISÃO, sem simular física local."""
        from modulos.physics.collision_manager import Vector
        previous_state=self.state
        old_bumpers=[b.flash for b in self.bumpers]
        old_targets=[t.flash for t in self.targets]
        objects=msg.get('level')
        if objects is not None and objects!=self.level.as_dict():
            self.load_level(Level.from_dict(objects))
        self.state=msg['state']
        self.active_player=msg['active_player']
        self.players=[PlayerScore(**p) for p in msg['players']]
        self.player_count=len(self.players)
        self.balls=[]
        for d in msg['balls']:
            ball=Ball(self.trajectory,d['x'],d['y'],ready=d['ready'])
            ball.velocity=Vector(d['vx'],d['vy'])
            ball.active=d['active']
            self.balls.append(ball)
        for f,d in zip(self.flippers,msg['flippers']):
            f.angle=d['angle'];f.active=d['active']
        self.plunger.charge=msg['plunger']
        self.banner=msg['banner'];self.banner_time=msg['banner_time']
        for e,t in zip(self.bumpers,msg['bumpers_flash']):e.flash=t
        for e,t in zip(self.targets,msg['targets_flash']):e.flash=t
        if self.hole:self.hole.flash=msg['hole_flash']
        if self.state=='playing' and previous_state!='playing':self.audio.music_start()
        if self.state=='gameover' and previous_state!='gameover':self.audio.sound('gameover')
        if any(x>0.10 and (i>=len(old_bumpers) or old_bumpers[i]==0)
               for i,x in enumerate(msg['bumpers_flash'])):
            self.audio.sound('bumper')
        if any(x>0.15 and (i>=len(old_targets) or old_targets[i]==0)
               for i,x in enumerate(msg['targets_flash'])):
            self.audio.sound('target')

    def shutdown(self):
        self.leave_lan()
