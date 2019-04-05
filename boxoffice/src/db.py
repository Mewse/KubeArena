from pymongo import MongoClient
from bson import ObjectId
from constants import *

# Constants
RETRY_DELAY = 5

client = None
logger = logging.getLogger(__name__)


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


def get_next_available_arena(player):
    col = get_collection("arena")
    arena_id = col.find_one_and_update(
        {"$where": "this.players.length <= this.maxPlayers"}, 
        {"$push": {"players": {"name": player}}}
    )
    logger.info(str(arena_id))
    if arena_id:
        # Success, we are now in a game
        logger.info("Successfully joined arena: %s" % arena_id)
        return arena_id
    else:
        # No space available in any arenas
        logger.info("No spaces available in any arena..")
        # TODO Dynamically create a new Arena deployment to account for this load
        return None