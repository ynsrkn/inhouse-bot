from classes.PlayerGameStats import PlayerGameStats

class MatchHistoryMatch:
    def __init__(self, gameStats: PlayerGameStats, mmrDelta: int) -> None:
        self.gameStats = gameStats
        self.mmrDelta = mmrDelta