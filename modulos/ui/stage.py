"""Mesa, cenografia pixel art e sprites recortados das pranchas fornecidas."""
import math
import random
from pathlib import Path
import pygame
from .sprite_sheet import SpriteSheet
from constants import (WIDTH, HEIGHT, LEFT, RIGHT, TOP, BOTTOM, COLORS,
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
        fontfile = self.root/'assets'/'fonts'/'FreeSans.ttf'
        self.font_name = str(fontfile) if fontfile.exists() else None
        titlefont = self.root/'assets'/'fonts'/'Call of Ops Duty II.otf'
        self.title_fontfile = str(titlefont) if titlefont.exists() else self.font_name
        self.font_cache = {}
        self.base = self._create_background()

    def font(self, size, title=False):
        key = (size,title)
        if key not in self.font_cache:
            self.font_cache[key] = pygame.font.Font(self.title_fontfile if title else self.font_name, size)
        return self.font_cache[key]

    def text(self, surface, message, x, y, size=19, color=None, center=False, title=False):
        fg = COLORS['white'] if color is None else color
        img = self.font(size,title).render(str(message),True,fg)
        box = img.get_rect()
        if center:
            box.midtop = (int(x),int(y))
        else:
            box.topleft = (int(x),int(y))
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
        pygame.draw.circle(s,(27,63,91),(360,447),46)
        pygame.draw.circle(s,(112,48,140),(360,447),40,width=3)
        pygame.draw.circle(s,(23,11,42),(360,447),29)
        for i in range(10):
            phi = 2*math.pi*i/10
            x=360+35*math.cos(phi);y=447+35*math.sin(phi)
            pygame.draw.circle(s,(246,89,165),(int(x),int(y)),3)
        rng = random.Random(83)
        for _ in range(70):
            x=rng.randint(15,WIDTH-15);y=rng.randint(112,HEIGHT-18)
            inside = LEFT-20 < x < RIGHT+20 and y < BOTTOM+22 and (
                y >= ARCH_CENTER_Y or math.hypot(x-ARCH_CENTER_X,y-ARCH_CENTER_Y) < ARCH_RADIUS+20)
            if not inside:
                pygame.draw.circle(s,(130,177,217),(x,y),rng.choice([1,1,1,2]))
        return s

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
        for i, target in enumerate(game.targets):
            self.sprite(surface,('target25','target10','target50')[i],target.x,target.y,
                        int(target.radius*2+7),target.flash)
        for i, bumper in enumerate(game.bumpers):
            self.sprite(surface,('bumper_blue','bumper_gold','bumper_pink','bumper_red','bumper_blue')[i],
                        bumper.x,bumper.y,int(bumper.radius*2+8),bumper.flash)
        if game.hole.flash:
            pygame.draw.circle(surface,COLORS['pink'],(int(game.hole.x),int(game.hole.y)),45,4)
        self.text(surface,'BÔNUS',360,433,13,COLORS['pink'],center=True)
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

    def draw_hud(self,s,game):
        pygame.draw.rect(s,(7,12,29),(20,8,WIDTH-40,103),border_radius=13)
        pygame.draw.rect(s,(40,114,187),(20,8,WIDTH-40,103),2,border_radius=13)
        self.text(s,'PINBALL',43,10,31,COLORS['cyan'],title=True)
        self.text(s,'TAC III  /  ARCADE',43,52,14,COLORS['muted'])
        for i,score in enumerate(game.players):
            x = 322 if i == 0 else 506
            fg = COLORS['gold'] if game.active_player == i else COLORS['muted']
            self.text(s,f'JOGADOR {i+1}',x,16,14,fg)
            self.text(s,f'{score.score:07d}',x,35,28,COLORS['white'])
            self.text(s,f'BOLAS: {score.remaining}',x,76,15,fg)
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
        backend = getattr(game, 'render_backend', 'a verificar').upper()
        fps = getattr(game, 'fps', 0.0)
        self.text(s, f'RENDER: {backend} / FPS: {fps:.0f}', 20,884,11,COLORS['muted'])

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
