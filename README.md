# Pinball TAC III

Jogo de pinball 2D em estilo arcade, desenvolvido em Python com Pygame e PyOpenGL para a disciplina Tópicos Avançados em Computação III. A mesa tem teto em semicírculo, dois flippers, lançador com carga, bumpers, alvos, buraco de bônus e slingshots. Partidas para 1 ou 2 jogadores, com 3 bolas por pessoa (de 1 a 5 nas configurações) e turnos alternados, pontuação com combos, multiplicador 2X temporário e multiball. Um menu inicial dá acesso a novo jogo, multiplayer local, multiplayer LAN (dois computadores na mesma rede, com servidor TCP autoritativo e turnos com controles isolados), editor de fases, troca de jogador, tabela de score e configurações de som, volume, velocidade de queda e número de bolas. No editor de fases o jogador posiciona com o mouse bumpers, alvos e buracos de bônus para montar novas mesas, salvas em JSON no mesmo formato da fase padrão, e escolhe qual fase será jogada. Jogadores cadastrados pelo nome, recordes, fases e configurações ficam salvos entre as sessões. A física roda em passo fixo de 120 Hz e a imagem é composta em OpenGL, com sprites recortados de um atlas, efeitos sonoros e trilha musical.

## Como executar

Requisitos: Python 3.11 ou 3.12 e uma placa de vídeo com suporte a OpenGL.

**Windows (PowerShell, na pasta do projeto):**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

**Linux / macOS:**

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python main.py
```

No VS Code, abra a pasta do projeto e pressione `F5` (configuração "Pinball TAC III (Pygame + OpenGL)").

Se o OpenGL não iniciar, `python main.py --compat-pygame` abre o jogo só com Pygame, para diagnóstico.

**Controles:** `A`/`D` ou setas movem os flippers, segurar e soltar `Espaço` lança a bola, `P`/`Esc` pausa e `M` liga ou desliga o som. Nos menus, use `W`/`S` ou as setas e `Enter`.

Guia completo (editor de fases, multiplayer LAN e configurações): [`docs/entrega/GUIA_VSCODE_WINDOWS.md`](docs/entrega/GUIA_VSCODE_WINDOWS.md).
