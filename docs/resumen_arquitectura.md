# Resumen de archivos y módulos del pinball

Resumen generado a partir de los archivos y las importaciones reales del proyecto. Tiene **288 archivos**, y el pinball funciona con **17 módulos Python**, de los cuales 15 están conectados al juego.

## Módulos del pinball y sus dependencias

```mermaid
flowchart TD
    MAIN["main.py<br/>Punto de entrada"] --> ENGINE

    subgraph NUCLEO["Núcleo (raíz)"]
        ENGINE["engine.py<br/>GameEngine: bucle principal"]
        GAME["game.py<br/>Game: reglas, estados y turnos"]
        DISPLAY["display.py<br/>Display: Pygame + OpenGL"]
        CONST["constants.py<br/>Constantes globales"]
    end

    subgraph MODULOS["modulos/"]
        subgraph EVENTS["events/"]
            COMMANDS["commands.py<br/>InputManager"]
        end
        subgraph AUDIO["audio/"]
            AUDIOM["audio_manager.py<br/>AudioManager"]
        end
        subgraph UI["ui/"]
            STAGE["stage.py<br/>Stage: mesa y HUD"]
            SPRITE["sprite_sheet.py<br/>SpriteSheet"]
        end
        subgraph EFFECTS["effects/"]
            SCORE["score.py<br/>PlayerScore"]
        end
        subgraph ENTITIES["entities/"]
            BALL["ball.py<br/>Ball"]
            ACT["actuators.py<br/>Actuator, Flipper, Plunger"]
            OBS["obstacles.py<br/>Obstacle, Bumper, Target, Hole"]
        end
        subgraph PHYSICS["physics/"]
            TRAJ["trajectory_controller.py<br/>TrajectoryController"]
            COLL["collision_manager.py<br/>Vector, CollisionManager"]
        end
        subgraph CONFIG["config/ (sin uso)"]
            SETTINGS["settings.py"]
            THEME["theme.py"]
        end
    end

    ENGINE --> DISPLAY
    ENGINE --> GAME
    ENGINE --> COMMANDS
    ENGINE --> AUDIOM
    GAME --> STAGE
    GAME --> SCORE
    GAME --> BALL
    GAME --> ACT
    GAME --> OBS
    GAME --> TRAJ
    GAME --> COLL
    STAGE --> SPRITE
    BALL --> COLL
    ACT --> COLL
    OBS --> COLL
    TRAJ --> COLL
    THEME -.-> CONST
```

`constants.py` también lo usan `engine`, `game`, `display`, `stage`, `score`, `ball` y `trajectory_controller`. Esas flechas se omiten para que el diagrama se pueda leer.

## Organización de los archivos

```mermaid
flowchart LR
    ROOT["Proyecto<br/>288 archivos"]

    ROOT --> CODE["Código del pinball"]
    CODE --> C1["Núcleo: 5 archivos"]
    CODE --> C2["modulos/: 12 módulos activos"]
    CODE --> C3["tests/: 2 archivos, 28 tests"]

    ROOT --> RES["Recursos"]
    RES --> R1["assets/pinball: 16<br/>Sprites y atlas"]
    RES --> R2["assets/sound: 8<br/>Efectos y música"]
    RES --> R3["assets/image: 61<br/>Heredado, solo se usa back.jpg"]

    ROOT --> DOC["Documentación"]
    DOC --> D1["docs/: 20<br/>Incluye 6 de entrega"]
    DOC --> D2["README.md y ENTREGA_LEIA_PRIMEIRO.txt"]

    ROOT --> SETUP["Ejecución y entorno"]
    SETUP --> S1["requirements.txt"]
    SETUP --> S2["VERIFICAR_AMBIENTE.py"]
    SETUP --> S3["INICIAR_JOGO_WINDOWS.bat"]
    SETUP --> S4[".vscode/ y conftest.py"]

    ROOT --> OLD["Legado, fuera del pinball"]
    OLD --> O1["exemplos/: 116"]
    OLD --> O2["diagramas/: 13"]
    OLD --> O3["data/: 3, locale/: 1, logs/: 1"]
    OLD --> O4["12 módulos del prototipo<br/>player, panel, utils, tiles, level1..."]
```

## Puntos a limpiar

- **`modulos/config/` no está conectado:** ningún módulo activo importa `settings.py` ni `theme.py`, así que cambiar esas opciones no afecta al juego.
- **El código legado ya no funciona:** varios de esos módulos importan rutas como `modulos.constants` y `modulos.game`, que ya no existen. El pinball no los usa, así que hoy no causan fallos.
