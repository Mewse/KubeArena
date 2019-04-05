import os
import time
import logging
import requests
from pymongo import MongoClient
from bson import ObjectId
from constants import *
from db import get_arena, get_config

# Constants
RETRY_DELAY = 5

client = None
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("Bot: %s" % BOT_ID)

def get_arena_booking():
    # Contact boxoffice to get an arena booking
    arenaId = None
    while arenaId is None:
        try:
            logger.info("Calling the BoxOffice to make a reservation...")
            resp = requests.post(BOXOFFICE_URL, json={"botId": BOT_ID}, timeout=1)
            if resp.status_code == requests.codes['✓']: # 200
                arenaId = resp.json()["arenaId"]
                logger.info("New booking has been made! You are now a player in Arena-%s" % arenaId)
            elif resp.status_code == requests.codes["-o-"]: # 404
                logger.info("No booking can be made right now, please try again later...*click*")
                time.sleep(1)
            else: # Anything else
                logger.info("We're sorry, but the number you have dialled is not recognised. Please hangup and try again..")
                logger.error("BoxOffice returned %s for Bot %s" % (resp.status_code, BOT_ID))
                time.sleep(1)
        except Exception as e:
            logger.error("The BoxOffice...it's...gone! I looked everywhere but all I could find was: %s" % e)
            time.sleep(1)
        
arena_id = get_arena_booking()
logger.info("Online! Did you miss me?")
logger.info("Entering arena...")
while True:
    # read mongo
    # Determine what action must be taken to reach next command condition
    if arena_id:
        arena = get_arena(arena_id)
    else:
        logger.error("Arena has been shutdown...")
        break

logger.info("Fare thee well! x.x")
logger.error("R.I.P Bot %s" % BOT_ID)