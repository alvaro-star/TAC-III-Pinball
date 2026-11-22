# Matriz de conformidade ao GDD original — Pinball TAC III

Esta matriz foi elaborada a partir do documento **UNI - TAC III - GDD de Pinball.docx**, preservado em `GDD_original.docx`. Os identificadores e os critérios abaixo seguem a ordem do documento; a presença de código não equivale à comprovação de desempenho em Windows.

| Identificador | Orientação do GDD | Implementação / arquivo | Verificação nesta entrega |
|---|---|---|---|
| RF1 | Iniciar, pausar e reiniciar | `game.py` (`start_game`, `pause`) e `input/commands.py` | Teste automatizado |
| RF2 | Flippers controlados pelo teclado | `entities/actuators.py`, `input/commands.py` | Teste de acionamento independente |
| RF3 | Física: gravidade, atrito, colisão e quicar | `physics/trajectory_controller.py`, `physics/collision_manager.py` | Testes de trajetória e rebote |
| RF4 | Colisão com obstáculos, paredes, bumpers e flippers | `game.py` (`collide_world`), `entities/obstacles.py` | Testes parciais de colisão; jogabilidade visual pendente |
| RF5 | Escolher força de lançamento | `Plunger` e `Ball.launch` | Testes de carga/força |
| RF6 | Identificar bola perdida | `game.py` (dreno inferior e `lose_last_ball`) | Teste de perda/contagem |
| RF7 | Contabilizar e exibir pontuação de cada jogador | `effects/score.py`, `ui/stage.py` | Teste do placar individual; interface pendente de validação |
| RF8 | Bônus por colisões/power-ups | `effects/score.py`, `game.py` | Testes de combo e multiplicador |
| RF9 | Permitir multiball (opcional) | `game.py` (`point`) | Teste de multiball |
| RF10 | Encerrar jogo após todas as vidas | `game.py` (`lose_last_ball`) | Teste de game over |
| RF11 | Efeitos sonoros de colisão, power-ups e game over | `audio/audio_manager.py`, `assets/sound/*.wav` | Arquivos gerados; reprodução pendente de validação |
| RF12 | Trilha musical de fundo | `assets/sound/music.wav`, `audio/audio_manager.py` | Arquivo gerado; reprodução pendente de validação |
| RF13 | HUD com pontos, vidas e status dos power-ups | `ui/stage.py` (`draw_hud`) | Código revisado; interface pendente de validação |
| RNF1 | Rodar em PC Windows | `main.py`, `.vscode/launch.json`, `INICIAR_JOGO_WINDOWS.bat`, `requirements.txt` | Estrutura Windows criada; execução real pendente |
| RNF2 | Mínimo 30 FPS | `constants.FPS=60`, `display.py` | **Não comprovado** sem benchmark Windows |
| RNF3 | Compatibilidade com resoluções comuns | `display.py`: janela proporcional ajustada à tela | Código revisado; teste em diferentes monitores pendente |
| RNF4 | Código modular | `modulos/{engine,display,input,physics,entities,audio,effects,ui,config}` | Organização/compilação confirmadas |
| RNF5 | Recursos de imagem/som leves | sprites PNG recortados e áudios WAV mono de baixa duração | Arquivos presentes; benchmark de memória pendente |

## Equações do GDD

- `v_t = v_(t-1) + a * Δt` — atualização da velocidade na etapa de física.
- `p_t = p_(t-1) + v_t * Δt` — atualização da posição a partir da velocidade atualizada.

O documento é claro quanto à plataforma **Windows**, à perspectiva **2D**, à estética **pixel art**, ao **uso dos flippers/lançador**, à **modularidade** e ao aproveitamento dos recursos gráficos fornecidos. A versão desta pasta foi desenvolvida em **Python/Pygame/OpenGL**, mantendo a natureza técnica do código original, sem substituir por HTML5.

## Desvios e decisões adicionais explicitadas

1. **O GDD não fixa pontuações, tempos de power-up nem número de vidas:** foram atribuídos valores para viabilizar a jogabilidade, documentados no README.
2. **Áudio de origem:** o ZIP auxiliar contém só `PINBALL1.png`, `PINBALL2.png` e `PINBALL3.png`. Foram sintetizados efeitos WAV e trilha original; não foi alegada obtenção de sons não fornecidos.
3. **Diagramas:** diagramas novos são regenerados em Graphviz a partir do código e dos relacionamentos implementados; o script utiliza pyreverse quando disponível, com geração AST/Graphviz caso ele não esteja instalado (como neste ambiente).
4. **Testes em Windows:** não realizados neste ambiente. A execução foi validada por sintaxe e testes de lógica, não por comprovação gráfica/sonora.
5. **Dependências:** requirements originais eram um `pip freeze` contendo pacotes estranhos ao pinball. O arquivo foi substituído por `pygame` e `PyOpenGL`, suficientes para a implementação principal; o texto original fica no backup do ZIP de origem recebido.

**Nota adicional sobre fidelidade às instruções do Ethan:** execução em VS Code por `.vscode/launch.json`, Pygame convencional instalado por `pip`, backend OpenGL obrigatório por padrão, sprite sheet unificada carregada dinamicamente e localização de áudio e sprites descrita em `GUIA_VSCODE_WINDOWS.md` e `MAPA_DE_MODULOS_APRESENTACAO.md`. O modo alternativo `--compat-pygame` é apenas diagnóstico, não comprova o requisito OpenGL.
