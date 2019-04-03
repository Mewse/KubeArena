import os
import time
import logging
import requests

from pymongo import MongoClient
from bson import ObjectId

# ENV
MONGO_URL = os.environ.get("MONGO_URL", "localhost")
MONGO_PORT = os.environ.get("MONGO_PORT", 27017)
ARENA_ID = os.environ.get("ARENA_ID", "Demo")

# Constants
RETRY_DELAY = 5

client = None
logger = logging.getLogger("Arena: %s" % ARENA_ID)
def get_collection(collection):
    global client
    while client is None:
        try:
            logger.info("Connecting to mongo: %s:%s" % (MONGO_URL, MONGO_PORT))
            client = MongoClient(MONGO_URL, MONGO_PORT)
        except Exception as e:
            logger.exception("Could not connect to mongo: %s" % e)
            logger.info("Retrying connection in %s..." % RETRY_DELAY)
            time.sleep(RETRY_DELAY)
    return client

def get_arena():
    arenas = get_collection("arenas")
    arena = arenas.find({"_id": ObjectId(ARENA_ID)})
    return arena[0]

def get_player_action(player):
    url = "http://bot-%s/next" % player["id"]
    resp = requests.get(url, timeout=1000)

# Game Loop
while True:
    # Get players
    arena = get_arena()
    # Get player actions
    for bot in arena["players"]:

    # Action actions
    # Save new state