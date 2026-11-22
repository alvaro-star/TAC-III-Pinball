"""Ponto de entrada: rodar a partir da pasta raiz no VS Code: python main.py."""
import argparse
from source.modules.engine import GameEngine


def main():
    parser = argparse.ArgumentParser(description='Pinball TAC III em Python/Pygame/OpenGL')
    parser.add_argument('--compat-pygame', action='store_true',
                        help='Modo de diagnóstico Pygame 2D, sem usar OpenGL')
    args = parser.parse_args()
    GameEngine(allow_fallback=args.compat_pygame).run()


if __name__ == '__main__':
    main()
