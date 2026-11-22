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

Alternativa: `INICIAR_JOGO_WINDOWS.bat` automatiza os passos de instalar e iniciar no Windows. Na primeira execução, é necessária internet para baixar os pacotes. **Não execute `source/modules/game.py` isoladamente**; rode `main.py` na raiz.

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
- **Código para os recortes em execução:** `source/modules/ui/sprite_sheet.py` (`SpriteSheet`) e desenho em `source/modules/ui/stage.py` (`Stage`).
- Áudio do jogo em `assets/sound/` (singular), gerenciado por `source/modules/audio/audio_manager.py`; efeitos e trilha foram sintetizados como assets adicionais para RF11 e RF12.
- Módulos essenciais: `engine.py` (loop), `display.py` (Pygame/OpenGL), `input/`, `physics/`, `entities/`, `effects/`, `ui/`, `audio/`, `game.py` (regras/turnos).

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

`docs/classes_game.png` e `docs/packages_game.png`; `python source/docs/generate.py` gera a partir dos módulos utilizando AST/Graphviz, com pyreverse como opção. O programa precisa do Graphviz `dot` para gerar PNG/SVG.

### Materiais legados

`backup_prototipo_original/`, `exemplos/` e imagens herdadas do protótipo são referências históricas que não substituem os assets ativos `assets/pinball/` e `assets/sound/`. Músicas do protótipo inicial que não eram necessárias ao pinball não integram esta entrega, evitando confusão quanto à trilha atual e direitos autorais.

#### Arquitetura de pastas de `backup_prototipo_original/`

Cópia de referência do protótipo original (engine de plataforma). Não faz parte do jogo de pinball. Contém 32 arquivos (18 `.py`), cerca de 204 KB. Esta seção descreve apenas a organização das pastas; as funções indicadas são inferidas dos nomes dos arquivos.

```text
backup_prototipo_original/
├── main.py                            # ponto de entrada
├── engine.py                          # núcleo: motor
├── game.py                            # núcleo: jogo
├── display.py                         # núcleo: tela
├── constants.py                       # constantes
├── player.py                          # cópia idêntica de modulos/entities/player.py
├── panel.py                           # cópia idêntica de modulos/ui/panel.py
├── utils.py                           # cópia idêntica de modulos/utils.py
├── requirements_original_utf16.txt    # dependências originais (UTF-16)
├── modulos/
│   ├── editor.py                      # vazio
│   ├── utils.py
│   ├── entities/                      # player.py, tiles.py
│   ├── events/                        # __init__.py (vazio), actions.py, io.py
│   └── ui/                            # background.py, level1.py, panel.py
└── diagramas/                         # 13 arquivos
    ├── classes_game.*                 # .dot, .mmd, .png, .puml, .svg
    ├── packages_game.*                # .dot, .mmd, .png, .puml, .svg
    └── grafo.*                        # .dot, .png, .svg
```

| Local | Arquivos | Papel |
|---|---:|---|
| Raiz | 9 | Entrada, núcleo, constantes, dependências e três cópias soltas de módulos |
| `modulos/` | 10 | Entidades, eventos, interface e utilitários |
| `diagramas/` | 13 | Diagramas de classes, pacotes e dependências |

Pontos de atenção da estrutura:

- `player.py`, `panel.py` e `utils.py` existem na raiz e em `modulos/` com conteúdo idêntico.
- `modulos/editor.py` e `modulos/events/__init__.py` estão vazios.
- Apenas `modulos/events/` possui `__init__.py`.
- A pasta ainda não está versionada no Git.
