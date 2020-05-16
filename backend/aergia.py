from .config import app, db, guard
from .models import User

# Make all routes visible to the app
from .routes import *

# Guard is initialised here to prevent a circular import between `config.py` and the models
guard.init_app(app, User)

with app.app_context():
    db.init_app(app)
    db.create_all()

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

