# GUIA DE INSTALAÇÃO E EXECUÇÃO NO VS CODE — TAC III PINBALL

**Esta versão é 100% Python**, não utiliza HTML nem JavaScript. O jogo cria uma janela com **Pygame** (`pygame.OPENGL | pygame.DOUBLEBUF`) e apresenta os gráficos nela com **PyOpenGL**. A mesa é montada em uma `pygame.Surface` 2D e enviada como textura ao OpenGL a cada quadro; não há shaders 3D.

## 1. Pré-requisitos

- Windows 10 ou 11 com placa gráfica/driver compatível com OpenGL legado (a implementação usa `glBegin`/`glOrtho`).
- Python **3.12** recomendado (Python 3.11 também é opção). Marque **Add python.exe to PATH** durante a instalação.
- Visual Studio Code, conectado à internet na primeira instalação de pacotes.
- Extensão do VS Code **Python** (Microsoft, identificador `ms-python.python`) — necessária/recomendada.
- Extensões **Pylance** (`ms-python.vscode-pylance`) e **Python Debugger** (`ms-python.debugpy`) são recomendadas, mas **não** substituem `pip install`.
- **Não existe extensão OpenGL obrigatória no VS Code.** A biblioteca Python se chama **PyOpenGL** e o import do código é `from OpenGL import GL`.

## 2. Abrir a pasta certa no VS Code

1. Extraia o arquivo `.zip` usando **Extrair Tudo** no Windows.
2. Abra **Visual Studio Code → File / Arquivo → Open Folder / Abrir Pasta**.
3. Selecione a pasta extraída **`Pinball_TACIII_Python`** — nela aparecem `main.py`, `requirements.txt`, `source` e `assets`.
4. Confirme o espaço de trabalho, caso o VS Code pergunte se você confia na pasta.
5. Abra **Terminal → New Terminal / Novo Terminal**. O terminal deve estar nessa pasta, não dentro de `modulos`.

## 3. Instalar Pygame e PyOpenGL NO MESMO ambiente Python

Execute linha por linha no terminal **PowerShell** do VS Code:

```powershell
py -3.12 --version
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -c "import pygame, OpenGL; print(pygame.version.ver, OpenGL.__version__)"
```

O arquivo `requirements.txt` declara os pacotes **pygame** e **PyOpenGL**. Se o Python 3.12 não estiver instalado, substitua `py -3.12` por `py -3.11` (se tiver 3.11) ou instale 3.12. Se já houver uma `.venv` montada com uma versão diferente/incompatível, apague somente a pasta `.venv` e recrie.

**Por que executar com `.venv\Scripts\python.exe` diretamente?** Assim você evita o erro comum de instalar numa versão de Python e tentar executar em outra. Não é necessário ativar o PowerShell nem mudar sua política de execução.

## 4. Selecionar o interpretador no VS Code

1. `Ctrl + Shift + P` → digite **Python: Select Interpreter**.
2. Escolha o interpretador correspondente a **`.venv\Scripts\python.exe`** dentro da pasta do projeto.
3. Se não aparecer, clique em **Enter interpreter path → Find...** e selecione esse arquivo.
4. Abra um novo terminal. Execute `python -c "import pygame, OpenGL; print(pygame.version.ver, OpenGL.__version__)"` para conferir as bibliotecas, ou use explicitamente o comando da etapa 3.

Configurações `.vscode/settings.json` e `.vscode/launch.json` já incluídas: elas facilitam o reconhecimento do ambiente e o depurador.

## 5. Iniciar, depurar e testar

**Executar no terminal:**

```powershell
.\.venv\Scripts\python.exe main.py
```

**Executar com depurador:** no VS Code, pressione **F5**, escolha **Pinball TAC III (Pygame + OpenGL)**. É necessário que o interpretador `.venv` tenha sido selecionado.

**Verificações de lógica (opcional):**

```powershell
.\.venv\Scripts\python.exe -m pip install pytest
.\.venv\Scripts\python.exe -m pytest -q tests
```

## 6. Controles

- **Menu inicial:** `W`/`S` ou setas para escolher, `Enter` para confirmar, `Esc` para voltar. Opções: Novo jogo (1 jogador), Multiplayer (2 jogadores em turnos), Editor de fases, Mudar de jogador, Score, Configurações e Sair. Novo jogo e Multiplayer usam a fase escolhida, mostrada no topo do menu.
- **Editor de fases:** lista a fase PADRÃO e as fases criadas. `Enter` escolhe a fase que será jogada, `J` joga na hora, `E` edita (na PADRÃO cria uma cópia, pois ela é somente leitura), `N` cria uma fase nova (pede o nome) e `Del`/`X` apaga (pressionar duas vezes). No editor, a paleta à esquerda lista todas as peças: `1`–`9`, roda do mouse ou clique escolhem a peça; clique esquerdo posiciona onde o mouse estiver (anel verde = cabe, vermelho = não cabe) e clique direito remove; `Z` desfaz. `Esc` abre o menu Continuar editando / Salvar e sair / Salvar e jogar / Limpar mesa / Sair sem salvar. As fases ficam em `storage/fases/*.json`, no mesmo formato da fase padrão `data/fases/padrao.json`.
- **Multiplayer LAN:** dois computadores na mesma rede local (Wi-Fi ou cabo). No PC A escolha **Hospedar partida**: a tela mostra o IPv4 dele. No PC B escolha **Conectar a um IP**, digite esse IPv4 e `Enter`. A partida começa sozinha quando os dois entram, com a fase escolhida e as bolas/velocidade de queda do anfitrião. O servidor (no PC A) calcula toda a física; cada PC só envia as teclas, e só as do jogador da vez valem. O rodapé mostra **SUA VEZ** ou de quem é a vez. `P`/`Esc` abre um menu local (Continuar / Sair da partida) sem parar o jogo. Cada PC grava no seu Score a pontuação do próprio jogador, com a fase marcada como `(LAN)`. Porta TCP **50505**: se o Windows perguntar, permita o acesso só em **redes privadas**; não abra essa porta para a Internet (não há senha).
- **Mudar de jogador:** lista os jogadores cadastrados com seus recordes. `Enter` escolhe com qual nome jogar, `N` cadastra um novo nome e `Del`/`X` apaga (duas vezes). No Multiplayer o jogador 2 é o próximo cadastrado. Os jogadores ficam em `storage/players.json` e o score registra o nome e a fase de cada pontuação.
- **Configurações:** `A`/`D` ou setas laterais ajustam som, volume da música, volume dos efeitos, velocidade de queda (gravidade), bolas por jogador e exibição do FPS. São salvas em `storage/settings.json`; o score fica em `storage/scores.json`.
- `A` ou `←`: flipper esquerdo; `D` ou `→`: flipper direito.
- **Segurar e soltar `Espaço`**: ajustar força e lançar a bola.
- `P` ou `Esc`: pausa. O **menu de pausa** é navegado como o inicial (`W`/`S` e `Enter`) e tem Continuar, Reiniciar partida, Configurações (voltam para a pausa), Menu principal e Sair do jogo; `Esc` ou `P` continuam a partida.
- `R`: reiniciar durante a partida; `M`: silenciar/reativar em qualquer tela.
- Segurar o flipper levantado prende a bola sobre ele; ela só é rebatida com força enquanto o flipper sobe.
- Game Over: `Enter` joga novamente, `Esc` volta ao menu.
- O painel inferior mostra o backend gráfico e FPS observados. O mínimo previsto no GDD é **30 FPS**, que precisa ser comprovado em Windows.

## 7. Solução de problemas

| Mensagem / sintoma | Solução |
|---|---|
| `ModuleNotFoundError: No module named 'pygame'` | Reexecute `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` e selecione a `.venv` no VS Code. |
| `ModuleNotFoundError: No module named 'OpenGL'` | O pacote que fornece esse import é **PyOpenGL**. Instale na `.venv`: `.\.venv\Scripts\python.exe -m pip install PyOpenGL`. |
| Sublinhado amarelo `Import 'pygame' could not be resolved` | `Ctrl+Shift+P` → `Python: Select Interpreter` → escolha a `.venv`; faça **Developer: Reload Window** se necessário. |
| `py` não é reconhecido | Python não foi instalado adequadamente. Reinstale Python 3.12 com o launcher habilitado, ou use `python -m venv .venv` se `python --version` funcionar. |
| PowerShell impede `Activate.ps1` | **Não precisa ativar**: use os comandos `.\.venv\Scripts\python.exe ...` exatamente como acima. |
| Falha ao criar contexto OpenGL | Atualize driver gráfico, verifique hardware e execute `python main.py --compat-pygame` **somente para diagnosticar a interface 2D**. Esse modo não substitui a exigência de OpenGL. |
| Executou `modulos/core/game.py` e deu erro de import relativo | Não execute módulos isolados. Abra a **raiz** e execute **`main.py`**. |
| Sem som | Confira volume do Windows e dispositivo padrão. Os arquivos usados estão em `assets/sound/` e o gerenciador em `modulos/audio/audio_manager.py`. |

## 8. Limites dos testes disponíveis

Os testes automatizados verificam lógica e consistência estrutural. **A execução real em Windows, som, OpenGL e FPS não foram validados por esta entrega**, portanto precisam passar pelo roteiro `docs/entrega/TESTE_MANUAL_WINDOWS.md` antes da apresentação.
