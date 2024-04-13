from scripts.classes.PlayerGameStats import PlayerGameStats


class MatchHistoryMatch:
    def __init__(self, gameStats: PlayerGameStats, mmrDelta: int) -> None:
        self.gameStats: PlayerGameStats = gameStats
        self.mmrDelta: int = mmrDelta
