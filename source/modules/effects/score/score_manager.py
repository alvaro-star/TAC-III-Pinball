class ScoreManager():
    """Contabiliza a pontuacao, com suporte a multiplos jogadores (RF7)."""
    def __init__(self):
        self.scores = {}
        self.current_player = 1

    def add_player(self, player_id):
        self.scores[player_id] = 0

    def add_points(self, points, player_id=None):
        player_id = player_id or self.current_player
        self.scores[player_id] = self.scores.get(player_id, 0) + points

    def get_score(self, player_id=None):
        player_id = player_id or self.current_player
        return self.scores.get(player_id, 0)


score_manager = ScoreManager()
