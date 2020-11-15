# from .config import guard
# from .models import User
# from .importing import import_test_datasets

# Make all routes visible to the app
# from .routes import *
from .routes.auth import *

from .config import app

# Guard is initialised here to prevent a circular import between `config.py` and the models
# guard.init_app(app, User)
#
#
# def create_dummy_users():
#     app.logger.info("Creating dummy users")
#     User.query.delete()
#     admin = User(
#         username="ernst_haft", password=guard.hash_password("adminadmin"), roles="admin"
#     )
#     db.session.add(admin)
#
#     worker1 = User(
#         username="anna_lühse",
#         password=guard.hash_password("very_secret"),
#         roles="worker",
#     )
#     db.session.add(worker1)
#
#     worker2 = User(
#         username="mario_nette",
#         password=guard.hash_password("very_secret"),
#         roles="worker",
#     )
#     db.session.add(worker2)
#
#
# with app.app_context():
#     db.init_app(app)
#     db.create_all()
#
#     # Create the dummy users if none already exists
#     if not User.query.count():
#         create_dummy_users()
#         db.session.commit()
#
#     if not Sample.query.count():
#         import_test_datasets()
#
#
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", debug=True)
