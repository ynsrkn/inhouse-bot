from classes.PlayerGameStats import PlayerGameStats

class ChampionStats:
    def __init__(self, championName) -> None:
        self.championName = championName
        self.gamesPlayed = 0
        self.wins = 0
        self.losses = 0
        self.winrate = 0
        self.totalKills = 0
        self.totalDeaths = 0
        self.totalAssists = 0
        self.avgKills = 0
        self.avgDeaths = 0
        self.avgAssists = 0
        self.avgkda = 0


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