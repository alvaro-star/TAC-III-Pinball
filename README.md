# PINBALL TAC III — PROJETO PYTHON / PYGAME / OPENGL

**Entregar e executar no Visual Studio Code, com Python, Pygame e PyOpenGL.** O arquivo principal é `main.py`; o jogo NÃO é HTML/JavaScript.

## COMEÇAR (Windows + VS Code)

1. Extraia o ZIP completo e abra a **pasta `Pinball_TACIII_Python`** no VS Code (`Arquivo → Abrir Pasta`).
2. Instale o Python 3.12 e a extensão **Python** no VS Code. Pylance e Python Debugger são opcionais e recomendadas.
3. No terminal PowerShell do VS Code, execute:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe VERIFICAR_AMBIENTE.py
.\.venv\Scripts\python.exe main.py
```

4. No VS Code, `Ctrl+Shift+P → Python: Select Interpreter → .venv\Scripts\python.exe`. Para depurar, pressione **F5** e escolha **Pinball TAC III (Pygame + OpenGL)**.

Alternativa: `INICIAR_JOGO_WINDOWS.bat` automatiza os passos de instalar e iniciar no Windows. Na primeira execução, é necessária internet para baixar os pacotes. **Não execute `game.py` isoladamente**; rode `main.py` na raiz.

**Documentação detalhada:** `docs/entrega/GUIA_VSCODE_WINDOWS.md` — instalação, problemas frequentes, seleção de ambiente. `docs/entrega/MAPA_DE_MODULOS_APRESENTACAO.md` — localização de sprites, áudio, física e regras; roteiro para explicar ao professor. `docs/entrega/GDD_COM_ANEXO_TECNICO.docx` — GDD com anexo explicativo. GDD original está preservado em `docs/entrega/GDD_original.docx`.

## Comandos

| Tecla | Ação |
|---|---|
| `1` / `2` no menu | Número de jogadores |
| `Enter` | Iniciar / nova partida |
| `A` / `←` | Flipper esquerdo |
| `D` / `→` | Flipper direito |
| `Espaço` (segurar/soltar) | Carga e lançamento |
| `P` / `Esc` | Pausa / retorno |
| `R` | Reiniciar |
| `M` | Mutar / voltar áudio |

## Origem e utilização dos arquivos visuais/sonoros

- Três pranchas originais recebidas: `assets/pinball/PINBALL1.png`, `PINBALL2.png`, `PINBALL3.png`.
- **Sprite sheet efetivamente carregada:** `assets/pinball/pinball_atlas.png` + coordenadas em `pinball_atlas.json`.
- **Código para os recortes em execução:** `modulos/ui/sprite_sheet.py` (`SpriteSheet`) e desenho em `modulos/ui/stage.py` (`Stage`).
- Áudio do jogo em `assets/sound/` (singular), gerenciado por `modulos/audio/audio_manager.py`; efeitos e trilha foram sintetizados como assets adicionais para RF11 e RF12.
- Módulos essenciais: `engine.py` (loop), `display.py` (Pygame/OpenGL), `modulos/events/`, `modulos/physics/`, `modulos/entities/`, `modulos/effects/`, `modulos/ui/`, `modulos/audio/`, `game.py` (regras/turnos).

## GDD: regras e limitações

A matriz de requisitos RF1–RF13 e RNF1–RNF5 está em `docs/entrega/MATRIZ_DE_CONFORMIDADE.md`. Parâmetros de jogabilidade (pontos, duração de bônus, 3 bolas/pessoa) foram definidos na implementação porque o GDD não determina seus valores.

**A renderização usa OpenGL por padrão.** A opção `python main.py --compat-pygame` existe exclusivamente como **diagnóstico da interface** se houver problema de OpenGL, não como substituição do requisito de utilizar OpenGL.

Os testes automatizados do pacote validam lógica e assets; **som, contexto gráfico e FPS real em Windows ainda precisam ser testados no PC**. Não alegamos comprovação de 30 FPS sem medição. Checklist: `docs/entrega/TESTE_MANUAL_WINDOWS.md`.

### Testes automatizados

```powershell
.\.venv\Scripts\python.exe -m pip install pytest
.\.venv\Scripts\python.exe -m pytest -q tests
```

### Diagramas

`docs/classes_game.png` e `docs/packages_game.png`; `python docs/generate.py` gera a partir dos módulos utilizando AST/Graphviz, com pyreverse como opção. O programa precisa do Graphviz `dot` para gerar PNG/SVG.

### Arquitetura de pastas

O pinball segue a arquitetura do protótipo: arquivos de núcleo na raiz do projeto e os demais módulos em `modulos/`.

```text
Pinball_TACIII_Python/
├── main.py                 # ponto de entrada
├── engine.py               # loop principal
├── game.py                 # regras, estados e turnos
├── display.py              # Pygame + OpenGL
├── constants.py            # constantes
├── modulos/
│   ├── audio/              # áudio
│   ├── config/             # opções e tema
│   ├── effects/            # pontuação e bônus
│   ├── entities/           # bola, flippers, lançador e obstáculos
│   ├── events/             # entrada de teclado (commands.py)
│   ├── physics/            # colisões e trajetória
│   └── ui/                 # mesa, HUD e sprite sheet
├── assets/                 # sprites, sons e imagens
├── tests/                  # testes automatizados
├── docs/                   # documentação e diagramas do pinball
├── diagramas/              # diagramas do protótipo original
├── data/, locale/, logs/   # material herdado, sem uso no pinball
└── exemplos/               # exemplos de aula
```

### Materiais legados

Não fazem parte do pinball: `exemplos/`, `diagramas/`, `data/`, `player.py`, `panel.py`, `utils.py`, `requirements_original_utf16.txt`, `modulos/editor.py`, `modulos/utils.py`, `modulos/entities/player.py`, `modulos/entities/tiles.py`, `modulos/events/actions.py`, `modulos/events/io.py`, `modulos/ui/background.py`, `modulos/ui/level1.py` e `modulos/ui/panel.py`. As versões originais de `main.py`, `engine.py`, `game.py`, `display.py` e `constants.py` do protótipo continuam no histórico do Git, no commit "Registrar protótipo original antes da migração".
