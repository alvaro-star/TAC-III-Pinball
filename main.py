import os

# Wayland (COSMIC) trava no set_mode com OPENGL - usar XWayland por padrão
os.environ.setdefault("SDL_VIDEODRIVER", "x11")

from source.modules.engine import engine

if __name__ == "__main__":
    engine.run()