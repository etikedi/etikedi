from datetime import timedelta
from logging.config import dictConfig
from dataclasses import dataclass, field
from flask.app import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_praetorian import Praetorian
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from flask_marshmallow import Marshmallow
from marshmallow import validate
from marshmallow_dataclass import class_schema


class Config(object):
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    SECRET_KEY = "ieantnqgevlngfgpznnnzpvngnfg1h08309e4ngferfpnqguivnqgh09ßengß"
    CSRF_ENABLED = False

    JWT_EXPIRATION_EDLAT = timedelta(days=10)
    JWT_ACCESS_LIFESPAN = {"hours": 24}
    JWT_REFRESH_LIFESPAN = {"days": 30}


dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

app = Flask(__name__)
app.config.from_object(Config())

### swagger specific ###
SWAGGER_URL = "/api-spec"
API_URL = "/static/swagger.yml"
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Aergia"}
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
cors = CORS(app, resources={r"/api/*": {"origins": "*"}, r"/login": {"origins": "*"}})


@dataclass
class ALConfig:
    SAMPLING: str = field(
        metadata={
            "validate": validate.OneOf(
                [
                    "random",
                    "uncertainty_lc",
                    "uncertainty_max_margin",
                    "uncertainty_entropy",
                ]
            )
        }
    )
    CLUSTER: str = field(
        metadata={
            "validate": validate.OneOf(
                [
                    "dummy",
                    "random",
                    "MostUncertain_lc",
                    "MostUncertain_max_margin",
                    "MostUncertain_entropy",
                ]
            )
        }
    )
    MINIMUM_TEST_ACCURACY_BEFORE_RECOMMENDATIONS: float = field(
        metadata={"validate": validate.Range(min=0, max=1)}
    )
    UNCERTAINTY_RECOMMENDATION_CERTAINTY_THRESHOLD: float = field(
        metadata={"validate": validate.Range(min=0.5, max=1)}
    )
    UNCERTAINTY_RECOMMENDATION_RATIO: float = field(
        metadata={"validate": validate.Range(min=0, max=1)}
    )
    CLUSTER_RECOMMENDATION_RATIO_LABELED_UNLABELED: float = field(
        metadata={"validate": validate.Range(min=0, max=1)}
    )
    CLUSTER_RECOMMENDATION_MINIMUM_CLUSTER_UNITY_SIZE: float = field(
        metadata={"validate": validate.Range(min=0, max=1)}
    )
    STOPPING_CRITERIA_UNCERTAINTY: float = field(
        metadata={"validate": validate.Range(min=0, max=1)}
    )
    STOPPING_CRITERIA_ACC: float = field(
        metadata={"validate": validate.Range(min=0, max=1)}
    )
    STOPPING_CRITERIA_STD: float = field(
        metadata={"validate": validate.Range(min=0, max=1)}
    )
    USER_QUERY_BUDGET_LIMIT: float = field(metadata={"validate": validate.Range(min=0)})
    RANDOM_SEED: float = field(metadata={"validate": validate.Range(min=-1)})
    NR_QUERIES_PER_ITERATION: int = field(metadata={"validate": validate.Range(min=0)})
    N_JOBS: int = field(metadata={"validate": validate.Range(min=-1)})
    NR_LEARNING_ITERATIONS: int = field(metadata={"validate": validate.Range(min=0)})
    ALLOW_RECOMMENDATIONS_AFTER_STOP: bool
    WITH_UNCERTAINTY_RECOMMENDATION: bool
    WITH_CLUSTER_RECOMMENDATION: bool
    WITH_SNUBA_LITE: bool

    RANDOM_SAMPLE_EVERY: int = field(metadata={"validate": validate.Range(min=5)})


ALConfigSchema = class_schema(ALConfig)

default_al_config = ALConfig(
    SAMPLING="uncertainty_max_margin",
    CLUSTER="MostUncertain_max_margin",
    NR_QUERIES_PER_ITERATION=100,
    WITH_UNCERTAINTY_RECOMMENDATION=True,
    WITH_CLUSTER_RECOMMENDATION=True,
    WITH_SNUBA_LITE=False,
    MINIMUM_TEST_ACCURACY_BEFORE_RECOMMENDATIONS=0,
    UNCERTAINTY_RECOMMENDATION_CERTAINTY_THRESHOLD=0.99,
    UNCERTAINTY_RECOMMENDATION_RATIO=0.01,
    CLUSTER_RECOMMENDATION_RATIO_LABELED_UNLABELED=0.8,
    CLUSTER_RECOMMENDATION_MINIMUM_CLUSTER_UNITY_SIZE=0.3,
    ALLOW_RECOMMENDATIONS_AFTER_STOP=True,
    STOPPING_CRITERIA_UNCERTAINTY=0,
    STOPPING_CRITERIA_ACC=0,
    STOPPING_CRITERIA_STD=0,
    USER_QUERY_BUDGET_LIMIT=2000,
    RANDOM_SEED=-1,
    N_JOBS=-1,
    NR_LEARNING_ITERATIONS=200000,
    RANDOM_SAMPLE_EVERY=10,
)
