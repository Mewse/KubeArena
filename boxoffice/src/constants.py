import os
import logging

# ENV
MONGO_URL = os.environ.get("MONGO_URL", "localhost")
MONGO_PORT = os.environ.get("MONGO_PORT", 27017)
LOG_LEVEL = os.environ.get("LOG_LEVEL", logging.INFO)