from lcu_connector import Connector
from classes.ClientNotOpenException import ClientNotOpenException
from constants import MATCHES_PATH

import requests
import os
import json
import urllib3
import logging

# shut up let me write bad code
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set log level
logging.basicConfig(level=logging.INFO)

URL_BASE = "https://127.0.0.1:"
MATCHES_ENDPOINT = "/lol-match-history/v1/products/lol/current-summoner/matches"
GAMES_ENDPOINT = "/lol-match-history/v1/games/"


def scrape_match_data() -> None:
    """
        Scrape custom game data from an open local client's match history and adds the JSON
        result to the /matches folder
    """
    try:
        connector = Connector(start=True)
    except:
        logging.warning("Client closed, cannot scrape new games")
        raise ClientNotOpenException

    logging.info("Getting local match history")
    
    headers = connector.headers

    # get list of matches
    response = requests.get(
        connector.url + MATCHES_ENDPOINT,
        headers=headers,
        verify=False
    )
    riotGameIds = []
    # get riotGameIds of inhouse custom games
    matches = response.json()['games']['games']
    for match in matches:
        if match['gameMode'] == 'CLASSIC' and match['gameType'] == 'CUSTOM_GAME' and match['endOfGameResult'] == 'GameComplete':
            riotGameIds.append(match['gameId'])

    # get each match data
    retrieved_game = False
    for riotGameId in riotGameIds[::-1]:
        matchId = len(os.listdir(MATCHES_PATH)) + 1
        matchFileName = f"{MATCHES_PATH}/match-{riotGameId}.json"
        
        if not os.path.exists(matchFileName):
            logging.info(f"Getting data for riotGameId: {riotGameId}, matchId: {matchId}")
            response = requests.get(
                connector.url + GAMES_ENDPOINT + str(riotGameId),
                headers=headers,
                verify=False
            )
            retrieved_game = True
            
            match = json.dumps(response.json(), indent=4)
            with open(matchFileName, 'w') as matchFile:
                matchFile.write(match)
    
    if not retrieved_game:
        logging.info("No new games")


if __name__ == "__main__":
    scrape_match_data()
