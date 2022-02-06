from flask import Flask, request
from mongoengine import Document, connect
import json
from bson import ObjectId

# Create application
app = Flask(__name__)

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# MongoDB settings
app.config['MONGODB_SETTINGS'] = {
    'alias':'registry',
    'db': 'registry',
    'host': 'db',
    'port': "",
    'username': 'root',
    'password': 'password'
    }


# Build db connection with straight mongoengine
# mongo = connect('registry', host='mongodb://admin:password@0.0.0.0:27017/registry', alias='registry-db')

mongo = connect(**app.config['MONGODB_SETTINGS'])
