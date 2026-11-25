"""Game engine e loop fixo de física; mantém separadas entrada, update e render."""
import pygame
from pathlib import Path
from modulos.config.constants import FIXED_DT
from modulos.core.display import Display
from modulos.core.game import Game
from modulos.events.commands import InputManager
from modulos.audio.audio_manager import AudioManager

# Raiz do projeto (pasta de main.py), onde ficam assets/.
ROOT = Path(__file__).resolve().parents[2]


class GameEngine:
    def __init__(self, allow_fallback=False):
        pygame.mixer.pre_init(frequency=44100,size=-16,channels=2,buffer=512)
        pygame.init()
        self.display=Display(allow_fallback=allow_fallback,
                             background=ROOT/'assets'/'image'/'back.jpg')
        self.input=InputManager()
        self.input.to_logical=self.display.to_logical
        pygame.key.start_text_input()  # nomes de jogadores e fases
        self.audio=AudioManager(pygame,ROOT)
        self.game=Game(self.input,self.audio,ROOT,storage=ROOT/'storage')
        self.accumulator=0.0

    def run(self):
        try:
            while self.game.running:
                dt=self.display.tick()
                for event in pygame.event.get():
                    self.input.handle(event,self.game)
                self.game.poll_lan()
                if self.game.remote_mode:
                    # Partida em rede: a física roda no servidor; aqui só teclas e desenho.
                    self.game.send_input()
                    self.accumulator=0.0
                else:
                    self.accumulator=min(self.accumulator+dt,FIXED_DT*8)
                    while self.accumulator>=FIXED_DT:
                        self.game.update(FIXED_DT)
                        self.accumulator-=FIXED_DT
                self.game.fps = self.display.last_fps
                self.game.render_backend = self.display.backend
                self.game.draw(self.display.surface)
                self.display.present()
        finally:
            self.game.shutdown()
            pygame.quit()
