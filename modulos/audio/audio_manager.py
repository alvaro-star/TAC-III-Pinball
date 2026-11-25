"""Reprodução de efeitos WAV e trilha OGG/WAV incluídos nos assets."""
from pathlib import Path


class AudioManager:
    def __init__(self, pygame_module, root):
        self.pg = pygame_module
        self.muted = False
        self.sounds = {}
        self.available = False
        self.music_wanted = False
        self.music_volume = 0.15
        self.sfx_volume = 0.45
        try:
            if not self.pg.mixer.get_init():
                self.pg.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.available = True
            for name in ('flipper','launch','bumper','target','bonus','lose','gameover'):
                file = Path(root)/'assets'/'sound'/f'{name}.wav'
                if file.exists():
                    self.sounds[name] = self.pg.mixer.Sound(str(file))
                    self.sounds[name].set_volume(self.sfx_volume)
            music = Path(root)/'assets'/'sound'/'music.wav'
            if music.exists():
                self.pg.mixer.music.load(str(music))
                self.pg.mixer.music.set_volume(self.music_volume)
        except (Exception, OSError) as e:
            print('Áudio indisponível:',e)
            self.available = False

    def apply(self, settings):
        """Aplica volumes e som ligado/desligado vindos das configurações."""
        self.music_volume = settings.music_volume/100
        self.sfx_volume = settings.sfx_volume/100
        if self.available:
            for snd in self.sounds.values():
                snd.set_volume(self.sfx_volume)
            self.pg.mixer.music.set_volume(self.music_volume)
        self.set_muted(not settings.sound_on)

    def music_start(self):
        self.music_wanted = True
        if self.available and not self.muted:
            try: self.pg.mixer.music.play(-1)
            except Exception: pass

    def music_stop(self):
        self.music_wanted = False
        if self.available:
            try: self.pg.mixer.music.stop()
            except Exception: pass

    def sound(self, name):
        if self.available and not self.muted and name in self.sounds:
            self.sounds[name].play()

    def set_muted(self, muted):
        if muted == self.muted:
            return
        self.muted = muted
        if not self.available:
            return
        if muted:
            self.pg.mixer.music.pause()
        else:
            self.pg.mixer.music.unpause()
            # A trilha pode nunca ter começado se o som estava desligado.
            if self.music_wanted and not self.pg.mixer.music.get_busy():
                self.music_start()

    def toggle_mute(self):
        self.set_muted(not self.muted)
        return self.muted
