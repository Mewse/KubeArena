import os
import time
import logging
import grequests

from pymongo import MongoClient
from bson import ObjectId

# ENV
MONGO_URL = os.environ.get("MONGO_URL", "localhost")
MONGO_PORT = os.environ.get("MONGO_PORT", 27017)
ARENA_ID = os.environ.get("ARENA_ID", "Demo")
ARENA_WIDTH = os.environ.get("ARENA_WIDTH", 500)
ARENA_HEIGHT = os.environ.get("ARENA_HEIGHT", 500)
ARENA_MAX_PLAYERS = os.environ.get("ARENA_MAX_PLAYERS", 10)
PLAYER_RADIUS = os.environ.get("PLAYER_RADIUS", 10)

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
    try:
        col = get_collection("bots")
        bot = col.find({"name": "player"})
        return bot["action"]
    except Exception as e:
        logger.error("Could not retrieve action from player: %s" % player)
        logger.exception(e)
        return {}

def apply_action(arena, player, action):
    # Movement
    player["position"] = move(player["position"], action["velocity"], action["speed"])

def move(position, direction, speed):
    new_position = {"x": 0, "y": 0}


# Arena Document
"""
arena = {
    "players": {
        "Player1": {
            name: "Player1",
            position: {x:200,y:542}
            rotation: 54,
            sensors: {
                movement_blocked: False,
                target_acquired: True,
                can_fire: False
            }
        }
    },
    "scores": {
        "Player1": 4,
        "MasterChief": 634
    },
    "projectiles": [
        {
            owner: "Player1",
            position: (110,402),
            velocity: (0.52,0.92),
            speed: 24
        }
    ]
}
"""


# Game Loop
while True:
    # Get players
    arena = get_arena()
    for player in arena["players"].keys():
        action = get_player_action(player, actions)
        apply_action(arena, player, action)
    # Save new state
    time.sleep(1/60)