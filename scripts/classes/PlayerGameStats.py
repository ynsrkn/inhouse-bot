from constants import champ_id_map

class PlayerGameStats:
    def __init__(self, raw_stats, pmap, gameId) -> None:
        self.gameId = gameId
        self.playerId = raw_stats['participantId']
        self.playerName = pmap[self.playerId].lower()
        self.playerDisplayName = pmap[self.playerId]
        self.championId = raw_stats['championId']
        self.championName = champ_id_map[self.championId]
        self.cs = raw_stats['stats']['totalMinionsKilled'] + raw_stats['stats']['neutralMinionsKilled']
        self.kills = raw_stats['stats']['kills']
        self.deaths = raw_stats['stats']['deaths']
        self.assists = raw_stats['stats']['assists']
        self.win = raw_stats['stats']['win']
        self.damageDealt = raw_stats['stats']['totalDamageDealtToChampions']
        self.team = 'Blue' if raw_stats['teamId'] == 100 else 'Red'
        if self.deaths == 0:
            self.kda = self.kills + self.assists
        else:
            self.kda = round((self.kills + self.assists) / self.deaths, 2)

    def __str__(self) -> str:
        return f"""{self.championName:15} {self.kills}/{self.deaths}/{self.assists} ({self.kda})"""
