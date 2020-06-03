from dataclasses import dataclass
from datetime import timedelta
from flask.app import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_praetorian import Praetorian
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from flask_marshmallow import Marshmallow


@dataclass
class ALConfig:
    SAMPLING: str
    CLUSTER: str
    NR_QUERIES_PER_ITERATION: int
    WITH_UNCERTAINTY_RECOMMENDATION: bool
    WITH_CLUSTER_RECOMMENDATION: bool
    WITH_SNUBA_LITE: bool
    MINIMUM_TEST_ACCURACY_BEFORE_RECOMMENDATIONS: float
    UNCERTAINTY_RECOMMENDATION_CERTAINTY_THRESHOLD: float
    UNCERTAINTY_RECOMMENDATION_RATIO: float
    CLUSTER_RECOMMENDATION_RATIO_LABELED_UNLABELED: float
    CLUSTER_RECOMMENDATION_MINIMUM_CLUSTER_UNITY_SIZE: float
    ALLOW_RECOMMENDATIONS_AFTER_STOP: bool
    STOPPING_CRITERIA_UNCERTAINTY: float
    STOPPING_CRITERIA_ACC: float
    STOPPING_CRITERIA_STD: float
    USER_QUERY_BUDGET_LIMIT: float
    RANDOM_SEED: float
    N_JOBS: int
    NR_LEARNING_ITERATIONS: int


class Config(object):
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    SECRET_KEY = "ieantnqgevlngfgpznnnzpvngnfg1h08309e4ngferfpnqguivnqgh09ßengß"
    CSRF_ENABLED = False

    JWT_EXPIRATION_EDLAT = timedelta(days=10)
    JWT_ACCESS_LIFESPAN = {'hours': 24}
    JWT_REFRESH_LIFESPAN = {'days': 30}


app = Flask(__name__)
app.config.from_object(Config())

### swagger specific ###
SWAGGER_URL = '/api-spec'
API_URL = '/static/swagger.yml'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Aergia"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

# Make the creation of REST endpoints a lot easier
api = Api(app)

# Create the database handler
db = SQLAlchemy(app)

# Add Marshmallow dependency
ma = Marshmallow(app)

# Security and user management
guard = Praetorian()

# Configure Cross Origin Resource Sharing (CORS), making cross-origin AJAX possible
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
