"""Janela Pygame, renderização em OpenGL por padrão e compatibilidade opcional."""
import pygame
from modulos.config.constants import WIDTH, HEIGHT, TITLE, FPS, COLORS


def fit_viewport(window_w, window_h):
    """Maior área com a proporção da mesa, centralizada na janela."""
    scale = min(window_w/WIDTH, window_h/HEIGHT)
    w, h = max(1, round(WIDTH*scale)), max(1, round(HEIGHT*scale))
    return (window_w-w)//2, (window_h-h)//2, w, h


class Display:
    def __init__(self, allow_fallback=False, background=None):
        info = pygame.display.Info()
        desired_height = min(820,max(550,info.current_h-95)) if info.current_h>0 else 740
        self.size = (int(WIDTH*desired_height/HEIGHT),desired_height)
        self.clock = pygame.time.Clock()
        self.backend = 'pygame'
        self.surface = None
        self.texture = None
        self.gl = None
        # Padrão do trabalho: janela Pygame OPENGL e textura composta em OpenGL.
        if not allow_fallback:
            try:
                pygame.display.set_mode(self.size,pygame.OPENGL|pygame.DOUBLEBUF|pygame.RESIZABLE)
                from OpenGL import GL as gl
                self.gl = gl
                gl.glClearColor(*(c/255 for c in COLORS['bg']),1)
                gl.glMatrixMode(gl.GL_PROJECTION)
                gl.glLoadIdentity()
                gl.glOrtho(0,WIDTH,HEIGHT,0,-1,1)
                gl.glMatrixMode(gl.GL_MODELVIEW)
                gl.glLoadIdentity()
                gl.glEnable(gl.GL_TEXTURE_2D)
                self.texture = gl.glGenTextures(1)
                gl.glBindTexture(gl.GL_TEXTURE_2D,self.texture)
                gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MIN_FILTER,gl.GL_LINEAR)
                gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MAG_FILTER,gl.GL_LINEAR)
                gl.glTexImage2D(gl.GL_TEXTURE_2D,0,gl.GL_RGBA,WIDTH,HEIGHT,0,gl.GL_RGBA,
                                gl.GL_UNSIGNED_BYTE,None)
                self.backend='opengl'
            except Exception as exc:
                pygame.display.quit()
                raise RuntimeError(
                    'Falha ao inicializar OpenGL. Verifique PyOpenGL e o driver de vídeo; '
                    'para testar somente a interface Pygame execute: python main.py --compat-pygame'
                ) from exc
        if self.backend=='pygame':
            pygame.display.set_mode(self.size,pygame.RESIZABLE)
        pygame.display.set_caption(TITLE)
        self.surface = pygame.Surface((WIDTH,HEIGHT)).convert_alpha()
        self.last_fps = 0.0
        self.backdrop = self._create_backdrop(background)
        self.backdrop_texture = None
        if self.backend == 'opengl' and self.backdrop is not None:
            gl = self.gl
            self.backdrop_texture = gl.glGenTextures(1)
            gl.glBindTexture(gl.GL_TEXTURE_2D,self.backdrop_texture)
            gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MIN_FILTER,gl.GL_LINEAR)
            gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MAG_FILTER,gl.GL_LINEAR)
            # Repetição espelhada: as cópias vizinhas da imagem se encontram sem emenda.
            gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_WRAP_S,gl.GL_MIRRORED_REPEAT)
            gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_WRAP_T,gl.GL_MIRRORED_REPEAT)
            w,h = self.backdrop.get_size()
            gl.glTexImage2D(gl.GL_TEXTURE_2D,0,gl.GL_RGBA,w,h,0,gl.GL_RGBA,gl.GL_UNSIGNED_BYTE,
                            pygame.image.tostring(self.backdrop,'RGBA',True))
        self._tiled = None

    @staticmethod
    def _create_backdrop(background):
        """Mesmo fundo da mesa (galáxia escurecida, 720x900) para repetir nas bordas da janela."""
        if not background or not background.exists():
            return None
        tile = pygame.Surface((WIDTH,HEIGHT))
        tile.fill(COLORS['bg'])
        image = pygame.transform.smoothscale(pygame.image.load(str(background)).convert(),(WIDTH,HEIGHT))
        image.set_alpha(110)
        tile.blit(image,(0,0))
        return tile

    def to_logical(self, pos):
        """Posição do mouse na janela -> coordenadas lógicas da mesa (720x900)."""
        x,y,w,h = fit_viewport(*pygame.display.get_window_size())
        return (pos[0]-x)*WIDTH/w, (pos[1]-y)*HEIGHT/h

    def _draw_backdrop_gl(self, window_w, window_h):
        """Preenche a janela inteira com o fundo repetido, alinhado ao da mesa."""
        gl = self.gl
        x,y,w,h = fit_viewport(window_w,window_h)
        gl.glViewport(0,0,window_w,window_h)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0,window_w,window_h,0,-1,1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        # Coordenadas de textura em "cópias da mesa": 0..1 cobre exatamente a área do jogo.
        u0,u1 = -x/w, (window_w-x)/w
        v1,v0 = 1+y/h, 1-(window_h-y)/h
        gl.glBindTexture(gl.GL_TEXTURE_2D,self.backdrop_texture)
        gl.glColor3f(1,1,1)
        gl.glBegin(gl.GL_QUADS)
        gl.glTexCoord2f(u0,v1);gl.glVertex2f(0,0)
        gl.glTexCoord2f(u1,v1);gl.glVertex2f(window_w,0)
        gl.glTexCoord2f(u1,v0);gl.glVertex2f(window_w,window_h)
        gl.glTexCoord2f(u0,v0);gl.glVertex2f(0,window_h)
        gl.glEnd()
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0,WIDTH,HEIGHT,0,-1,1)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def _tiled_backdrop(self, size, rect):
        """Versão Pygame (modo compatível): fundo espelhado em mosaico, guardado em cache."""
        key = (size,rect)
        if self._tiled is None or self._tiled[0] != key:
            x,y,w,h = rect
            tile = pygame.transform.smoothscale(self.backdrop,(w,h))
            flips = {(i%2,j%2): pygame.transform.flip(tile,i%2==1,j%2==1)
                     for i in range(2) for j in range(2)}
            out = pygame.Surface(size)
            i0 = -(-x//w)  # cópias necessárias à esquerda/acima
            j0 = -(-y//h)
            for i in range(-i0, (size[0]-x)//w+1):
                for j in range(-j0, (size[1]-y)//h+1):
                    out.blit(flips[(i%2,j%2)],(x+i*w,y+j*h))
            self._tiled = (key,out)
        return self._tiled[1]

    def tick(self):
        dt = self.clock.tick(FPS)/1000.0
        self.last_fps = self.clock.get_fps()
        return min(dt,0.05)

    def present(self):
        if self.backend == 'opengl':
            gl = self.gl
            data = pygame.image.tostring(self.surface,'RGBA',True)
            gl.glBindTexture(gl.GL_TEXTURE_2D,self.texture)
            gl.glTexSubImage2D(gl.GL_TEXTURE_2D,0,0,0,WIDTH,HEIGHT,gl.GL_RGBA,
                               gl.GL_UNSIGNED_BYTE,data)
            window_w,window_h = pygame.display.get_window_size()
            gl.glViewport(0,0,window_w,window_h)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            if self.backdrop_texture is not None:
                self._draw_backdrop_gl(window_w,window_h)
                gl.glBindTexture(gl.GL_TEXTURE_2D,self.texture)
            gl.glViewport(*fit_viewport(window_w,window_h))
            gl.glLoadIdentity()
            gl.glColor3f(1,1,1)
            gl.glBegin(gl.GL_QUADS)
            gl.glTexCoord2f(0,1);gl.glVertex2f(0,0)
            gl.glTexCoord2f(1,1);gl.glVertex2f(WIDTH,0)
            gl.glTexCoord2f(1,0);gl.glVertex2f(WIDTH,HEIGHT)
            gl.glTexCoord2f(0,0);gl.glVertex2f(0,HEIGHT)
            gl.glEnd()
            pygame.display.flip()
        else:
            screen=pygame.display.get_surface()
            x,y,w,h = fit_viewport(*screen.get_size())
            if self.backdrop is not None:
                screen.blit(self._tiled_backdrop(screen.get_size(),(x,y,w,h)),(0,0))
            else:
                screen.fill(COLORS['bg'])
            screen.blit(pygame.transform.smoothscale(self.surface,(w,h)),(x,y))
            pygame.display.flip()
