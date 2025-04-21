
from flask import Flask
from flask_cors import CORS
from app.routes.api import api
from app.utils.db import init_db
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = "supersecretkey"
    CORS(app, supports_credentials=True, origins=["http://localhost:5500"])
    app.register_blueprint(api)
    with app.app_context():
        init_db()
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
