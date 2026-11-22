"""Reprodução de efeitos WAV e trilha OGG/WAV incluídos nos assets."""
from pathlib import Path


class AudioManager:
    def __init__(self, pygame_module, root):
        self.pg = pygame_module
        self.muted = False
        self.sounds = {}
        self.available = False
        try:
            if not self.pg.mixer.get_init():
                self.pg.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.available = True
            for name in ('flipper','launch','bumper','target','bonus','lose','gameover'):
                file = Path(root)/'assets'/'sound'/f'{name}.wav'
                if file.exists():
                    self.sounds[name] = self.pg.mixer.Sound(str(file))
                    self.sounds[name].set_volume(0.45)
            music = Path(root)/'assets'/'sound'/'music.wav'
            if music.exists():
                self.pg.mixer.music.load(str(music))
                self.pg.mixer.music.set_volume(0.14)
        except (Exception, OSError) as e:
            print('Áudio indisponível:',e)
            self.available = False

    def music_start(self):
        if self.available and not self.muted:
            try: self.pg.mixer.music.play(-1)
            except Exception: pass

    def sound(self, name):
        if self.available and not self.muted and name in self.sounds:
            self.sounds[name].play()

    def toggle_mute(self):
        self.muted = not self.muted
        if self.available:
            if self.muted:
                self.pg.mixer.music.pause()
            else:
                self.pg.mixer.music.unpause()
        return self.muted
