import os
import time
import logging

from pymongo import MongoClient
from bson import ObjectId

# ENV
MONGO_URL = os.environ.get("MONGO_URL", "localhost")
MONGO_PORT = os.environ.get("MONGO_PORT", 27017)
ARENA_ID = os.environ.get("ARENA_ID", "5ca65e92c2d2da8069951d59")
ARENA_WIDTH = os.environ.get("ARENA_WIDTH", 500)
ARENA_HEIGHT = os.environ.get("ARENA_HEIGHT", 500)
ARENA_MAX_PLAYERS = os.environ.get("ARENA_MAX_PLAYERS", 10)
PLAYER_RADIUS = os.environ.get("PLAYER_RADIUS", 10)
LOG_LEVEL = os.environ.get("LOG_LEVEL", logging.DEBUG)
# Constants
RETRY_DELAY = 5

client = None
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("Arena: %s" % ARENA_ID)


def get_db_client():
    """
    Retry connecting to mongo until successful. Blocking function until connection is successful
    :return: MongoClient
    """
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


def get_collection(collection):
    """
    Return collection after connecting to mongo if required.
    :param collection: String  Name of the collection to return
    :return: MongoClient.Collection
    """
    client = get_db_client()
    db = client.kubearena
    return db[collection]


def get_arena():
    """
    Return the Arena document that matches the ID of this instance
    :return:
    """
    arenas = get_collection("arena")
    arena = arenas.find({"_id": ObjectId(ARENA_ID)})
    return arena[0]


def get_player_action(player):
    """
    Retrieve the bot document from DB containing the current action to perform
    Returns empty action on any exceptions
    :param player: String  Which player to retrieve action for
    :return: Dict
    """
    try:
        col = get_collection("bots")
        bot = col.find({"name": player})
        return bot[0]["action"]
    except Exception as e:
        logger.error("Could not retrieve action from player: %s" % player)
        logger.exception(e)
        return {}


def apply_action(arena, player, action):
    """
    Apply any movements or rotations to the bot in the arena. Also trigger firing if conditions are met
    :param arena: Dict  Main arena object to update
    :param player: String  Player to update
    :param action: Dict  Changes to make to the bot in the arena
    """
    bot = arena["players"][player]
    # Movement
    bot["position"] = move(bot["position"], action["direction"], action["speed"])
    # Rotation
    bot["rotation"] = action["rotate"]
    # Fire


def clamp(value, low, high):
    return max(low, min(value, high))


def move(position, direction, speed):
    """
    Move the player within the confines of the arena
    :param position: Dict  Starting position
    :param direction: Dict  Vector to move bot
    :param speed: Int  Speed at which to move
    :return: Dict  New location after movement vector applied
    """
    new_x = position["x"] + (direction["x"] * speed)
    new_y = position["y"] + (direction["y"] * speed)
    new_x = clamp(new_x, 0, ARENA_WIDTH-PLAYER_RADIUS)
    new_y = clamp(new_y, 0, ARENA_HEIGHT-PLAYER_RADIUS)
    return {"x": new_x, "y": new_y}


def calculate_collisions(arena):
    """
    Detect collisions with walls and other players
    Raycast from player turret and detect LOS
    Update bot sensors based on collisions detected
    :param arena: Dict  Arena object to scan and update
    """
    # Detect wall collisions
    # Detect player collisions
    # Detect projectile collisions
    # Detect raycast collisions
    pass


def save_arena(arena):
    """
    Update the DB with the arena data
    :param arena: Dict  New arena data
    """
    col = get_collection("arena")
    result = col.update({"_id": ObjectId(ARENA_ID)}, arena)
    if result["n"] <= 0:
        logger.error("Unable to save arena state for arena %s..." % ARENA_ID)


def startup():
    """
    Print startup info
    """
    arena = get_arena()
    logger.info("Welcome to the Arena...")
    logger.info("This is Arena %s" % ARENA_ID)
    logger.info("Arena Dimensions: %s x %s. Max Players: %s" % (ARENA_WIDTH, ARENA_HEIGHT, ARENA_MAX_PLAYERS))
    logger.info("Starting player list: %s" % [player for player in arena["players"].keys()])


def run():
    """
    Main game loop
    Runs forever
    """
    startup()
    while True:
        try:
            arena = get_arena()
            for player in arena["players"].keys():
                # Get player actions from Db
                action = get_player_action(player)
                # Apply movement/rotation/firing condition
                apply_action(arena, player, action)
            # Update sensors
            calculate_collisions(arena)
            # Save any changes made this iteration
            save_arena(arena)
            # 10 frames per second
            time.sleep(0.1)
        except Exception as e:
            logger.error("Blissfully ignoring Exception in main game loop: %s" % e)

run()
logger.error("Great, you broke it...")
