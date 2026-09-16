from ..constants import COLOR_TEXT, COLOR_BG


class Theme():
    """Tema visual do jogo (cores, fontes) selecionavel/ajustavel atraves do Menu."""
    def __init__(self):
        self.color_text = COLOR_TEXT
        self.color_bg = COLOR_BG
        self.font_name = None
        self.font_size = 24
