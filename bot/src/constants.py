import os
import logging

# ENV
MONGO_URL = os.environ.get("MONGO_URL", "localhost")
MONGO_PORT = os.environ.get("MONGO_PORT", 27017)

BOXOFFICE_URL = os.environ.get("BOXOFFICE_URL", "http://localhost:5001/enroll")

BOT_ID = os.environ.get("BOT_ID", "5ca65e92c2d2da8069951d59")
LOG_LEVEL = os.environ.get("LOG_LEVEL", logging.INFO)