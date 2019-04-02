import os
import time
from pymongo import MongoClient
import logging
from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from bson.objectid import ObjectId

# Pull in environment config
MONGO_URL = os.environ.get("MONGO_URL", "localhost")
MONGO_PORT = os.environ.get("MONGO_PORT", 27017)
# Setup
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger = logging.getLogger("werkzeug")
logger.addHandler(ch)

app = Flask(__name__)
api = Api(app)

client = None

def get_db_client():
    # Only connect if required
    global client
    while client is None:
        try:
            logger.info("Connecting to mongo: %s:%s" % (MONGO_URL, MONGO_PORT))
            client = MongoClient(MONGO_URL, MONGO_PORT)
        except Exception as e:
            logger.exception("Could not connect to Mongo: %s" % e)
            logger.info("Retrying connection in %s seconds..." % "5")
            time.sleep(5)
    return client

def get_collection(collection):
    client = get_db_client()
    db = client.kubearena
    return db[collection]

class BotConfig(Resource):
    def get(self, id):
        col = get_collection("botConfigs")
        doc = col.find({"_id": ObjectId(id)})
        if doc:
            config = {
                "configId": doc[0]["configId"],
                "commands": doc[0]["commands"],
                "id": str(doc[0]["_id"])
            }
            return config, 200
        else:
            return "No config with this ID was found", 404

    def put(self, id):
        col = get_collection("botConfigs")
        data = request.get_json()
        updated_config = {
            "configId": data["name"],
            "commands": data["commands"]
        }
        result = col.update({"_id": ObjectId(id)}, updated_config)
        if result["n"] > 0:
            return "Config Updated", 200
        else: 
            return "No config with this ID was found", 404

    def delete(self, id):
        col = get_collection("botConfigs")
        deleted = col.remove({"_id": ObjectId(id)})
        logger.info("Deleted: %s" % deleted)
        if deleted["n"] > 0:
            return "", 200
        else: 
            return "No config with this ID was found", 404

class BotConfigList(Resource):
    def get(self):
        col = get_collection("botConfigs")
        docs = col.find()
        configs = []
        for d in docs:
            configs.append(
                {
                    "id": str(d["_id"]),
                    "configId": d["configId"]
                }
            )
        return {"configs": configs}

    def post(self):
        configs = get_collection("botConfigs")
        logger.info("POST Data: %s" % request.get_json())
        data = request.get_json()
        
        existing = configs.count_documents({"configId": data["name"]})
        if existing > 0:
            return "A configuration with this name already exists", 409

        new_config = {
            "configId": data["name"],
            "commands": data["commands"]
        }
        _id = configs.insert(new_config)
        logger.info("New config created: %s" % _id)
        return "",204

api.add_resource(BotConfig, "/config/<string:id>")
api.add_resource(BotConfigList, "/config")

app.run(debug=True)