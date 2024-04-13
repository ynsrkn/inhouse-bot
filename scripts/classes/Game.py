from scripts.classes.PlayerGameStats import PlayerGameStats
from scripts.classes.PlayerName import PlayerName


class Game:
    def __init__(self, gameId: int, raw_data: dict) -> None:
        self.id: int = gameId
        self.pmap: dict[int, PlayerName] = {}
        for p in raw_data["participantIdentities"]:
            self.pmap[p["participantId"]] = PlayerName(
                summonerName=p["player"]["summonerName"],
                name=p["player"]["gameName"],
                tag=p["player"]["tagLine"],
            )

        self.team1: list[PlayerGameStats] = []
        self.team2: list[PlayerGameStats] = []
        self.players: list[PlayerGameStats] = []
        for participant in raw_data["participants"]:
            if participant["teamId"] == 100:
                self.team1.append(PlayerGameStats(participant, self.pmap, self.id))
            else:
                self.team2.append(PlayerGameStats(participant, self.pmap, self.id))

            self.players.append(PlayerGameStats(participant, self.pmap, self.id))

        if len(self.team1) > 5 or len(self.team2) > 5:
            raise Exception("Team size exceeded")

        self.gameDuration: int = raw_data["gameDuration"]
        self.result: str = (
            "Blue Win" if raw_data["teams"][0]["win"] == "Win" else "Red Win"
        )

    def __repr__(self) -> str:
        res = ""
        res += "=" * 20 + f"GAME {self.id}" + "=" * 20
        res += "\nBLUE:\n"
        for player in self.team1:
            res += f"    {player}\n"
        res += "RED:\n"
        for player in self.team2:
            res += f"    {player}\n"
        res += "=" * 50
        return res
