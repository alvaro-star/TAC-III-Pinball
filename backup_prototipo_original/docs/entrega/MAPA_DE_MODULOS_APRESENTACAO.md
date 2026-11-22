# MAPA DOS MÓDULOS, SPRITE SHEETS E ÁUDIO — PARA APRESENTAÇÃO

## Fluxo principal

`main.py` → `engine.py` → `display.py` (janela Pygame e exibição OpenGL) + `input/commands.py` (teclado) + `game.py` (partida) → `physics/` (física) + `entities/` (bola/obstáculos/atuadores) + `effects/` (pontos/bônus) → `ui/stage.py` (mesa/HUD/sprites) + `audio/audio_manager.py` (som).

## Onde encontrar cada parte

| O que demonstrar | Módulo / pasta | Função real |
|---|---|---|
| Inicialização | `main.py` | Ponto de entrada do jogo; abre a engine. |
| Game loop | `engine.py` | Lê eventos, atualiza física em passos fixos e manda desenhar. |
| Pygame e OpenGL | `display.py` | Cria janela `pygame.OPENGL`, contexto de textura e apresenta frames via `OpenGL.GL`. |
| Física da bola | `modulos/physics/trajectory_controller.py` | Integra gravidade e atrito, velocidade e posição a cada delta de tempo. |
| Resolução de colisões | `modulos/physics/collision_manager.py` | Vetores, contato círculo × círculo e círculo × segmento. |
| Entidade bola | `modulos/entities/ball.py` | Estado, posição, velocidade e lançamento. |
| Flippers e lançador | `modulos/entities/actuators.py` | `Actuator`, `Flipper` e `Plunger`. |
| Obstáculos | `modulos/entities/obstacles.py` | `Obstacle`, `Bumper`, `Target` e `Hole`. |
| Regras e turnos | `game.py` | Coordena jogadores, vidas, perdas de bola, multiball, entidades e efeitos. |
| Regras de pontos | `modulos/effects/score.py` | `PlayerScore`, combos, multiplicador e multiball. |
| Teclado | `modulos/events/commands.py` | Converte eventos `pygame.KEYDOWN/KEYUP` em comandos. |
| Sprite sheet (arquivo) | `assets/pinball/pinball_atlas.png` | **Atlas usado em execução**, produzido com recortes das três pranchas recebidas. |
| Coordenadas dos sprites | `assets/pinball/pinball_atlas.json` | Retângulos x/y/largura/altura dos itens do atlas. |
| Sprite sheet (código) | `modulos/ui/sprite_sheet.py` | `SpriteSheet.get()` faz `subsurface(rect)` no atlas, sem exigir Pillow em runtime. |
| Artes originais | `assets/pinball/PINBALL1.png`, `PINBALL2.png`, `PINBALL3.png` | **Três pranchas intactas enviadas no anexo**, para origem e edição. |
| Sprites individuais | `assets/pinball/sprites/*.png` | Recortes RGBA individuais mantidos para edição do atlas; o jogo lê o atlas. |
| Visual e HUD | `modulos/ui/stage.py` | `Stage` busca os sprites, desenha a mesa, os flippers animados e o placar. |
| Efeitos de som | `assets/sound/{flipper,launch,bumper,target,bonus,lose,gameover}.wav` | Efeitos WAV sintetizados para demonstrar RF11. |
| Trilha | `assets/sound/music.wav` | Trilha WAV sintetizada para RF12. |
| Áudio (código) | `modulos/audio/audio_manager.py` | Carrega, reproduz e silencia sons via `pygame.mixer`. |
| Aparência/idioma | `modulos/config/`, `locale/` | Parâmetros e referências de configuração. |
| Diagramas UML | `docs/classes_game.png`, `docs/packages_game.png` | Relações de classes e módulos. |
| GDD original | `docs/entrega/GDD_original.docx` | Documento entregue, preservado sem alteração. |
| GDD complementado | `docs/entrega/GDD_COM_ANEXO_TECNICO.docx` | Cópia com mapa e guia anexados para apresentação. |
| Testes | `tests/` | Testes de regras, física e presença de assets. |
| Verificador | `VERIFICAR_AMBIENTE.py` | Mostra qual Python está rodando e verifica `pygame` e `OpenGL`. |

**IMPORTANTE:** `assets/sounds/` (plural), caso presente no material legado, contém efeitos do protótipo antigo e **não é a pasta usada pelo jogo atual**. O diretório operacional é `assets/sound/` (singular). Não apresentar músicas herdadas do protótipo como trilha original do pinball.

## Cadeia de sprite sheets — exemplo para mostrar em código

1. Abrir `assets/pinball/PINBALL2.png` para mostrar uma prancha fornecida.
2. Abrir `assets/pinball/pinball_atlas.png` para mostrar o atlas unificado.
3. Abrir `assets/pinball/pinball_atlas.json`: cada nome, como `ball`, possui `x`, `y`, `w`, `h`.
4. Abrir `modulos/ui/sprite_sheet.py`: o método `get(name)` recorta `pygame.Surface.subsurface()`.
5. Abrir `modulos/ui/stage.py`: `Stage` usa os recortes para desenhar bumpers, alvos e bola.
6. Diferenciar dos **flippers**: o movimento é geométrico e animado em código, inspirado na estética das pranchas; essa escolha simplifica a animação e sincroniza o desenho com o contato físico.

## Cadeia de áudio — exemplo para mostrar

1. `assets/sound/` tem arquivos `.wav` individuais e `music.wav`.
2. `modulos/audio/audio_manager.py` utiliza `pygame.mixer.Sound` e `pygame.mixer.music`.
3. `game.py` dispara sons ao lançar, colidir, perder a bola e acionar bônus.
4. `modulos/events/commands.py` trata `M` para mutar.
5. **Origem:** sons não estavam definidos/especificados no GDD; arquivos sintetizados foram acrescentados para cumprir RF11 e RF12, não extraídos das pranchas PNG.

## O que dizer na apresentação (até 1 minuto)

> Nosso projeto é desenvolvido em Python. O Pygame gerencia a janela, teclado e áudio, enquanto o OpenGL apresenta a interface gráfica. A lógica do jogo está separada em módulos de física, entidades, pontuação, entrada e áudio. As três sprite sheets fornecidas foram preservadas e seus recortes foram agrupados em um atlas com coordenadas JSON; um módulo próprio carrega o atlas e entrega cada imagem para a interface. O som fica em `assets/sound`, comandado pelo `audio_manager.py`. Os testes unitários validam a lógica, e a validação de FPS e compatibilidade gráfica deve ser feita na máquina Windows de apresentação.

## Critérios de conformidade

A matriz completa RF1–RF13 e RNF1–RNF5 está em `MATRIZ_DE_CONFORMIDADE.md`. Não confundir código implementado com comprovação prática de desempenho; o requisito de **mínimo 30 FPS** só pode ser confirmado após medição real no Windows.

**Origem demonstrável por sprite:** no arquivo `pinball_atlas.json`, o campo `origens` relaciona cada elemento à prancha `PINBALL1.png`, `PINBALL2.png` ou `PINBALL3.png`. O ícone `icon_2x` vem da primeira prancha; `bumper_red` e `ball`, da terceira; a maior parte dos demais elementos, da segunda.
