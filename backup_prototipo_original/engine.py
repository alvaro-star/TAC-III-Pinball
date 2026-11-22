"""Game engine e loop fixo de física; mantém separadas entrada, update e render."""
import pygame
from pathlib import Path
from constants import FIXED_DT
from display import Display
from game import Game
from modulos.events.commands import InputManager
from modulos.audio.audio_manager import AudioManager


class GameEngine:
    def __init__(self, allow_fallback=False):
        pygame.mixer.pre_init(frequency=44100,size=-16,channels=2,buffer=512)
        pygame.init()
        self.display=Display(allow_fallback=allow_fallback)
        self.input=InputManager()
        self.audio=AudioManager(pygame,Path(__file__).resolve().parent)
        self.game=Game(self.input,self.audio,Path(__file__).resolve().parent)
        self.accumulator=0.0

    def run(self):
        try:
            while self.game.running:
                dt=self.display.tick()
                for event in pygame.event.get():
                    self.input.handle(event,self.game)
                self.accumulator=min(self.accumulator+dt,FIXED_DT*8)
                while self.accumulator>=FIXED_DT:
                    self.game.update(FIXED_DT)
                    self.accumulator-=FIXED_DT
                self.game.fps = self.display.last_fps
                self.game.render_backend = self.display.backend
                self.game.draw(self.display.surface)
                self.display.present()
        finally:
            pygame.quit()
