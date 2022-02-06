from flask import Blueprint, current_app as app
import json

mod = Blueprint('/', __name__)

@mod.route('/', methods=["GET"])
def root():
    return app.response_class(
        response=json.dumps(
            {
                "api": "online"
            }
        ),
        headers={"Content-Type":"application/json"},
        mimetype='application/json',
        status=200
    )