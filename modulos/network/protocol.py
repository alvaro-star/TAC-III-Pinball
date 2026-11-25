"""Protocolo da partida em LAN: mensagens JSON, uma por linha, sobre TCP.

Servidor -> cliente:
  welcome  {player_id}                      identificação do jogador (0 = J1, 1 = J2)
  lobby    {connected, names}               sala de espera
  start    {level, names}                   início da partida (peças da fase do anfitrião)
  snapshot {state, active, players, balls, flippers, plunger, banner, banner_time,
            flashes, sounds}                estado visual calculado pelo servidor
  error    {message}                        ex.: sala cheia
  disconnected {message}                    o outro jogador saiu
Cliente -> servidor:
  hello    {name}                           nome do jogador cadastrado
  input    {left, right, launch}            teclas seguradas (só valem no turno do jogador)
  launch   {}                               soltou o Espaço
"""
import json

PORT = 50505
MAX_LINE = 65536  # bytes por mensagem; linhas maiores derrubam a conexão
SNAPSHOT_HZ = 60


def encode(message):
    return (json.dumps(message, separators=(',', ':'), ensure_ascii=False) + '\n').encode('utf-8')


class LineDecoder:
    """Junta os pedaços recebidos do socket e devolve as mensagens completas."""

    def __init__(self):
        self.buffer = b''

    def feed(self, data):
        self.buffer += data
        messages = []
        while b'\n' in self.buffer:
            line, self.buffer = self.buffer.split(b'\n', 1)
            if len(line) > MAX_LINE:
                raise ValueError('mensagem grande demais')
            try:
                msg = json.loads(line.decode('utf-8'))
            except (UnicodeDecodeError, ValueError):
                continue  # linha inválida é ignorada
            if isinstance(msg, dict) and isinstance(msg.get('type'), str):
                messages.append(msg)
        if len(self.buffer) > MAX_LINE:
            raise ValueError('mensagem grande demais')
        return messages
