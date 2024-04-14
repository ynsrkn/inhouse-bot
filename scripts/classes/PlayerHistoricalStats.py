from scripts.classes.MatchHistoryMatch import MatchHistoryMatch
from scripts.classes.PlayerGameStats import PlayerGameStats
from scripts.classes.ChampionStats import ChampionStats
from scripts.classes.Teammate import Teammate
from scripts.classes.Game import Game
from scripts.classes.PlayerName import PlayerName

import trueskill


class PlayerHistoricalStats:
    wins: int = 0
    losses: int = 0
    gamesPlayed: int = 0
    totalKills: int = 0
    totalDeaths: int = 0
    totalAssists: int = 0
    avgKills: float = 0
    avgDeaths: float = 0
    avgAssists: float = 0
    totalkda: float = 0
    averageDamageDealt: float = 0
    winrate: float = 0
    totalGameDuration: int = 0
    totalCs: int = 0
    csPerMin: float = 0

    def __init__(self, name: PlayerName) -> None:
        self.matchHistory: list[MatchHistoryMatch] = []
        self.name: PlayerName = name
        self.teammates: dict[str, Teammate] = {}
        self.opponents: dict[str, Teammate] = {}
        self.championStats: dict[str, ChampionStats] = {}
        self.mmr = trueskill.Rating()

    def add_game_stats(self, game_stats: PlayerGameStats) -> None:
        self.totalCs += game_stats.cs
        self.totalKills += game_stats.kills
        self.totalDeaths += game_stats.deaths
        self.totalAssists += game_stats.assists
        if self.totalDeaths == 0:
            self.totalkda = self.totalKills + self.totalAssists
        else:
            self.totalkda = round(
                (self.totalKills + self.totalAssists) / self.totalDeaths, 2
            )

        self.gamesPlayed += 1

        self.avgKills = round(self.totalKills / self.gamesPlayed, 1)
        self.avgDeaths = round(self.totalDeaths / self.gamesPlayed, 1)
        self.avgAssists = round(self.totalAssists / self.gamesPlayed, 1)
        if game_stats.win:
            self.wins += 1
        else:
            self.losses += 1
        self.winrate = int(round(self.wins / (self.wins + self.losses) * 100, 0))

        self.averageDamageDealt = int(
            (
                (self.averageDamageDealt * (self.gamesPlayed - 1))
                + game_stats.damageDealt
            )
            / self.gamesPlayed
        )

        if self.championStats.get(game_stats.championName) is None:
            self.championStats[game_stats.championName] = ChampionStats(
                game_stats.championName
            )
        self.championStats[game_stats.championName].add_game(game_stats)

    def track_teammate_stats(
        self,
        win: bool,
        teammates: list[PlayerGameStats],
        opponents: list[PlayerGameStats],
    ):
        for teammate in teammates:
            if teammate.name == self.name:
                continue

            if self.teammates.get(teammate.name.name) is None:
                self.teammates[teammate.name.name] = Teammate(teammate.name)

            self.teammates[teammate.name.name].add_game(win)

        for opponent in opponents:
            if self.opponents.get(opponent.name.name) is None:
                self.opponents[opponent.name.name] = Teammate(opponent.name)

            self.opponents[opponent.name.name].add_game(win)

    def add_game(
        self, game: Game, playerGameStats: PlayerGameStats, mmrDelta: int
    ) -> None:
        self.add_game_stats(playerGameStats)

        self.matchHistory.insert(0, MatchHistoryMatch(playerGameStats, mmrDelta))

        # track teammate and opponent information
        playerTeam = 1
        for player in game.team2:
            if player.name == self.name:
                playerTeam = 2
                break

        if playerTeam == 1:
            self.track_teammate_stats(playerGameStats.win, game.team1, game.team2)
        else:
            self.track_teammate_stats(playerGameStats.win, game.team2, game.team1)

        # track CS/min
        self.totalGameDuration += game.gameDuration
        self.csPerMin = round(self.totalCs / self.totalGameDuration * 60, 1)

    def __repr__(self) -> str:
        res = ""
        res += f"{self.name.displayName}".ljust(16)
        res += f"{self.wins}W {self.losses}L ({self.winrate}% WR)".ljust(20)
        res += f"KDA: {self.avgKills} / {self.avgDeaths} / {self.avgAssists}".ljust(23)
        res += f"({self.totalkda})".ljust(10)
        res += f"Avg dmg: {self.averageDamageDealt:,}".ljust(20)
        res += f"MMR: {self.mmr}"
        return res
