# MAPA DOS MÓDULOS, SPRITE SHEETS E ÁUDIO — PARA APRESENTAÇÃO

## Fluxo principal

`main.py` → `modulos/core/engine.py` → `modulos/core/display.py` (janela Pygame e exibição OpenGL) + `events/commands.py` (teclado) + `modulos/core/game.py` (partida) → `physics/` (física) + `entities/` (bola/obstáculos/atuadores) + `effects/` (pontos/bônus) → `ui/stage.py` (mesa/HUD/sprites) + `audio/audio_manager.py` (som).

## Onde encontrar cada parte

| O que demonstrar | Módulo / pasta | Função real |
|---|---|---|
| Inicialização | `main.py` | Ponto de entrada do jogo; abre a engine. |
| Game loop | `modulos/core/engine.py` | Lê eventos, atualiza física em passos fixos e manda desenhar. |
| Pygame e OpenGL | `modulos/core/display.py` | Cria janela `pygame.OPENGL`, contexto de textura e apresenta frames via `OpenGL.GL`. |
| Física da bola | `modulos/physics/trajectory_controller.py` | Integra gravidade e atrito, velocidade e posição a cada delta de tempo. |
| Resolução de colisões | `modulos/physics/collision_manager.py` | Vetores, contato círculo × círculo e círculo × segmento. |
| Entidade bola | `modulos/entities/ball.py` | Estado, posição, velocidade e lançamento. |
| Flippers e lançador | `modulos/entities/actuators.py` | `Actuator`, `Flipper` e `Plunger`. |
| Obstáculos | `modulos/entities/obstacles.py` | `Obstacle`, `Bumper`, `Target` e `Hole`. |
| Regras e turnos | `modulos/core/game.py` | Coordena jogadores, vidas, perdas de bola, multiball, entidades e efeitos. |
| Regras de pontos | `modulos/effects/score.py` | `PlayerScore`, combos, multiplicador e multiball. |
| Teclado e mouse | `modulos/events/commands.py` | Converte eventos `pygame.KEYDOWN/KEYUP` em comandos; nas telas de menu traduz teclas em ações (`up`, `down`, `left`, `right`, `enter`, `back`, `edit`, `new`, `play`, `delete`); no editor converte cliques e roda do mouse (via `Display.to_logical`) e na caixa de nome repassa `TEXTINPUT`. |
| Menu inicial e de pausa | `modulos/ui/menu.py` + `modulos/core/game.py` (`menu_action`) | Inicial: Novo jogo, Multiplayer, Editor de fases, Mudar de jogador, Score, Configurações e Sair. Pausa: Continuar, Reiniciar, Configurações, Menu principal e Sair. Desenho em `Stage.menu_card`. |
| Configurações | `modulos/config/settings.py` | Som, volumes, velocidade de queda, bolas por jogador e FPS; salvas em `storage/settings.json`. |
| Score | `modulos/effects/highscores.py` | 10 melhores pontuações (nome do jogador e fase), gravadas no Game Over em `storage/scores.json`. |
| Multiplayer LAN | `modulos/network/protocol.py`, `modulos/network/lan.py` + `Game.host_lan/join_lan/poll_lan/apply_snapshot` | Cliente-servidor TCP na porta 50505, mensagens JSON por linha. O anfitrião roda `LANServer` (um `Game` sem desenho, `headless=True`) e os dois PCs rodam `LANClient`; só as teclas do jogador da vez são aplicadas e o servidor envia snapshots a 60 Hz. Arquitetura baseada na proposta do Trabalho II (PR #3). |
| Jogadores | `modulos/effects/players.py` | Jogadores cadastrados e jogador ativo em `storage/players.json`. |
| Fases | `modulos/core/levels.py` | Catálogo de peças (`PIECES`), formato JSON da fase, fase padrão `data/fases/padrao.json` (recriada por `create_default_level` se faltar), regras de posicionamento e `LevelStore` para `storage/fases/`. |
| Editor de fases | `modulos/core/level_editor.py` + `Stage.draw_editor` | Peça escolhida, paleta, colocar/remover/desfazer; desenho da paleta e da prévia sob o mouse. |
| Fundo da janela | `modulos/core/display.py` | Repete o fundo de galáxia (textura `GL_MIRRORED_REPEAT`) nas faixas fora da mesa quando a janela não tem a proporção 720×900. |
| Sprite sheet (arquivo) | `assets/pinball/pinball_atlas.png` | **Atlas usado em execução**, produzido com recortes das três pranchas recebidas. |
| Coordenadas dos sprites | `assets/pinball/pinball_atlas.json` | Retângulos x/y/largura/altura dos itens do atlas. |
| Sprite sheet (código) | `modulos/ui/sprite_sheet.py` | `SpriteSheet.get()` faz `subsurface(rect)` no atlas, sem exigir Pillow em runtime. |
| Artes originais | `assets/pinball/PINBALL1.png`, `PINBALL2.png`, `PINBALL3.png` | **Três pranchas intactas enviadas no anexo**, para origem e edição. |
| Sprites individuais | `assets/pinball/sprites/*.png` | Recortes RGBA individuais mantidos para edição do atlas; o jogo lê o atlas. |
| Visual e HUD | `modulos/ui/stage.py` | `Stage` busca os sprites, desenha a mesa, os flippers animados e o placar. |
| Efeitos de som | `assets/sound/{flipper,launch,bumper,target,bonus,lose,gameover}.wav` | Efeitos WAV sintetizados para demonstrar RF11. |
| Trilha | `assets/sound/music.wav` | Trilha WAV sintetizada para RF12. |
| Áudio (código) | `modulos/audio/audio_manager.py` | Carrega, reproduz e silencia sons via `pygame.mixer`. |
| Aparência/idioma | `modulos/config/theme.py`, `locale/` | Parâmetros e referências de configuração. |
| Diagramas UML | `docs/classes_game.png`, `docs/packages_game.png` | Relações de classes e módulos. |
| GDD original | `docs/entrega/GDD_original.docx` | Documento entregue, preservado sem alteração. |
| GDD complementado | `docs/entrega/GDD_COM_ANEXO_TECNICO.docx` | Cópia com mapa e guia anexados para apresentação. |
| Testes | `tests/` | Testes de regras, física e presença de assets. |

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
3. `modulos/core/game.py` dispara sons ao lançar, colidir, perder a bola e acionar bônus.
4. `modulos/events/commands.py` trata `M` para mutar.
5. **Origem:** sons não estavam definidos/especificados no GDD; arquivos sintetizados foram acrescentados para cumprir RF11 e RF12, não extraídos das pranchas PNG.

## O que dizer na apresentação (até 1 minuto)

> Nosso projeto é desenvolvido em Python. O Pygame gerencia a janela, teclado e áudio, enquanto o OpenGL apresenta a interface gráfica. A lógica do jogo está separada em módulos de física, entidades, pontuação, entrada e áudio. As três sprite sheets fornecidas foram preservadas e seus recortes foram agrupados em um atlas com coordenadas JSON; um módulo próprio carrega o atlas e entrega cada imagem para a interface. O som fica em `assets/sound`, comandado pelo `audio_manager.py`. Os testes unitários validam a lógica, e a validação de FPS e compatibilidade gráfica deve ser feita na máquina Windows de apresentação.

## Critérios de conformidade

A matriz completa RF1–RF13 e RNF1–RNF5 está em `MATRIZ_DE_CONFORMIDADE.md`. Não confundir código implementado com comprovação prática de desempenho; o requisito de **mínimo 30 FPS** só pode ser confirmado após medição real no Windows.

**Origem demonstrável por sprite:** no arquivo `pinball_atlas.json`, o campo `origens` relaciona cada elemento à prancha `PINBALL1.png`, `PINBALL2.png` ou `PINBALL3.png`. O ícone `icon_2x` vem da primeira prancha; `bumper_red` e `ball`, da terceira; a maior parte dos demais elementos, da segunda.
