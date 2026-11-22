# Roteiro de validação manual — Windows

O código e os 20 testes lógicos não substituem esta validação de execução. Marque cada item após testar na máquina alvo.

- [ ] Descompactar ZIP, abrir pasta no VS Code, instalar `pygame` e `PyOpenGL` conforme o guia, selecionar `.venv`, executar `main.py` sem traceback.
- [ ] Conferir abertura com `RENDER: OPENGL` no HUD, mesa, sprites recortados do atlas, HUD e menu.
- [ ] Selecionar 1 jogador com tecla `1`, Enter; iniciar partida.
- [ ] Segurar `Espaço` por intervalos diferentes e soltar; verificar a força do lançamento.
- [ ] Acionar `A` sozinho e `D` sozinho; verificar movimento independente dos flippers e retorno ao soltar.
- [ ] Observar gravidade, atrito e quique em parede, bumper e flipper.
- [ ] Acertar bumpers, conferir acréscimo no placar e bônus de combo.
- [ ] Acertar três alvos, conferir multiplicador 2× no HUD e sua expiração.
- [ ] Acertar seis alvos, conferir multiball, controle e placar.
- [ ] Perder bolas, conferir contador de 3 a 0 e mensagem Game Over.
- [ ] Repetir para 2 jogadores, conferindo alternância e dois placares independentes.
- [ ] Pressionar `P`/`Esc` para pausar/retomar e `R` para reiniciar.
- [ ] Pressionar `M` e conferir trilha sonora, efeitos e muting.
- [ ] Testar em resolução comum (por exemplo 1366×768 e 1920×1080).
- [ ] Medir FPS real; verificar se mantém pelo menos 30 FPS em situação de multiball.
- [ ] Confirmar encerramento ao fechar a janela sem processo preso.

- [ ] Abrir `pinball_atlas.json` e `sprite_sheet.py` durante apresentação: demonstrar recorte em execução (`subsurface`).
- [ ] Abrir `audio_manager.py` e `assets/sound/` e demonstrar os sons lançador, bumper, bônus e game over.
- [ ] Anotar modelo do PC, resolução, FPS observado e se o áudio tocou corretamente.
