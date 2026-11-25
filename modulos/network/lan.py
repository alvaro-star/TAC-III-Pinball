"""Multiplayer em rede local: servidor TCP autoritativo e cliente.

O computador que hospeda roda um LANServer (com a física da partida) e também um
LANClient ligado a 127.0.0.1, como o computador que conecta. Os dois clientes só
enviam teclas; o servidor aceita apenas as do jogador da vez e devolve snapshots
com o que deve ser desenhado. Não há autenticação: use só em rede local confiável.
"""
import queue
import selectors
import socket
import threading
import time
from dataclasses import asdict
from modulos.config.constants import FIXED_DT
from modulos.network.protocol import PORT, SNAPSHOT_HZ, encode, LineDecoder

MAX_PLAYERS = 2
SOUNDS = ('flipper', 'launch', 'bumper', 'target', 'bonus', 'lose', 'gameover')


def local_ip():
    """IPv4 desta máquina na rede local (só para exibir ao anfitrião)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('10.255.255.255', 1))  # UDP sem envio: só escolhe a interface
            return s.getsockname()[0]
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return '127.0.0.1'


class _ServerInput:
    left = False
    right = False
    launch = False


class _ServerAudio:
    """Guarda os sons da simulação para os clientes tocarem."""
    muted = False

    def __init__(self):
        self.events = []

    def sound(self, name):
        if len(self.events) < 32:
            self.events.append(name)

    def drain(self):
        events, self.events = self.events, []
        return events

    def music_start(self):
        pass

    def music_stop(self):
        pass


class _Peer:
    def __init__(self, sock, player_id):
        self.sock = sock
        self.id = player_id
        self.decoder = LineDecoder()
        self.name = f'JOGADOR {player_id + 1}'
        self.greeted = False
        self.keys = {'left': False, 'right': False, 'launch': False}


class LANServer:
    def __init__(self, level, root, balls_per_player=3, gravity=100, port=PORT, host='0.0.0.0'):
        self.level = level
        self.root = root
        self.balls_per_player = balls_per_player
        self.gravity = gravity
        self.host = host
        self.port = port
        self.peers = []
        self.game = None
        self.running = False
        self.thread = None
        self.listener = None
        self.selector = selectors.DefaultSelector()

    def start(self):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.listener.bind((self.host, self.port))
            self.listener.listen(4)
        except OSError:
            self.listener.close()
            raise
        self.port = self.listener.getsockname()[1]
        self.listener.setblocking(False)
        self.selector.register(self.listener, selectors.EVENT_READ)
        self.running = True
        self.thread = threading.Thread(target=self._run, name='lan-server', daemon=True)
        self.thread.start()
        return self

    def stop(self):
        self.running = False
        if self.thread and self.thread is not threading.current_thread():
            self.thread.join(timeout=2)
        for peer in list(self.peers):
            self._close(peer)
        try:
            self.selector.unregister(self.listener)
        except (KeyError, ValueError):
            pass
        if self.listener:
            self.listener.close()

    # ---- Comunicação
    def _send(self, peer, message):
        try:
            peer.sock.sendall(encode(message))
            return True
        except OSError:
            self._drop(peer)
            return False

    def _broadcast(self, message):
        data = encode(message)
        for peer in list(self.peers):
            try:
                peer.sock.sendall(data)
            except OSError:
                self._drop(peer)

    def _close(self, peer):
        try:
            self.selector.unregister(peer.sock)
        except (KeyError, ValueError):
            pass
        peer.sock.close()
        if peer in self.peers:
            self.peers.remove(peer)

    def _drop(self, peer):
        """Um jogador saiu: na sala, atualiza a espera; na partida, encerra para o outro."""
        if peer not in self.peers:
            return
        self._close(peer)
        if self.game is None:
            self._lobby()
        else:
            self._broadcast({'type': 'disconnected', 'message': f'{peer.name} SAIU DA PARTIDA'})
            for other in list(self.peers):
                self._close(other)
            self.running = False

    def _lobby(self):
        self._broadcast({'type': 'lobby', 'connected': len(self.peers),
                         'names': [p.name for p in self.peers]})

    def _accept(self):
        try:
            sock, _ = self.listener.accept()
        except OSError:
            return
        sock.settimeout(2.0)  # envios bloqueiam no máximo 2 s
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        used = {p.id for p in self.peers}
        if self.game is not None or len(self.peers) >= MAX_PLAYERS:
            try:
                sock.sendall(encode({'type': 'error', 'message': 'SALA CHEIA'}))
            except OSError:
                pass
            sock.close()
            return
        peer = _Peer(sock, min(set(range(MAX_PLAYERS)) - used))
        self.peers.append(peer)
        self.peers.sort(key=lambda p: p.id)
        self.selector.register(sock, selectors.EVENT_READ, peer)
        self._send(peer, {'type': 'welcome', 'player_id': peer.id})
        self._lobby()

    def _receive(self, peer):
        try:
            data = peer.sock.recv(4096)
        except OSError:
            data = b''
        if not data:
            self._drop(peer)
            return
        try:
            messages = peer.decoder.feed(data)
        except ValueError:
            self._drop(peer)
            return
        for msg in messages:
            self._handle(peer, msg)

    def _handle(self, peer, msg):
        kind = msg['type']
        if kind == 'hello' and isinstance(msg.get('name'), str):
            from modulos.effects.players import clean_name
            peer.name = clean_name(msg['name']) or peer.name
            peer.greeted = True
            self._lobby()
            if (self.game is None and len(self.peers) == MAX_PLAYERS and
                    all(p.greeted for p in self.peers)):
                self._start_game()
        elif kind == 'input':
            for key in peer.keys:
                peer.keys[key] = bool(msg.get(key))
        elif kind == 'launch' and self.game and self.game.active_player == peer.id:
            self.game.launch()

    # ---- Partida
    def _start_game(self):
        from modulos.core.game import Game
        game = Game(_ServerInput(), _ServerAudio(), self.root, headless=True)
        game.settings.values['balls_per_player'] = self.balls_per_player
        game.settings.values['gravity'] = self.gravity
        game.apply_settings()
        game.level = self.level
        game.player_count = MAX_PLAYERS
        game.start_game()
        game.player_names = [p.name for p in self.peers]
        self.game = game
        self._broadcast({'type': 'start', 'names': game.player_names,
                         'level': {'name': self.level.name, 'objects': self.level.objects}})

    def _snapshot(self):
        g = self.game
        return {
            'type': 'snapshot', 'state': g.state, 'active': g.active_player,
            'players': [asdict(p) for p in g.players],
            'balls': [[round(b.position.x, 1), round(b.position.y, 1), b.ready, b.active]
                      for b in g.balls],
            'flippers': [[round(f.angle, 4), f.active] for f in g.flippers],
            'plunger': round(g.plunger.charge, 3),
            'banner': g.banner, 'banner_time': round(g.banner_time, 2),
            'flashes': [[round(e.flash, 2) for e in group]
                        for group in (g.bumpers, g.targets, g.holes)],
            'sounds': g.audio.drain(),
        }

    def _step(self):
        g = self.game
        keys = next((p.keys for p in self.peers if p.id == g.active_player), None)
        # Controles isolados por turno: só as teclas do jogador da vez movem a mesa.
        g.input.left = bool(keys and keys['left'])
        g.input.right = bool(keys and keys['right'])
        g.input.launch = bool(keys and keys['launch'])
        g.update(FIXED_DT)

    def _run(self):
        last = time.monotonic()
        accumulator = 0.0
        next_snapshot = last
        while self.running:
            for key, _ in self.selector.select(timeout=FIXED_DT / 2):
                if key.data is None:
                    self._accept()
                else:
                    self._receive(key.data)
            now = time.monotonic()
            accumulator = min(accumulator + now - last, FIXED_DT * 8)
            last = now
            if self.game is None or not self.running:
                continue
            while accumulator >= FIXED_DT:
                self._step()
                accumulator -= FIXED_DT
            if now >= next_snapshot:
                self._broadcast(self._snapshot())
                next_snapshot = now + 1 / SNAPSHOT_HZ


class LANClient:
    def __init__(self):
        self.sock = None
        self.inbox = queue.Queue()
        self.closing = False
        self.lock = threading.Lock()

    def connect(self, host, port=PORT, timeout=3.0):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.settimeout(None)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        threading.Thread(target=self._read, name='lan-client', daemon=True).start()
        return self

    def _read(self):
        decoder = LineDecoder()
        reason = 'CONEXÃO ENCERRADA PELO ANFITRIÃO'
        try:
            while True:
                data = self.sock.recv(65536)
                if not data:
                    break
                for msg in decoder.feed(data):
                    self.inbox.put(msg)
        except (OSError, ValueError):
            reason = 'CONEXÃO PERDIDA'
        if not self.closing:
            self.inbox.put({'type': 'disconnected', 'message': reason})

    def send(self, message):
        if self.closing or self.sock is None:
            return
        try:
            with self.lock:
                self.sock.sendall(encode(message))
        except OSError:
            self.inbox.put({'type': 'disconnected', 'message': 'CONEXÃO PERDIDA'})

    def poll(self):
        messages = []
        while True:
            try:
                messages.append(self.inbox.get_nowait())
            except queue.Empty:
                return messages

    def close(self):
        self.closing = True
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.sock.close()
