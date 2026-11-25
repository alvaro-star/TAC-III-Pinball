"""Regras do pinball - menu, estados, jogo para 1-2 pessoas, pontuação, vidas e fases."""
from pathlib import Path
import math
from modulos.config.constants import (LEFT, RIGHT, BOTTOM, LAUNCH_X, LAUNCH_Y, LANE_LEFT,
                       ARCH_CENTER_X, ARCH_CENTER_Y, ARCH_RADIUS)
from modulos.physics.collision_manager import Vector, CollisionManager
from modulos.physics.trajectory_controller import TrajectoryController
from modulos.entities.ball import Ball
from modulos.entities.actuators import Flipper, Plunger
from modulos.effects.score import PlayerScore
from modulos.effects.highscores import HighScores
from modulos.effects.players import Players, MAX_NAME
from modulos.config.settings import Settings, ITEMS
from modulos.core.levels import LevelStore, Level, DEFAULT_NAME
from modulos.core.level_editor import LevelEditor, palette_hit
from modulos.ui.menu import Menu, MAIN_ITEMS, PAUSE_ITEMS, EDIT_ITEMS

MAX_LEVEL_NAME = 16
from modulos.ui.stage import Stage


class Game:
    def __init__(self, inputs, audio, root, storage=None):
        """storage: pasta para settings.json e scores.json; None = só em memória."""
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
        self.flippers = [Flipper('left',(240,782)),Flipper('right',(480,782))]
        self.plunger = Plunger()
        # Bumpers, alvos e buracos vêm da fase escolhida (arquivo JSON), ver load_table.
        self.bumpers, self.targets, self.holes = [], [], []
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
        storage = Path(storage) if storage else None
        self.settings = Settings(storage/'settings.json' if storage else None)
        self.highscores = HighScores(storage/'scores.json' if storage else None)
        self.roster = Players(storage/'players.json' if storage else None)
        self.levels = LevelStore(storage/'fases' if storage else None)
        self.level = self.levels.find(self.settings.fase) or self.levels.default()
        self.level_list = []
        self.editor = None
        self.text = None  # caixa de digitação: prompt, valor, finalidade, tela de volta, erro
        self.confirm_delete = None  # item marcado para apagar (exige Del duas vezes)
        self.player_names = [self.roster.active]
        self.menu = Menu()
        # Tela para onde as configurações voltam: menu inicial ou pausa.
        self.settings_return = 'menu'
        self.new_records = []
        self.load_table(self.level)
        self.apply_settings()

    def load_table(self, level):
        self.bumpers, self.targets, self.holes = level.build()

    def set_level(self, level):
        self.level = level
        self.settings.values['fase'] = '' if level.builtin else level.name
        self.settings.save()
        self.load_table(level)

    def apply_settings(self):
        self.trajectory.gravity_scale = self.settings.gravity/100
        if hasattr(self.audio,'apply'):
            self.audio.apply(self.settings)

    def toggle_sound(self):
        self.settings.adjust('sound_on',1)
        self.settings.save()
        self.apply_settings()

    def back_to_menu(self):
        self.state = 'menu'
        self.balls = []
        self.load_table(self.level)
        self.banner_time = 0.0
        if hasattr(self.audio,'music_stop'):
            self.audio.music_stop()

    def menu_action(self, action):
        """action: 'up', 'down', 'left', 'right', 'enter' ou 'back'."""
        step = {'up':-1,'down':1}.get(action)
        if self.state == 'menu':
            if step:
                self.menu.move('menu',step)
            elif action == 'enter':
                self.select(self.menu.main_choice())
        elif self.state == 'settings':
            key = self.menu.settings_choice()
            if step:
                self.menu.move('settings',step)
            elif action in ('left','right') and key:
                self.settings.adjust(key,-1 if action=='left' else 1)
                self.apply_settings()
            elif action == 'enter' and key and isinstance(self.settings.values[key],bool):
                self.settings.adjust(key,1)
                self.apply_settings()
            elif action == 'back' or (action == 'enter' and key is None):
                self.settings.save()
                self.state = self.settings_return
        elif self.state == 'paused':
            if step:
                self.menu.move('paused',step)
            elif action == 'enter':
                self.select_pause(self.menu.pause_choice())
            elif action == 'back':
                self.pause()
        elif self.state == 'levels':
            self.levels_action(action,step)
        elif self.state == 'players':
            self.players_action(action,step)
        elif self.state == 'editor_menu':
            if step:
                self.menu.move('editor_menu',step)
            elif action == 'enter':
                self.select_edit(self.menu.edit_choice())
            elif action == 'back':
                self.state = 'editing'
        elif action in ('enter','back'):
            self.state = 'menu'

    # ---- Lista de fases: escolher, jogar, criar, editar e apagar.
    def open_levels(self, select=None):
        self.level_list = self.levels.all()
        names = [lv.name for lv in self.level_list]
        target = select or self.level.name
        self.menu.levels_index = names.index(target) if target in names else 0
        self.confirm_delete = None
        self.state = 'levels'
        self.preview_level()

    def selected_level(self):
        i = self.menu.levels_index
        return self.level_list[i] if i < len(self.level_list) else None

    def preview_level(self):
        # A mesa ao fundo mostra a fase sob o cursor.
        self.load_table(self.selected_level() or self.level)

    def levels_action(self, action, step):
        level = self.selected_level()
        row = self.menu.levels_index - len(self.level_list)  # 0 = NOVA FASE, 1 = VOLTAR
        if action != 'delete':
            self.confirm_delete = None
        if step:
            self.menu.move('levels',step,len(self.level_list)+2)
            self.preview_level()
        elif action == 'back' or (action == 'enter' and row == 1):
            self.load_table(self.level)
            self.state = 'menu'
        elif action == 'new' or (action == 'enter' and row == 0):
            self.ask_text('NOME DA NOVA FASE','level','levels',MAX_LEVEL_NAME)
        elif level is None:
            return
        elif action == 'enter':
            self.set_level(level)
            self.state = 'menu'
        elif action == 'play':
            self.set_level(level)
            self.start_game()
        elif action == 'edit':
            if level.builtin:
                # A padrão é somente leitura: edita-se uma cópia com outro nome.
                self.ask_text('NOME DA CÓPIA DA FASE PADRÃO','copy','levels',MAX_LEVEL_NAME)
            else:
                self.open_editor(level)
        elif action == 'delete' and not level.builtin:
            if self.confirm_delete != level.name:
                self.confirm_delete = level.name
                return
            self.confirm_delete = None
            if self.levels.delete(level) and level.name == self.level.name:
                self.set_level(self.levels.default())
            self.open_levels(self.level.name)

    # ---- Jogadores cadastrados.
    def open_players(self):
        names = self.roster.names
        self.menu.players_index = names.index(self.roster.active)
        self.confirm_delete = None
        self.state = 'players'

    def players_action(self, action, step):
        names = self.roster.names
        i = self.menu.players_index
        row = i - len(names)  # 0 = NOVO JOGADOR, 1 = VOLTAR
        if action != 'delete':
            self.confirm_delete = None
        if step:
            self.menu.move('players',step,len(names)+2)
        elif action == 'back' or (action == 'enter' and row == 1):
            self.state = 'menu'
        elif action == 'new' or (action == 'enter' and row == 0):
            self.ask_text('NOME DO NOVO JOGADOR','player','players',MAX_NAME)
        elif row >= 0:
            return
        elif action == 'enter':
            self.roster.select(names[i])
            self.state = 'menu'
        elif action == 'delete':
            if self.confirm_delete != names[i]:
                self.confirm_delete = names[i]
                return
            self.confirm_delete = None
            self.roster.remove(names[i])
            self.menu.players_index = min(i,len(self.roster.names)-1)

    # ---- Caixa de texto para nomes de jogadores e fases.
    def ask_text(self, prompt, purpose, back, limit):
        self.text = {'prompt':prompt,'value':'','purpose':purpose,'back':back,
                     'limit':limit,'error':''}
        self.state = 'text_input'

    def text_type(self, chars):
        if self.state != 'text_input':
            return
        allowed = ''.join(c for c in chars.upper() if c.isalnum() or c in ' -_')
        self.text['value'] = (self.text['value']+allowed)[:self.text['limit']]
        self.text['error'] = ''

    def text_action(self, action):
        """action: 'enter', 'back' ou 'erase'."""
        if self.state != 'text_input':
            return
        t = self.text
        if action == 'erase':
            t['value'] = t['value'][:-1]
            t['error'] = ''
        elif action == 'back':
            self.state = t['back']
        elif action == 'enter':
            name = ' '.join(t['value'].split())
            if not name:
                t['error'] = 'DIGITE UM NOME'
            elif t['purpose'] == 'player':
                if self.roster.add(name) is None:
                    t['error'] = 'JOGADOR JÁ CADASTRADO'
                else:
                    self.open_players()
            elif self.levels.name_taken(name):
                t['error'] = 'JÁ EXISTE UMA FASE COM ESSE NOME'
            else:
                objects = self.levels.default().objects if t['purpose'] == 'copy' else []
                self.open_editor(Level(name,objects))

    # ---- Editor de fases.
    def open_editor(self, level):
        self.editor = LevelEditor(level)
        self.balls = []
        self.load_table(self.editor.level)
        self.state = 'editing'

    def editor_click(self, x, y, button):
        """button 1 = colocar peça (ou escolher na paleta), 3 = remover."""
        if self.state != 'editing':
            return
        editor = self.editor
        editor.cursor = (x,y)
        index = palette_hit(x,y)
        if index is not None:
            editor.choose(index)
        elif button == 1 and editor.place(x,y):
            self.audio.sound('target')
        elif button == 3 and editor.remove_at(x,y):
            self.audio.sound('lose')
        self.load_table(editor.level)

    def editor_command(self, command, value=0):
        """command: 'choose' (value = índice), 'cycle' (value = ±1), 'undo' ou 'menu'."""
        if self.state != 'editing':
            return
        if command == 'choose':
            self.editor.choose(value)
        elif command == 'cycle':
            self.editor.cycle(value)
        elif command == 'undo':
            self.editor.undo()
            self.load_table(self.editor.level)
        elif command == 'menu':
            self.menu.edit_index = 0
            self.state = 'editor_menu'

    def select_edit(self, choice):
        level = self.editor.level
        if choice == 'continuar':
            self.state = 'editing'
        elif choice == 'limpar':
            self.editor.clear()
            self.load_table(level)
            self.state = 'editing'
        elif choice == 'descartar':
            self.editor = None
            self.open_levels()
        elif choice in ('salvar','jogar'):
            self.levels.save(level)
            self.editor = None
            if choice == 'jogar' or level.name == self.level.name:
                self.set_level(level)
            if choice == 'jogar':
                self.start_game()
            else:
                self.open_levels(level.name)

    def select(self, choice):
        if choice in ('novo','multi'):
            self.player_count = 1 if choice == 'novo' else 2
            self.start_game()
        elif choice == 'score':
            self.state = 'scores'
        elif choice == 'fases':
            self.open_levels()
        elif choice == 'jogador':
            self.open_players()
        elif choice == 'config':
            self.open_settings('menu')
        elif choice == 'sair':
            self.running = False

    def select_pause(self, choice):
        if choice == 'continuar':
            self.pause()
        elif choice == 'reiniciar':
            self.start_game()
        elif choice == 'config':
            self.open_settings('paused')
        elif choice == 'menu':
            self.back_to_menu()
        elif choice == 'sair':
            self.running = False

    def open_settings(self, return_to):
        self.menu.settings_index = 0
        self.settings_return = return_to
        self.state = 'settings'

    def start_game(self):
        self.players = [PlayerScore(remaining=self.settings.balls_per_player)
                        for _ in range(self.player_count)]
        self.player_names = [self.roster.active,self.roster.second()][:self.player_count]
        self.load_table(self.level)
        self.new_records = []
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
            self.menu.pause_index = 0
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
            self.record_scores()
            return
        for step in range(1,len(self.players)+1):
            nxt=(self.active_player+step)%len(self.players)
            if self.players[nxt].remaining>0:
                self.active_player=nxt
                break
        self.balls=[Ball(self.trajectory)]
        self.plunger=Plunger()
        self.show_message('PRÓXIMA BOLA',1.5)

    def result_text(self):
        a,b = self.players[0].score,self.players[1].score
        if a == b:
            return 'EMPATE!'
        return f'MAIOR PONTUAÇÃO: {self.player_names[0 if a > b else 1]}'

    def record_scores(self):
        added = []
        for i,p in enumerate(self.players):
            added.append((i,self.highscores.add(p.score,self.player_names[i],self.level.name)))
        # Posições calculadas depois de registrar todos os jogadores da partida.
        self.new_records = [(i,self.highscores.rank(e)) for i,e in added
                            if e is not None and self.highscores.rank(e)]

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
        for entity in [*self.targets,*self.bumpers,*self.holes]:
            entity.update(dt)
        for ball in list(self.balls):
            # Subpassos: a bola anda no máximo meio raio por passo e não atravessa paredes.
            steps = max(1, math.ceil(ball.velocity.magnitude()*dt/(ball.radius*0.5)))
            for _ in range(steps):
                ball.update(dt/steps)
                if ball.ready:
                    break
                self.collide_world(ball)
            if ball.ready:
                continue
            # Lançamento fraco: a bola volta ao lançador sem custar uma vida.
            if ball.position.x>LANE_LEFT and ball.position.y>=LAUNCH_Y and ball.velocity.y>0:
                ball.position=Vector(LAUNCH_X,LAUNCH_Y)
                ball.velocity=Vector()
                ball.ready=True
                continue
            # Evita que uma bola sem velocidade permaneça travada indefinidamente
            # (exceto quando o jogador a segura num flipper levantado).
            if ball.velocity.magnitude() < 45 and not any(f.active for f in self.flippers):
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
            if hit and flipper.swinging_up and ball.flipper_cooldown<=0:
                # O golpe para cima garante resposta imediata ao comando RF2/RF3;
                # com o flipper já parado no alto a bola só rebate e pode ser segurada.
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
        for entity in self.holes:
            value=entity.on_collide(ball)
            if value:
                self.point(value,'hole')
                self.show_message(f'BÔNUS +{value}',1.2)
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
        hint='W/S OU SETAS: ESCOLHER  |  ENTER: CONFIRMAR'
        card=self.stage.menu_card
        if self.state=='menu':
            subtitle=f'JOGADOR: {self.roster.active}   |   FASE: {self.level.name}'
            card(surface,'PINBALL ARCADE',[(label,None) for _,label in MAIN_ITEMS],
                 self.menu.main_index,hint,subtitle=subtitle)
        elif self.state=='settings':
            rows=[(label,self.settings.text(key)) for key,label,*_ in ITEMS]+[('VOLTAR',None)]
            card(surface,'CONFIGURAÇÕES',rows,self.menu.settings_index,
                 'W/S: ESCOLHER  |  A/D OU SETAS: AJUSTAR  |  ESC: VOLTAR',arrows=True)
        elif self.state=='scores':
            rows=[(f"{i+1:2d}. {e['label']}"+(f"  ·  {e['fase']}" if e.get('fase') else ''),
                   f"{e['score']:07d}") for i,e in enumerate(self.highscores.entries)]
            mine=[i for i,e in enumerate(self.highscores.entries) if e['label']==self.roster.active]
            card(surface,'SCORE',rows or [('NENHUMA PONTUAÇÃO AINDA',None)],None,
                 'ENTER OU ESC: VOLTAR',highlight=mine,
                 subtitle=f'JOGADOR ATIVO: {self.roster.active}')
        elif self.state=='levels':
            rows=[(lv.name,'ATIVA' if lv.name==self.level.name else
                   ('PADRÃO' if lv.builtin else f'{len(lv.objects)} PEÇAS'))
                  for lv in self.level_list]+[('+ NOVA FASE',None),('VOLTAR',None)]
            footer='ENTER: ESCOLHER  |  J: JOGAR  |  E: EDITAR  |  N: NOVA  |  DEL: APAGAR'
            if self.confirm_delete:
                footer=f'DEL DE NOVO PARA APAGAR "{self.confirm_delete}"'
            card(surface,'EDITOR DE FASES',rows,self.menu.levels_index,footer,
                 subtitle='A FASE ESCOLHIDA É A JOGADA EM NOVO JOGO',compact=True)
        elif self.state=='players':
            rows=[(n,('ATIVO  ·  ' if n==self.roster.active else '')+
                   f'RECORDE {self.highscores.best(n):07d}') for n in self.roster.names]
            rows+=[('+ NOVO JOGADOR',None),('VOLTAR',None)]
            footer='ENTER: JOGAR COM ESTE NOME  |  N: NOVO  |  DEL: APAGAR  |  ESC: VOLTAR'
            if self.confirm_delete:
                footer=f'DEL DE NOVO PARA APAGAR "{self.confirm_delete}"'
            card(surface,'JOGADORES',rows,self.menu.players_index,footer,compact=True)
        elif self.state=='text_input':
            self.stage.text_box(surface,self.text)
        elif self.state=='editing':
            self.stage.draw_editor(surface,self.editor)
        elif self.state=='editor_menu':
            self.stage.draw_editor(surface,self.editor)
            card(surface,'EDITOR',[(label,None) for _,label in EDIT_ITEMS],self.menu.edit_index,
                 'W/S: ESCOLHER  |  ENTER: CONFIRMAR  |  ESC: VOLTAR',
                 subtitle=f'{self.editor.level.name}  ·  {len(self.editor.objects)} PEÇAS')
        elif self.state=='paused':
            card(surface,'PAUSADO',[(label,None) for _,label in PAUSE_ITEMS],
                 self.menu.pause_index,'W/S: ESCOLHER  |  ENTER: CONFIRMAR  |  ESC: CONTINUAR')
        elif self.state=='gameover':
            lines=['FIM DE JOGO  -  TODAS AS BOLAS FORAM USADAS']
            if len(self.players)==2:
                lines += [f'{self.player_names[0]}: {self.players[0].score:07d}',
                          f'{self.player_names[1]}: {self.players[1].score:07d}',
                          self.result_text()]
            else:
                lines += [f'{self.player_names[0]}: {self.players[0].score:07d}']
            if self.new_records:
                i,rank=min(self.new_records,key=lambda r:r[1])
                who='' if len(self.players)==1 else f'{self.player_names[i]}: '
                lines += [f'NOVO RECORDE! {who}{rank}º LUGAR NO SCORE']
            lines += ['ENTER: JOGAR NOVAMENTE  |  ESC: MENU']
            self.stage.overlay(surface,'GAME OVER',lines,(252,95,125))
