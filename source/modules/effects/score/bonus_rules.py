class BonusRules():
    """Regras de pontuacao especial: combos e multiplicadores (RF8)."""
    def __init__(self):
        self.multiplier = 1
        self.combo_count = 0

    def register_hit(self):
        self.combo_count += 1
        if self.combo_count % 5 == 0:
            self.multiplier += 1

    def reset_combo(self):
        self.combo_count = 0
        self.multiplier = 1

    def apply(self, points):
        return points * self.multiplier


bonus_rules = BonusRules()
