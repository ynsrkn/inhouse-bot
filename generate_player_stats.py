import os
import json
import re

champ_id_map = {
    266: "Aatrox",
    103: "Ahri",        
    84: "Akali",        
    166: "Akshan",      
    12: "Alistar",      
    32: "Amumu",        
    34: "Anivia",       
    1: "Annie",
    523: "Aphelios",    
    22: "Ashe",
    136: "Aurelion Sol",
    268: "Azir",
    432: "Bard",
    200: "Bel'Veth",
    53: "Blitzcrank",
    63: "Brand",
    201: "Braum",
    233: "Briar",
    51: "Caitlyn",
    164: "Camille",
    69: "Cassiopeia",
    31: "Cho'Gath",
    42: "Corki",
    122: "Darius",
    131: "Diana",
    119: "Draven",
    36: "Dr. Mundo",
    245: "Ekko",
    60: "Elise",
    28: "Evelynn",
    81: "Ezreal",
    9: "Fiddlesticks",
    114: "Fiora",
    105: "Fizz",
    3: "Galio",
    41: "Gangplank",
    86: "Garen",
    150: "Gnar",
    79: "Gragas",
    104: "Graves",
    887: "Gwen",
    120: "Hecarim",
    74: "Heimerdinger",
    910: "Hwei",
    420: "Illaoi",
    39: "Irelia",
    427: "Ivern",
    40: "Janna",
    59: "Jarvan IV",
    24: "Jax",
    126: "Jayce",
    202: "Jhin",
    222: "Jinx",
    145: "Kai'Sa",
    429: "Kalista",
    43: "Karma",
    30: "Karthus",
    38: "Kassadin",
    55: "Katarina",
    10: "Kayle",
    141: "Kayn",
    85: "Kennen",
    121: "Kha'Zix",
    203: "Kindred",
    240: "Kled",
    96: "Kog'Maw",
    897: "K'Sante",
    7: "LeBlanc",
    64: "Lee Sin",
    89: "Leona",
    876: "Lillia",
    127: "Lissandra",
    236: "Lucian",
    117: "Lulu",
    99: "Lux",
    54: "Malphite",
    90: "Malzahar",
    57: "Maokai",
    11: "Master Yi",
    902: "Milio",
    21: "Miss Fortune",
    62: "Wukong",
    82: "Mordekaiser",
    25: "Morgana",
    950: "Naafiri",
    267: "Nami",
    75: "Nasus",
    111: "Nautilus",
    518: "Neeko",
    76: "Nidalee",
    895: "Nilah",
    56: "Nocturne",
    20: "Nunu",
    2: "Olaf",
    61: "Orianna",
    516: "Ornn",
    80: "Pantheon",
    78: "Poppy",
    555: "Pyke",
    246: "Qiyana",
    133: "Quinn",
    497: "Rakan",
    33: "Rammus",
    421: "Rek'Sai",
    526: "Rell",
    888: "Renata Glasc",
    58: "Renekton",
    107: "Rengar",
    92: "Riven",
    68: "Rumble",
    13: "Ryze",
    360: "Samira",
    113: "Sejuani",
    235: "Senna",
    147: "Seraphine",
    875: "Sett",
    35: "Shaco",
    98: "Shen",
    102: "Shyvana",
    27: "Singed",
    14: "Sion",
    15: "Sivir",
    72: "Skarner",
    901: "Smolder",
    37: "Sona",
    16: "Soraka",
    50: "Swain",
    517: "Sylas",
    134: "Syndra",
    223: "Tahm Kench",
    163: "Taliyah",
    91: "Talon",
    44: "Taric",
    17: "Teemo",
    412: "Thresh",
    18: "Tristana",
    48: "Trundle",
    23: "Tryndamere",
    4: "Twisted Fate",
    29: "Twitch",
    77: "Udyr",
    6: "Urgot",
    110: "Varus",
    67: "Vayne",
    45: "Veigar",
    161: "Vel'Koz",
    711: "Vex",
    254: "Vi",
    234: "Viego",
    112: "Viktor",
    8: "Vladimir",
    106: "Volibear",
    19: "Warwick",
    498: "Xayah",
    101: "Xerath",
    5: "Xin Zhao",
    157: "Yasuo",
    777: "Yone",
    83: "Yorick",
    350: "Yuumi",
    154: "Zac",
    238: "Zed",
    221: "Zeri",
    115: "Ziggs",
    26: "Zilean",
    142: "Zoe",
    143: "Zyra"
}

MATCHES_PATH = "matches/"

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

    def __str__(self) -> str:
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

class Teammate:
    def __init__(self, playerDisplayName: str) -> None:
        self.playerDisplayName = playerDisplayName
        self.wins = 0
        self.losses = 0
        self.gamesPlayed = 0
        self.winrate = 0

    def add_game(self, win: bool) -> None:
        if win:
            self.wins += 1
        else:
            self.losses += 1
        self.gamesPlayed += 1
        self.winrate = int(round(self.wins / self.gamesPlayed * 100))

    def __str__(self) -> str:
        return f"{self.wins}W {self.losses}L ({self.winrate})"

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

class PlayerHistoricalStats:
    wins = 0
    losses = 0
    gamesPlayed = 0
    totalKills = 0
    totalDeaths = 0
    totalAssists = 0
    avgKills = 0
    avgDeaths = 0
    avgAssists = 0
    totalkda = 0
    averageDamageDealt = 0
    winrate = 0
    matchHistory = []
    totalGameDuration = 0
    totalCs = 0
    csPerMin = 0
    def __init__(self, playerName: str, playerDisplayName: str) -> None:
        self.matchHistory = []
        self.playerName = playerName
        self.playerDisplayName = playerDisplayName
        self.teammates = {}
        self.opponents = {}
        self.championStats = {}

    def add_game_stats(self, game_stats: PlayerGameStats) -> None:
        self.totalCs += game_stats.cs
        self.totalKills += game_stats.kills
        self.totalDeaths += game_stats.deaths
        self.totalAssists += game_stats.assists
        if self.totalDeaths == 0:
            self.totalkda = self.totalKills + self.totalAssists
        else:
            self.totalkda = round((self.totalKills + self.totalAssists) / self.totalDeaths, 2)
        
        self.gamesPlayed += 1

        self.avgKills = round(self.totalKills / self.gamesPlayed, 1)
        self.avgDeaths = round(self.totalDeaths / self.gamesPlayed, 1)
        self.avgAssists = round(self.totalAssists / self.gamesPlayed, 1)
        if game_stats.win:
            self.wins += 1
        else:
            self.losses += 1
        self.winrate = int(round(self.wins / (self.wins + self.losses) * 100, 0))
        self.matchHistory.insert(0, game_stats)

        self.averageDamageDealt = int(((self.averageDamageDealt * (self.gamesPlayed - 1)) + game_stats.damageDealt) / self.gamesPlayed)

        if self.championStats.get(game_stats.championName) is None:
            self.championStats[game_stats.championName] = ChampionStats(game_stats.championName)
        self.championStats[game_stats.championName].add_game(game_stats)

    def track_teammate_stats(self, win: bool, teammates, opponents):
            for teammate in teammates:
                if teammate.playerName == self.playerName:
                    continue

                if self.teammates.get(teammate.playerName) is None:
                    self.teammates[teammate.playerName] = Teammate(teammate.playerDisplayName)
                
                self.teammates[teammate.playerName].add_game(win)
            
            for opponent in opponents:
                if self.opponents.get(opponent.playerName) is None:
                    self.opponents[opponent.playerName] = Teammate(opponent.playerDisplayName)
                
                self.opponents[opponent.playerName].add_game(win)
    
    def add_game(self, game: Game, playerGameStats: PlayerGameStats) -> None:
        self.add_game_stats(playerGameStats)

        # track teammate and opponent information
        playerTeam = 1
        for player in game.team2:
            if player.playerName == self.playerName:
                playerTeam = 2
                break
        
        if playerTeam == 1:
            self.track_teammate_stats(playerGameStats.win, game.team1, game.team2)
        else:
            self.track_teammate_stats(playerGameStats.win, game.team2, game.team1)

        # track CS/min
        self.totalGameDuration += game.gameDuration
        self.csPerMin = round(self.totalCs / self.totalGameDuration * 60, 1)

    def __str__(self) -> str:
        res = ""
        res += f"{self.playerName}".ljust(16)
        res += f"{self.wins}W {self.losses}L ({self.winrate}% WR)".ljust(20)
        res += f"KDA: {self.avgKills} / {self.avgDeaths} / {self.avgAssists}".ljust(23)
        res += f"({self.totalkda})".ljust(10)
        res += f"Avg dmg: {self.averageDamageDealt:,}"
        return res
        

def track_player_stats(games):
    playerStats = {}

    for game in games:
        for playerGameStats in game.players:
            playerName = playerGameStats.playerName
            playerDisplayName = playerGameStats.playerDisplayName
            
            if playerName not in playerStats:
                playerStats[playerName] = PlayerHistoricalStats(playerName, playerDisplayName)
            
            playerStats[playerName].add_game( game, playerGameStats)

    return playerStats

def load_games(dir_path):
    games = []
    for i, matchFileName in enumerate(os.listdir(dir_path)):
        data = {}
        with open(dir_path + matchFileName, 'r') as fh:
            data = json.load(fh)
        
        games.append(Game(i + 1, data))
    
    games.sort(key=lambda x: x.id)

    return games

if __name__ == "__main__":
    DIR_PATH = "matches/"

    games = load_games(DIR_PATH)
    
    playerStats = track_player_stats(games)

    for game in games:
        print(game)

    for playerName, stats in sorted(playerStats.items(), key=lambda x: -x[1].winrate):
        print(stats)

