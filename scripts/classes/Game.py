from classes.PlayerGameStats import PlayerGameStats

class Game:
    def __init__(self, gameId: int, raw_data: dict) -> None:
        self.id = gameId
        self.pmap = {}
        for participant in raw_data['participantIdentities']:
            self.pmap[participant['participantId']] = participant['player']['summonerName']
        
        self.team1 = []
        self.team2 = []
        self.players = []
        for participant in raw_data['participants']:
            if participant['teamId'] == 100:
                self.team1.append(PlayerGameStats(participant, self.pmap, self.id))
            else:
                self.team2.append(PlayerGameStats(participant, self.pmap, self.id))

            self.players.append(PlayerGameStats(participant, self.pmap, self.id))
        
        if len(self.team1) > 5 or len(self.team2) > 5:
            raise Exception("Team size exceeded")
        
        self.gameDuration = raw_data['gameDuration']
        self.result = "Blue Win" if raw_data['teams'][0]['win'] == 'Win' else "Red Win"

    def __repr__(self) -> str:
        res = ""
        res += "=" * 20 + f"GAME {self.id}" + "="*20
        res += "\nBLUE:\n"
        for player in self.team1:
            res += f"    {player}\n"
        res += "RED:\n"
        for player in self.team2:
            res += f"    {player}\n"
        res += "=" * 50
        return res
