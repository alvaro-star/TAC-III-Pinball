"""Constantes do pinball - coordenadas lógicas independentes da resolução."""
WIDTH = 720
HEIGHT = 900
TITLE = "TAC III - Pinball Arcade"
FPS = 60  # RNF2: a execução visa 60 fps; mínimo exigido 30
FIXED_DT = 1.0 / 120.0  # física com integração estável a 120 Hz
GRAVITY = 970.0  # px/s², eixo y positivo para baixo
DRAG = 0.085  # resistência ao movimento por segundo
MAX_SPEED = 1700.0
BALL_RADIUS = 11.0
LEFT = 105.0
RIGHT = 615.0
TOP = 122.0
BOTTOM = 849.0
# Teto em semicírculo: tangente às paredes laterais da mesa.
ARCH_RADIUS = (RIGHT - LEFT) / 2
ARCH_CENTER_X = (LEFT + RIGHT) / 2
ARCH_CENTER_Y = TOP + ARCH_RADIUS
LANE_LEFT = 568.0
LAUNCH_X = 590.0
LAUNCH_Y = 783.0
BALLS_PER_PLAYER = 3
START_BONUS_DURATION = 12.0
COLORS = {
    'bg': (6, 11, 24), 'panel': (13, 24, 46), 'frame': (45, 137, 230),
    'white': (236, 248, 255), 'muted': (137, 172, 210), 'gold': (255, 196, 54),
    'cyan': (51, 222, 249), 'pink': (246, 89, 165), 'red': (250, 74, 88),
}
