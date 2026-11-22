"""Janela Pygame, renderização em OpenGL por padrão e compatibilidade opcional."""
import pygame
from .constants import WIDTH, HEIGHT, TITLE, FPS


class Display:
    def __init__(self, allow_fallback=False):
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
                pygame.display.set_mode(self.size,pygame.OPENGL|pygame.DOUBLEBUF)
                from OpenGL import GL as gl
                self.gl = gl
                gl.glViewport(0,0,*self.size)
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
            pygame.display.set_mode(self.size)
        pygame.display.set_caption(TITLE)
        self.surface = pygame.Surface((WIDTH,HEIGHT)).convert_alpha()
        self.last_fps = 0.0

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
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
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
            if screen.get_size()==(WIDTH,HEIGHT):
                screen.blit(self.surface,(0,0))
            else:
                pygame.transform.scale(self.surface,self.size,screen)
            pygame.display.flip()
