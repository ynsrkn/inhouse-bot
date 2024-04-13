from scripts.constants import champ_id_map
from scripts.classes.PlayerName import PlayerName


class PlayerGameStats:
    def __init__(self, raw_stats, pmap, gameId) -> None:
        self.gameId: int = gameId
        self.name: PlayerName = pmap[raw_stats["participantId"]]
        self.championId: int = raw_stats["championId"]
        self.championName: str = champ_id_map[self.championId]
        self.cs: int = (
            raw_stats["stats"]["totalMinionsKilled"]
            + raw_stats["stats"]["neutralMinionsKilled"]
        )
        self.kills: int = raw_stats["stats"]["kills"]
        self.deaths: int = raw_stats["stats"]["deaths"]
        self.assists: int = raw_stats["stats"]["assists"]
        self.win: bool = raw_stats["stats"]["win"]
        self.damageDealt: int = raw_stats["stats"]["totalDamageDealtToChampions"]
        self.team: str = "Blue" if raw_stats["teamId"] == 100 else "Red"
        if self.deaths == 0:
            self.kda: float = self.kills + self.assists
        else:
            self.kda: float = round((self.kills + self.assists) / self.deaths, 2)

    def __str__(self) -> str:
        return f"""{self.championName:15} {self.kills}/{self.deaths}/{self.assists} ({self.kda})"""
