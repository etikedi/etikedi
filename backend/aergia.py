from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from .config import Config


app = Flask(__name__)
app.config.from_object(Config())

# Make the creation of REST endpoints a lot easier
api = Api(app)

# Configure Cross Origin Resource Sharing (CORS), making cross-origin AJAX possible
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# Create the database handler
db = SQLAlchemy(app)


with app.app_context():
    db.init_app(app)
    db.create_all()

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
