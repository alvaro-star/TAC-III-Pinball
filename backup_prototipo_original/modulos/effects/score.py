"""Pontuação, combos, multiplicadores temporários e condições de multiball."""
from dataclasses import dataclass
from ..constants import BALLS_PER_PLAYER, START_BONUS_DURATION


@dataclass
class PlayerScore:
    score: int = 0
    remaining: int = BALLS_PER_PLAYER
    bumpers_chain: int = 0
    targets_hit: int = 0
    multiplier_time: float = 0.0
    multiball_earned: bool = False

    def multiplier(self):
        return 2 if self.multiplier_time > 0 else 1

    def add_points(self, points, kind='obstacle'):
        total = points*self.multiplier()
        self.score += total
        if kind=='bumper':
            self.bumpers_chain += 1
            if self.bumpers_chain % 6 == 0:
                self.score += 500*self.multiplier()
                return total, 'COMBO +500'
        if kind=='target':
            self.targets_hit += 1
            if self.targets_hit == 3:
                self.multiplier_time = START_BONUS_DURATION
                return total, 'PONTUAÇÃO 2X'
            if self.targets_hit == 6 and not self.multiball_earned:
                self.multiball_earned = True
                return total, 'MULTIBALL'
        return total, None

    def update(self, dt):
        self.multiplier_time = max(0.0, self.multiplier_time-dt)
