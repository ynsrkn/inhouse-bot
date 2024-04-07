from classes.PlayerGameStats import PlayerGameStats


class ChampionStats:
    def __init__(self, championName: str) -> None:
        self.championName: str = championName
        self.gamesPlayed: int = 0
        self.wins: int = 0
        self.losses: int = 0
        self.winrate: float = 0
        self.totalKills: int = 0
        self.totalDeaths: int = 0
        self.totalAssists: int = 0
        self.avgKills: int = 0
        self.avgDeaths: int = 0
        self.avgAssists: int = 0
        self.avgkda: float = 0

    def add_game(self, game_stats: PlayerGameStats):
        self.gamesPlayed += 1
        if game_stats.win:
            self.wins += 1
        else:
            self.losses += 1
        self.winrate = int(round(self.wins / self.gamesPlayed * 100, 0))

        self.totalKills += game_stats.kills
        self.totalDeaths += game_stats.deaths
        self.totalAssists += game_stats.assists

        self.avgKills = round(self.totalKills / self.gamesPlayed, 1)
        self.avgDeaths = round(self.totalDeaths / self.gamesPlayed, 1)
        self.avgAssists = round(self.totalAssists / self.gamesPlayed, 1)

        if self.avgDeaths == 0:
            self.avgkda = self.avgKills + self.avgAssists
        else:
            self.avgkda = round((self.avgKills + self.avgAssists) / self.avgDeaths, 2)

    def __repr__(self) -> str:
        return f"{self.championName}: {self.gamesPlayed} games ({self.winrate}% WR)"
