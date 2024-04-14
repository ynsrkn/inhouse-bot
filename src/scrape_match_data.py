from src.classes.ClientNotOpenException import ClientNotOpenException
from src.utils import load_config, get_database_connection
from src.constants import CONFIG_PATH

from lcu_connector import Connector
import requests
import urllib3
import logging
from pymongo.database import Database

# shut up let me write bad code
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MATCHES_ENDPOINT = "/lol-match-history/v1/products/lol/current-summoner/matches"
GAMES_ENDPOINT = "/lol-match-history/v1/games/"


def scrape_match_data(db: Database) -> None:
    """
    Scrapes custom game data from an open local client's match history and inserts into DB
    """
    try:
        connector = Connector(start=True)
    except:
        logging.warning("Client closed, cannot scrape new games")
        raise ClientNotOpenException

    logging.info("Getting local match history")

    matches_table = db["matches"]

    headers = connector.headers

    # get list of matches
    response = requests.get(
        connector.url + MATCHES_ENDPOINT, headers=headers, verify=False
    )
    riot_game_ids = []
    # get riotGameIds of inhouse custom games
    try:
        matches = response.json()["games"]["games"]
    except KeyError:
        logging.error("Unexpected error when trying to query local match history")
        return

    for match in matches:
        if (
            match["gameMode"] == "CLASSIC"
            and match["gameType"] == "CUSTOM_GAME"
            and match["endOfGameResult"] == "GameComplete"
        ):
            riot_game_ids.append(match["gameId"])

    # get each match data
    retrieved_game = False
    for riot_game_id in riot_game_ids[::-1]:
        query_results = matches_table.find_one({"gameId": riot_game_id})

        if query_results is None:
            logging.info(f"Getting data for riotGameId: {riot_game_id}")
            response = requests.get(
                connector.url + GAMES_ENDPOINT + str(riot_game_id),
                headers=headers,
                verify=False,
            )
            retrieved_game = True

            matches_table.insert_one(response.json())

    if not retrieved_game:
        logging.info("No new games")


if __name__ == "__main__":
    config = load_config(CONFIG_PATH)

    db = get_database_connection(config["DB_CONNECTION_STRING"])
    scrape_match_data(db)
