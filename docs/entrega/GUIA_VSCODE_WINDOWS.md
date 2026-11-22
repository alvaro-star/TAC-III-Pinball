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
.\.venv\Scripts\python.exe VERIFICAR_AMBIENTE.py
```

O arquivo `requirements.txt` declara os pacotes **pygame** e **PyOpenGL**. Se o Python 3.12 não estiver instalado, substitua `py -3.12` por `py -3.11` (se tiver 3.11) ou instale 3.12. Se já houver uma `.venv` montada com uma versão diferente/incompatível, apague somente a pasta `.venv` e recrie.

**Por que executar com `.venv\Scripts\python.exe` diretamente?** Assim você evita o erro comum de instalar numa versão de Python e tentar executar em outra. Não é necessário ativar o PowerShell nem mudar sua política de execução.

## 4. Selecionar o interpretador no VS Code

1. `Ctrl + Shift + P` → digite **Python: Select Interpreter**.
2. Escolha o interpretador correspondente a **`.venv\Scripts\python.exe`** dentro da pasta do projeto.
3. Se não aparecer, clique em **Enter interpreter path → Find...** e selecione esse arquivo.
4. Abra um novo terminal. Execute `python VERIFICAR_AMBIENTE.py` para conferir o caminho e as bibliotecas, ou use explicitamente o comando da etapa 3.

Configurações `.vscode/settings.json` e `.vscode/launch.json` já incluídas: elas facilitam o reconhecimento do ambiente e o depurador.

## 5. Iniciar, depurar e testar

**Executar no terminal:**

```powershell
.\.venv\Scripts\python.exe main.py
```

**Executar com depurador:** no VS Code, pressione **F5**, escolha **Pinball TAC III (Pygame + OpenGL)**. É necessário que o interpretador `.venv` tenha sido selecionado.

**Executar pelo Windows sem entrar no VS Code:** clique duas vezes em `INICIAR_JOGO_WINDOWS.bat`. Ele cria ambiente virtual e instala dependências, depois chama `main.py`.

**Verificações de lógica (opcional):**

```powershell
.\.venv\Scripts\python.exe -m pip install pytest
.\.venv\Scripts\python.exe -m pytest -q tests
```

## 6. Controles

- `1` / `2` no menu: número de jogadores; `Enter` inicia a partida.
- `A` ou `←`: flipper esquerdo; `D` ou `→`: flipper direito.
- **Segurar e soltar `Espaço`**: ajustar força e lançar a bola.
- `P` ou `Esc`: pausar/continuar; `R`: reiniciar; `M`: silenciar/reativar.
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
| Executou `game.py` e deu erro de import relativo | Não execute módulos isolados. Abra a **raiz** e execute **`main.py`**. |
| Sem som | Confira volume do Windows e dispositivo padrão. Os arquivos usados estão em `assets/sound/` e o gerenciador em `modulos/audio/audio_manager.py`. |

## 8. Limites dos testes disponíveis

Os testes automatizados verificam lógica e consistência estrutural. **A execução real em Windows, som, OpenGL e FPS não foram validados por esta entrega**, portanto precisam passar pelo roteiro `docs/entrega/TESTE_MANUAL_WINDOWS.md` antes da apresentação.
