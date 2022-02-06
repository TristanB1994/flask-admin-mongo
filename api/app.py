from flask import Flask
from ext.mongo import Mongo
from controller import home


def register_app_modules(app_instance):
    """
        Takes application blueprints and registers them to the app object
    """
    app_instance.register_blueprint(
        home.mod, url_prefix="/"
    )
    return

def create_app(config_file="app_config.py"):
    app_instance = Flask(__name__)
    app_instance.config.from_pyfile(config_file)
    register_app_modules(app_instance)
    app_instance.db = Mongo().return_mongo()
    return app_instance
