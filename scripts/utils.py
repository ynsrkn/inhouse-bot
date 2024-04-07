import logging
from pymongo import MongoClient
from pymongo.database import Database
import yaml

def chunks(arr: list, n: int) -> list:
    '''
        returns arr broken into n-sized chunks
    '''
    chunks = []
    for i in range(0, len(arr), n):
        chunks.append(arr[i: i + n])
    return chunks


def set_logging_config() -> None:
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def load_config(path: str) -> dict:
    set_logging_config()
    with open(path, 'r') as config_fh:
        config = yaml.safe_load(config_fh)
    return config


def get_database_connection(connection_string: str) -> Database:
    client = MongoClient(connection_string)
    return client['inhouse-bot']
