import pygame
import sys
#import gc
from .entities.player import Player
from .display import display
from .entities.tiles import TileMap
from .ui.stage import Stage
from .ui.panel import Panel


class Game():
    def __init__(self):
        self.running = False

    def init_assets(self):
        # Create Group Managed via LayeredDirty for automated optimization
        #self.all_sprites = pygame.sprite.LayeredDirty()
        #self.all_sprites.set_timing_threshold(10000)
        #self.all_sprites.clear(display.off_screen, bg.image)
        #platforms = pygame.sprite.Group()

        self.player = Player()
        self.panel = Panel()
        '''self.all_sprites.add(self.player)
        panel.create()
        self.all_sprites.add(panel)'''

        # load tiles
        self.tile_map = TileMap()
        self.tile_map.load_sprite_maps()

        # Estados/locais selecionaveis do pinball - cada um com seus proprios
        # obstaculos, background, etc.
        self.stages = {
            1: Stage(1),
            2: Stage(2),
        }
        self.current_stage_id = 1
        self.stage = self.stages[self.current_stage_id]
        if not self.stage.load(self.tile_map):
            self.stage.load(self.tile_map)

        '''for line in self.stage.tiles:
            for obj in line:
                if obj: self.all_sprites.add(obj)'''

    def switch_stage(self, stage_id):
        """Troca o local/estado atual do pinball (ex.: selecionado pelo Menu)."""
        self.current_stage_id = stage_id
        self.stage = self.stages[stage_id]
        if not self.stage.load(self.tile_map):
            self.stage.load(self.tile_map)


    def start(self):
        self.running = True


    def stop(self):
        self.running = False
        #gc.enable()
        pygame.quit()
        sys.exit()



game = Game() 