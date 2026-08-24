from dataclasses import dataclass
from oracle.research.leaderboard import StrategyScore

@dataclass
class Champion:
    name: str
    score: float = float("-inf")

class ChampionChallenger:
    def __init__(self, champion: Champion) -> None:
        self.champion = champion

    def consider(self, candidate: StrategyScore) -> bool:
        if candidate.score <= self.champion.score:
            return False
        self.champion = Champion(candidate.name, candidate.score)
        return True
