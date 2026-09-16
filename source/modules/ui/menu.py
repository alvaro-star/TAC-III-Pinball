from ..config.settings import Settings
from ..config.theme import Theme


class Menu():
    """Gerencia o menu principal: iniciar, opcoes e sair (gerenciamento do projeto/jogo)."""
    def __init__(self):
        self.options = ["Iniciar", "Opcoes", "Sair"]
        self.selected = 0
        self.visible = False

        # Composicao: os elementos de configuracao (audio, idioma, tema) sao
        # definidos/ajustados atraves da tela de "Opcoes" do Menu
        self.settings = Settings()
        self.theme = Theme()

    def create(self):
        self.visible = True
        self.selected = 0

    def navigate(self, direction):
        self.selected = (self.selected + direction) % len(self.options)

    def select(self):
        return self.options[self.selected]

    def update(self, dt):
        pass

    def draw(self):
        pass


menu = Menu()
