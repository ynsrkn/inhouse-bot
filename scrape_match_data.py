import requests
import os
import json
import urllib3
import logging
import sys

# shut up let me write bad code
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set log level
logging.basicConfig(level=logging.INFO)

URL_BASE = "https://127.0.0.1:"
MATCHES_ENDPOINT = "/lol-match-history/v1/products/lol/current-summoner/matches"
GAMES_ENDPOINT = "/lol-match-history/v1/games/"

if __name__ == "__main__":
    port = sys.argv[1]
    auth = sys.argv[2]

    headers = {
        'accept': 'application/json',
        'Authorization': 'Basic ' + auth,
    }

    # get list of matches
    response = requests.get(
        URL_BASE + port + MATCHES_ENDPOINT,
        headers=headers,
        verify=False,
    )
    riotGameIds = []
    # get riotGameIds of inhouse custom games
    matches = response.json()['games']['games']
    for match in matches:
        if match['gameMode'] == 'CLASSIC' and match['gameType'] == 'CUSTOM_GAME' and match['endOfGameResult'] == 'GameComplete':
            riotGameIds.append(match['gameId'])
    
    # get each match data
    for i, riotGameId in enumerate(riotGameIds[::-1]):
        matchId = len(os.listdir("matches/")) + 1
        matchFileName = f"matches/match-{riotGameId}.json"
        if not os.path.exists(matchFileName):
            logging.info(f"Getting data for riotGameId: {riotGameId}, matchId: {matchId}")
            response = requests.get(
                URL_BASE + port + GAMES_ENDPOINT + str(riotGameId),
                headers=headers,
                verify=False
            )
            
            match = json.dumps(response.json(), indent=4)
            with open(matchFileName, 'w') as matchFile:
                matchFile.write(match)