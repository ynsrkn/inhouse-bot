import logging
from pymongo import MongoClient
from pymongo.database import Database
import yaml

def chunks(arr: list, n: int):
    '''
        returns arr broken into n-sized chunks
    '''
    chunks = []
    for i in range(0, len(arr), n):
        chunks.append(arr[i: i + n])
    return chunks


def set_logging_config():
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def get_database_connection(config: dict) -> Database:
    client = MongoClient(config['DB_CONNECTION_STRING'])
    return client['inhouse-bot']
