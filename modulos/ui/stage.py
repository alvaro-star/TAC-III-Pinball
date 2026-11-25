"""Mesa, cenografia pixel art e sprites recortados das pranchas fornecidas."""
import math
import random
from pathlib import Path
import pygame
from .sprite_sheet import SpriteSheet
from .menu import MENU_STATES
from modulos.core.levels import PIECES, PIECE_KEYS
from modulos.core.level_editor import palette_slot, PALETTE_SIZE, PALETTE_STEP, SHORT
from modulos.config.constants import (WIDTH, HEIGHT, LEFT, RIGHT, TOP, BOTTOM, COLORS,
                       ARCH_CENTER_X, ARCH_CENTER_Y, ARCH_RADIUS)


class Stage:
    def __init__(self, root):
        self.root = Path(root)
        self.images = {}
        self.scaled_images = {}
        pinball_folder = self.root / 'assets' / 'pinball'
        # O atlas é a sprite sheet que o jogo usa efetivamente em runtime.
        atlas = SpriteSheet(pinball_folder)
        for name in atlas.sprites:
            self.images[name] = atlas.get(name)
        # Fontes OFL incluídas no projeto: Exo 2 (textos) e Orbitron (títulos).
        fontfile = self.root/'assets'/'fonts'/'Exo2.ttf'
        self.font_name = str(fontfile) if fontfile.exists() else None
        titlefont = self.root/'assets'/'fonts'/'Orbitron.ttf'
        self.title_fontfile = str(titlefont) if titlefont.exists() else self.font_name
        self.font_cache = {}
        self.base = self._create_background()

    def font(self, size, title=False):
        key = (size,title)
        if key not in self.font_cache:
            font = pygame.font.Font(self.title_fontfile if title else self.font_name, size)
            font.set_bold(not title)  # Orbitron já é encorpada; negrito sintético a deixa vazada
            self.font_cache[key] = font
        return self.font_cache[key]

    def text(self, surface, message, x, y, size=19, color=None, center=False, title=False,
             valign=None):
        """valign alinha pela altura das maiúsculas: 'top' (topo da letra em y),
        'middle' (centro da letra em y) ou 'bottom' (linha de base em y)."""
        fg = COLORS['white'] if color is None else color
        font = self.font(size,title)
        img = font.render(str(message),True,fg)
        box = img.get_rect()
        top = int(y)
        if valign:
            ascent, cap = font.get_ascent(), font.metrics('H')[0][3]
            top = round(y-ascent+{'top':cap,'middle':cap/2,'bottom':0}[valign])
        if center:
            box.midtop = (int(x),top)
        else:
            box.topleft = (int(x),top)
        surface.blit(img,box)

    @staticmethod
    def _fill_table(surface, color, grow=0):
        """Preenche a silhueta da mesa: semicírculo no topo e base retangular."""
        cx,cy = int(ARCH_CENTER_X),int(ARCH_CENTER_Y)
        radius = int(ARCH_RADIUS)+grow
        pygame.draw.circle(surface,color,(cx,cy),radius,draw_top_left=True,draw_top_right=True)
        bottom = int(BOTTOM)+min(grow,13)
        pygame.draw.rect(surface,color,(cx-radius,cy-1,2*radius,bottom-cy+1),
                         border_bottom_left_radius=20+grow,border_bottom_right_radius=20+grow)

    def _create_background(self):
        s = pygame.Surface((WIDTH,HEIGHT))
        s.fill(COLORS['bg'])
        galaxy = self.root/'assets'/'image'/'back.jpg'
        if galaxy.exists():
            bg = pygame.image.load(str(galaxy)).convert()
            bg = pygame.transform.scale(bg,(WIDTH,HEIGHT))
            bg.set_alpha(110)
            s.blit(bg,(0,0))
        for grow,color in ((17,(12,31,61)),(10,(36,114,200)),(5,(12,31,61)),(0,(7,17,37))):
            self._fill_table(s,color,grow)
        # Fundo quadriculado da estética arcade / pixel art.
        grid = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        for y in range(int(TOP)+4,int(BOTTOM),26):
            for x in range(int(LEFT)+3,int(RIGHT)-2,26):
                tone = 13 if ((x//26+y//26)%2==0) else 17
                pygame.draw.rect(grid,(tone,tone+16,tone+30,255),(x,y,25,25))
        mask = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        self._fill_table(mask,(255,255,255,255))
        grid.blit(mask,(0,0),special_flags=pygame.BLEND_RGBA_MIN)
        s.blit(grid,(0,0))
        # Reflexo colorido nos limites da mesa e trilha de lançamento.
        pygame.draw.circle(s,COLORS['cyan'],(int(ARCH_CENTER_X),int(ARCH_CENTER_Y)),int(ARCH_RADIUS)-1,3,
                           draw_top_left=True,draw_top_right=True)
        pygame.draw.line(s,COLORS['cyan'],(LEFT+2,ARCH_CENTER_Y),(LEFT+2,688),3)
        pygame.draw.line(s,COLORS['cyan'],(RIGHT-2,ARCH_CENTER_Y),(RIGHT-2,822),3)
        pygame.draw.line(s,(66,118,183),(568,341),(568,819),5)
        pygame.draw.line(s,(13,54,91),(582,342),(582,820),3)
        pygame.draw.arc(s,(68,138,204),(170,TOP+16,380,192),math.pi*1.02,math.pi*1.97,4)
        pygame.draw.line(s,(45,120,208),(LEFT,677),(240,782),7)
        pygame.draw.line(s,(45,120,208),(568,683),(480,782),7)
        # Barreira lateral em ziguezague (slingshots).
        pygame.draw.lines(s,(255,169,54),False,[(158,619),(222,701),(194,681)],6)
        pygame.draw.lines(s,(255,169,54),False,[(514,619),(475,701),(496,681)],6)
        rng = random.Random(83)
        for _ in range(70):
            x=rng.randint(15,WIDTH-15);y=rng.randint(112,HEIGHT-18)
            inside = LEFT-20 < x < RIGHT+20 and y < BOTTOM+22 and (
                y >= ARCH_CENTER_Y or math.hypot(x-ARCH_CENTER_X,y-ARCH_CENTER_Y) < ARCH_RADIUS+20)
            if not inside:
                pygame.draw.circle(s,(130,177,217),(x,y),rng.choice([1,1,1,2]))
        return s

    def hole(self, surface, cx, cy, flash=0.0, scale=1.0):
        """Buraco bônus: anel com luzes; desenhado onde a fase o posiciona."""
        c=(int(cx),int(cy))
        pygame.draw.circle(surface,(27,63,91),c,round(46*scale))
        pygame.draw.circle(surface,(112,48,140),c,round(40*scale),width=3)
        pygame.draw.circle(surface,(23,11,42),c,round(29*scale))
        for i in range(10):
            phi = 2*math.pi*i/10
            pygame.draw.circle(surface,(246,89,165),(round(cx+35*scale*math.cos(phi)),
                                                     round(cy+35*scale*math.sin(phi))),3)
        if flash:
            pygame.draw.circle(surface,COLORS['pink'],c,round(45*scale),4)
        if scale>=1:
            self.text(surface,'BÔNUS',cx,cy-14,13,COLORS['pink'],center=True)

    def piece(self, surface, key, cx, cy, flash=0.0, diameter=None):
        """Desenha uma peça do catálogo de fases (paleta, prévia ou mesa)."""
        _,_,radius,_,sprite = PIECES[key]
        if sprite is None:
            self.hole(surface,cx,cy,flash,1.0 if diameter is None else diameter/92)
            return
        extra = 8 if key.startswith('bumper') else 7
        self.sprite(surface,sprite,cx,cy,diameter or int(radius*2+extra),flash)

    def sprite(self, surface, name, cx, cy, diameter, flash=0.0):
        im = self.images.get(name)
        if im is None:
            pygame.draw.circle(surface,COLORS['cyan'],(int(cx),int(cy)),diameter//2)
            return
        key = (name, diameter)
        if key not in self.scaled_images:
            self.scaled_images[key] = pygame.transform.smoothscale(im, (diameter, diameter))
        im = self.scaled_images[key]
        dst = im.get_rect(center=(int(cx),int(cy)))
        if flash:
            pygame.draw.circle(surface,COLORS['gold'],(int(cx),int(cy)),diameter//2+8,3)
        surface.blit(im,dst)

    def draw_playfield(self, surface, game):
        surface.blit(self.base,(0,0))
        # Luzes: cada sprite vem das pranchas PINBALL1-3 anexadas ao trabalho.
        # Cada entidade guarda a chave da peça (label) definida no arquivo da fase.
        for hole in game.holes:
            self.hole(surface,hole.x,hole.y,hole.flash)
        for entity in [*game.targets,*game.bumpers]:
            self.piece(surface,entity.label,entity.x,entity.y,entity.flash)
        # Flippers animados; cor e formato reproduzem a identidade das pranchas.
        for flip in game.flippers:
            a=(round(flip.pivot.x),round(flip.pivot.y))
            b=(round(flip.tip.x),round(flip.tip.y))
            pygame.draw.line(surface,(2,6,19),a,b,32)
            pygame.draw.line(surface,(214,224,235),a,b,26)
            color=(39,153,252) if flip.side=='left' else (245,71,82)
            pygame.draw.line(surface,color,a,b,18)
            pygame.draw.line(surface,(162,235,255),a,b,3)
            pygame.draw.circle(surface,(22,38,59),a,16)
            pygame.draw.circle(surface,(232,241,248),a,8)
            pygame.draw.circle(surface,color,b,13)
        # Canal do lançador: pino e medidor de carga à direita.
        pygame.draw.rect(surface,(12,24,42),(579,701,22,121),border_radius=8)
        pygame.draw.rect(surface,(49,85,112),(583,709,14,104),width=2,border_radius=5)
        charge = game.plunger.charge
        if charge > 0:
            h=round(charge*96)
            pygame.draw.rect(surface,COLORS['gold'],(585,808-h,10,h),border_radius=3)
        pygame.draw.line(surface,(188,213,235),(577,818+charge*10),(605,818+charge*10),5)
        for ball in game.balls:
            if ball.active:
                cx,cy=ball.position.x,ball.position.y
                pygame.draw.circle(surface,(26,111,172),(round(cx),round(cy)),16)
                self.sprite(surface,'ball',cx,cy,26)
        self.draw_hud(surface,game)

    # Painel do topo: margem interna igual em cima e embaixo (fileiras topo/meio/base).
    HUD = pygame.Rect(20,8,WIDTH-40,103)
    HUD_PAD = 18
    HUD_TOP = HUD.top+HUD_PAD
    HUD_MID = HUD.centery
    HUD_BOTTOM = HUD.bottom-HUD_PAD

    def draw_hud(self,s,game):
        pygame.draw.rect(s,(7,12,29),self.HUD,border_radius=13)
        pygame.draw.rect(s,(40,114,187),self.HUD,2,border_radius=13)
        self.text(s,'PINBALL',43,self.HUD_TOP,26,COLORS['cyan'],title=True,valign='top')
        if game.state not in ('editing','editor_menu'):
            self.text(s,'TAC III  /  ARCADE',43,self.HUD_MID+4,13,COLORS['muted'],valign='middle')
        if game.state in MENU_STATES:
            # Fora da partida o placar da última partida não aparece.
            return
        for i,score in enumerate(game.players):
            x = 322 if i == 0 else 506
            fg = COLORS['gold'] if game.active_player == i else COLORS['muted']
            names = getattr(game,'player_names',[])
            self.text(s,names[i] if i < len(names) else f'JOGADOR {i+1}',x,self.HUD_TOP,14,fg,
                      valign='top')
            self.text(s,f'{score.score:07d}',x,self.HUD_MID,26,COLORS['white'],valign='middle')
            self.text(s,f'BOLAS: {score.remaining}',x,self.HUD_BOTTOM,14,fg,valign='bottom')
        self.text(s,f'FASE: {game.level.name}',43,self.HUD_BOTTOM,14,COLORS['gold'],valign='bottom')
        if len(game.players)==1:
            self.text(s,'A / D - FLIPPERS    ESPAÇO - LANÇAR    P - PAUSAR',360,864,15,COLORS['muted'],center=True)
        else:
            self.text(s,'2 JOGADORES  |  ALTERNÂNCIA DE TURNOS  |  P - PAUSAR',360,864,15,COLORS['muted'],center=True)
        if game.state == 'playing' and any(b.ready for b in game.balls):
            self.text(s,'SEGURE E SOLTE ESPAÇO PARA LANÇAR',351,811,16,COLORS['gold'],center=True)
        if game.players:
            bonus=game.players[game.active_player]
            labels=[]
            if bonus.multiplier_time:
                labels.append(f'2X {bonus.multiplier_time:.0f}s')
                self.sprite(s, 'icon_2x', 262, 164, 30)
            if len(game.balls)>1:labels.append('MULTIBALL')
            if labels:
                self.text(s,'  |  '.join(labels),372,146,15,COLORS['gold'],center=True)
        if game.banner_time>0:
            self.text(s,game.banner,359,541,24,COLORS['gold'],center=True,title=True)
        self.text(s,'SOM: '+('DESLIGADO' if game.audio.muted else 'LIGADO')+' [M]',526,884,12,COLORS['muted'])
        # Indicadores úteis para demonstrar os requisitos de desempenho/OpenGL.
        if game.settings.show_fps:
            backend = getattr(game, 'render_backend', 'a verificar').upper()
            fps = getattr(game, 'fps', 0.0)
            self.text(s, f'RENDER: {backend} / FPS: {fps:.0f}', 20,884,11,COLORS['muted'])

    MAX_ROWS = 11

    def menu_card(self, s, title, rows, selected=None, footer='', accent=None,
                  subtitle='', highlight=(), compact=False, arrows=False):
        """Cartão central com linhas (rótulo, valor); a linha selecionada fica destacada.
        Listas longas rolam para manter a seleção visível."""
        tint=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        tint.fill((4,9,22,205))
        s.blit(tint,(0,0))
        first=0
        if len(rows)>self.MAX_ROWS:
            first=min(max(0,(selected or 0)-self.MAX_ROWS//2),len(rows)-self.MAX_ROWS)
        shown=rows[first:first+self.MAX_ROWS]
        spacing=38 if compact or len(rows)>8 else 44
        top_gap=34 if subtitle else 0
        height=128+top_gap+len(shown)*spacing+(46 if footer else 0)
        card=pygame.Rect(50,(HEIGHT-height)//2,WIDTH-100,height)
        pygame.draw.rect(s,(13,25,51),card,border_radius=20)
        pygame.draw.rect(s,COLORS['cyan'],card,3,border_radius=20)
        self.text(s,title,WIDTH//2,card.y+26,40,accent or COLORS['cyan'],center=True,title=True)
        if subtitle:
            self.text(s,subtitle,WIDTH//2,card.y+84,15,COLORS['muted'],center=True)
        y=card.y+106+top_gap
        for i,(label,value) in enumerate(shown,start=first):
            active = i==selected
            if active:
                row=pygame.Rect(card.x+22,y-10,card.w-44,spacing-6)
                pygame.draw.rect(s,(28,58,104),row,border_radius=10)
                pygame.draw.rect(s,COLORS['gold'],row,2,border_radius=10)
            fg = COLORS['gold'] if active or i in highlight else COLORS['white']
            if value is None:
                self.text(s,label,WIDTH//2,y,20,fg,center=True)
            else:
                self.text(s,label,card.x+44,y,18,fg)
                shown_value = f'<  {value}  >' if active and arrows else value
                img = self.font(17).render(str(shown_value),True,fg)
                s.blit(img,(card.right-44-img.get_width(),y+1))
            y+=spacing
        if first>0:
            self.text(s,'▲',card.right-30,card.y+106+top_gap-30,14,COLORS['muted'])
        if first+len(shown)<len(rows):
            self.text(s,'▼',card.right-30,y-12,14,COLORS['muted'])
        if footer:
            self.text(s,footer,WIDTH//2,card.bottom-40,13,COLORS['muted'],center=True)

    def text_box(self, s, box):
        """Caixa de digitação de nome (jogador ou fase)."""
        tint=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        tint.fill((4,9,22,215))
        s.blit(tint,(0,0))
        card=pygame.Rect(70,300,WIDTH-140,270)
        pygame.draw.rect(s,(13,25,51),card,border_radius=20)
        pygame.draw.rect(s,COLORS['cyan'],card,3,border_radius=20)
        self.text(s,box['prompt'],WIDTH//2,card.y+30,20,COLORS['cyan'],center=True)
        field=pygame.Rect(card.x+40,card.y+84,card.w-80,58)
        pygame.draw.rect(s,(6,14,32),field,border_radius=10)
        pygame.draw.rect(s,COLORS['gold'],field,2,border_radius=10)
        caret='_' if pygame.time.get_ticks()//450%2==0 else ' '
        self.text(s,box['value']+caret,WIDTH//2,field.y+12,28,COLORS['white'],center=True)
        self.text(s,f"{len(box['value'])}/{box['limit']}",field.right-8,field.bottom+6,12,
                  COLORS['muted'])
        if box['error']:
            self.text(s,box['error'],WIDTH//2,card.y+168,16,COLORS['red'],center=True)
        self.text(s,'DIGITE O NOME  |  ENTER: CONFIRMAR  |  ESC: CANCELAR',WIDTH//2,card.bottom-40,
                  13,COLORS['muted'],center=True)

    def draw_editor(self, s, editor):
        """Paleta de peças à esquerda, prévia sob o mouse e instruções no painel do topo."""
        for i,key in enumerate(PIECE_KEYS):
            cx,cy=palette_slot(i)
            box=pygame.Rect(cx-36,cy-PALETTE_STEP//2+3,72,PALETTE_STEP-6)
            active = i==editor.piece_index
            pygame.draw.rect(s,(28,58,104) if active else (9,18,38),box,border_radius=9)
            pygame.draw.rect(s,COLORS['gold'] if active else (40,114,187),box,2,border_radius=9)
            self.piece(s,key,cx,cy-8,diameter=PALETTE_SIZE-8)
            self.text(s,f'{i+1} {SHORT[key]}',cx,cy+18,10,
                      COLORS['gold'] if active else COLORS['muted'],center=True)
        # Prévia: anel verde onde a peça cabe, vermelho onde não cabe.
        if editor.cursor:
            x,y=editor.cursor
            if 100<x<RIGHT and TOP<y<BOTTOM:
                radius=PIECES[editor.piece][2]
                ghost=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
                self.piece(ghost,editor.piece,x,y)
                ghost.set_alpha(150)
                s.blit(ghost,(0,0))
                ok=editor.valid_at(x,y)
                pygame.draw.circle(s,(80,230,120) if ok else COLORS['red'],(round(x),round(y)),
                                   int(radius)+6,2)
                target=editor.object_at(x,y)
                if target:
                    pygame.draw.circle(s,COLORS['red'],(target['x'],target['y']),
                                       int(PIECES[target['piece']][2])+10,1)
        # Painel do topo.
        mark='*' if editor.dirty else ''
        self.text(s,f'EDITANDO: {editor.level.name}{mark}',290,self.HUD_TOP,16,COLORS['gold'],valign='top')
        self.text(s,f'PEÇA: {PIECES[editor.piece][0]}',290,self.HUD_MID,16,COLORS['white'],valign='middle')
        self.text(s,'1-9 OU RODA DO MOUSE: TROCAR PEÇA',290,self.HUD_BOTTOM,13,COLORS['muted'],valign='bottom')
        self.text(s,f'PEÇAS NA MESA: {len(editor.objects)}',43,self.HUD_BOTTOM,14,COLORS['muted'],valign='bottom')
        self.text(s,'CLIQUE ESQ.: COLOCAR   |   CLIQUE DIR.: REMOVER   |   Z: DESFAZER   |   ESC: MENU',
                  WIDTH//2,866,12,COLORS['muted'],center=True)
        self.text(s,'A PEÇA SÓ PODE FICAR ACIMA DOS SLINGSHOTS E FORA DO CANAL DE LANÇAMENTO',
                  WIDTH//2,883,11,COLORS['muted'],center=True)

    def overlay(self,s,title,lines,accent=None):
        tint=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        tint.fill((4,9,22,193))
        s.blit(tint,(0,0))
        card=pygame.Rect(98,249,524,372)
        pygame.draw.rect(s,(13,25,51),card,border_radius=20)
        pygame.draw.rect(s,COLORS['cyan'],card,3,border_radius=20)
        self.text(s,title,360,288,42,accent or COLORS['cyan'],center=True,title=True)
        for i,line in enumerate(lines):
            self.text(s,line,360,370+i*34,20,COLORS['white'],center=True)
