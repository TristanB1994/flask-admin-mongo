from mongoengine import connect
from app_config import MONGO_DB_URI, MONGO_DB_NAME
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Mongo(object):
    
    def __init__(self):
        try:
            self.mongo = connect(db=MONGO_DB_NAME, host=MONGO_DB_URI)
        except Exception as ex:
            logger.error(f"Mongo init failed: {ex}")
    
    def return_mongo(self):
        return self.mongo