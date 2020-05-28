import json
from .config import app, db, guard
from .models import User, Dataset, Label, Table

# Make all routes visible to the app
from .routes import *

# Guard is initialised here to prevent a circular import between `config.py` and the models
guard.init_app(app, User)


def create_dummy_users():
    app.logger.info('Creating dummy users')
    admin = User(
        username='ernst_haft',
        password=guard.hash_password('adminadmin'),
        roles='admin'
    )
    db.session.add(admin)

    worker1 = User(
        username='anna_lühse',
        password=guard.hash_password('very_secret'),
        roles='worker'
    )
    db.session.add(worker1)

    worker2 = User(
        username='mario_nette',
        password=guard.hash_password('very_secret'),
        roles='worker'
    )
    db.session.add(worker2)


def create_dummy_samples():
    dwtc = Dataset(name='DWTC')
    db.session.add(dwtc)

    beautiful = Label(name='Beautiful', dataset=dwtc)
    disgusting = Label(name='Disgusting', dataset=dwtc)
    db.session.add_all([beautiful, disgusting])

    sample_table_content = """
    <table>
        <thead>
            <tr>
                <td>One</td>
                <td>Two</td>
            </tr> 
        </thead>
        <tbody>
            <tr>
                <td>Hello</td> 
                <td>World</td> 
            </tr> 
        </tbody>
    </table> 
    """
    sample1 = Table(
        dataset=dwtc,
        features=json.dumps({
            'rows': 2,
            'color': 'red'
        }),
        content=sample_table_content
    )
    sample2 = Table(
        dataset=dwtc,
        features=json.dumps({
            'rows': 2,
            'color': 'blue'
        }),
        content=sample_table_content
    )
    db.session.add_all([sample1, sample2])


with app.app_context():
    db.init_app(app)
    db.create_all()

    # Create the dummy users if none already exists
    if not User.query.count():
        create_dummy_users()
        create_dummy_samples()
        db.session.commit()

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

