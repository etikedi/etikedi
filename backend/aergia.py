from active_learning_process.test_resources import Start, Index
from app_init import app, db, api

with app.app_context():
    db.init_app(app)
    db.create_all()

    api.add_resource(Start, "/api/start")
    api.add_resource(Index, "/api/index")

if __name__ == "__main__":
    app.run()
