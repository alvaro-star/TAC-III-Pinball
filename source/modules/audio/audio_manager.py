import pygame


class AudioManager():
    """Gerencia efeitos sonoros (SFX) e trilha sonora do jogo (RF11, RF12)."""
    def __init__(self):
        self.sfx = {}
        self.music_volume = 0.5
        self.sfx_volume = 0.7

    def load_sfx(self, name, file):
        self.sfx[name] = pygame.mixer.Sound(file)

    def play_sfx(self, name):
        if name in self.sfx:
            self.sfx[name].set_volume(self.sfx_volume)
            self.sfx[name].play()

    def play_music(self, file, loop=-1):
        pygame.mixer.music.load(file)
        pygame.mixer.music.set_volume(self.music_volume)
        pygame.mixer.music.play(loop)

    def stop_music(self):
        pygame.mixer.music.stop()


audio_manager = AudioManager()
