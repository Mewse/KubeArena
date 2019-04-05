import logging
from constants import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)
from flask import Flask, request
from db import get_next_available_arena
app = Flask(__name__)

logger = logging.getLogger(__name__)

@app.route("/enroll", methods=["POST"])
def enroll():
    try:
        data = request.get_json()
        logger.info("Request to join arena from %s" % data["botId"])
        arena = get_next_available_arena(data["botId"])
        if arena:
            return {"arena": str(arena)}, 202 # Accepted
        else:
            return "", 404 # No spaces found
    except Exception as e:
        logger.error("Unable to book player into arena: %s" % e)
        return "", 500 # It done broked

app.run(debug=True)