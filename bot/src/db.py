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


def get_arena(arena_id):
    col = get_collection("arena")
    arena = col.find({"_id": ObjectId(arena_id)})
    return arena[0]


def get_config():
    col = get_collection("botConfig")
    config = col.find({"name": BOT_ID})
    return config[0]