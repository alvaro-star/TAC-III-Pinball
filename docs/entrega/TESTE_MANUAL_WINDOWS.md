# Roteiro de validação manual — Windows

O código e os 20 testes lógicos não substituem esta validação de execução. Marque cada item após testar na máquina alvo.

- [ ] Descompactar ZIP, abrir pasta no VS Code, instalar `pygame` e `PyOpenGL` conforme o guia, selecionar `.venv`, executar `main.py` sem traceback.
- [ ] Conferir abertura com `RENDER: OPENGL` no HUD, mesa, sprites recortados do atlas, HUD e menu.
- [ ] No menu inicial, navegar com `W`/`S` e escolher **Novo jogo** com Enter; iniciar partida.
- [ ] Em **Configurações**, alterar volume, som, velocidade de queda e bolas por jogador; conferir o efeito na partida e que os valores continuam após reabrir o jogo.
- [ ] Terminar uma partida e conferir a pontuação na tela **Score** (com o nome do jogador e a fase).
- [ ] Em **Mudar de jogador**, cadastrar um nome com `N`, escolher com `Enter`, jogar e conferir que o score e o recorde aparecem nesse nome; fechar e abrir o jogo e conferir que o jogador continua cadastrado e ativo.
- [ ] Em **Editor de fases**, criar uma fase com `N`, posicionar peças com o mouse (testar o anel vermelho perto das paredes e do canal de lançamento), remover com clique direito, desfazer com `Z` e escolher **Salvar e jogar**: a partida deve usar a mesa criada.
- [ ] Na lista de fases, escolher a PADRÃO com `Enter` e conferir que **Novo jogo** volta a usar a mesa original; testar `E` na PADRÃO (abre uma cópia) e apagar uma fase com `Del` duas vezes.
- [ ] **Multiplayer LAN** com dois PCs na mesma rede: hospedar no PC A, conectar pelo IP no PC B, conferir que a partida começa sozinha, que o PC B vê a mesma bola, que no turno do J1 as teclas do PC B não mexem os flippers (e vice-versa), que `P` abre o menu local sem parar o jogo e que, ao fechar um dos jogos, o outro volta ao menu LAN com o aviso.
- [ ] Redimensionar a janela para ficar bem larga ou alta: as faixas fora da mesa devem mostrar o fundo de galáxia repetido, sem barras pretas.
- [ ] Pausar com `P`/`Esc` e testar cada opção do menu de pausa: Continuar, Reiniciar partida, Configurações (deve voltar para a pausa), Menu principal e Sair do jogo.
- [ ] Segurar o flipper levantado com a bola caindo sobre ele: a bola deve ficar presa, não ser arremessada.
- [ ] Segurar `Espaço` por intervalos diferentes e soltar; verificar a força do lançamento.
- [ ] Acionar `A` sozinho e `D` sozinho; verificar movimento independente dos flippers e retorno ao soltar.
- [ ] Observar gravidade, atrito e quique em parede, bumper e flipper.
- [ ] Acertar bumpers, conferir acréscimo no placar e bônus de combo.
- [ ] Acertar três alvos, conferir multiplicador 2× no HUD e sua expiração.
- [ ] Acertar seis alvos, conferir multiball, controle e placar.
- [ ] Perder bolas, conferir contador de 3 a 0 e mensagem Game Over.
- [ ] Repetir pela opção **Multiplayer** (2 jogadores), conferindo alternância e dois placares independentes.
- [ ] Pressionar `P`/`Esc` para pausar/retomar e `R` para reiniciar.
- [ ] Pressionar `M` e conferir trilha sonora, efeitos e muting.
- [ ] Testar em resolução comum (por exemplo 1366×768 e 1920×1080).
- [ ] Medir FPS real; verificar se mantém pelo menos 30 FPS em situação de multiball.
- [ ] Confirmar encerramento ao fechar a janela sem processo preso.

- [ ] Abrir `pinball_atlas.json` e `sprite_sheet.py` durante apresentação: demonstrar recorte em execução (`subsurface`).
- [ ] Abrir `audio_manager.py` e `assets/sound/` e demonstrar os sons lançador, bumper, bônus e game over.
- [ ] Anotar modelo do PC, resolução, FPS observado e se o áudio tocou corretamente.
