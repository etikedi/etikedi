# Backend
The backend features a REST API, built using [Flask](https://flask.palletsprojects.com/) and [Flask-RESTful](https://flask-restful.readthedocs.io/). 
For server side data storage a local SQLite database, stored at `test.db` is being used.

You need the following software preinstalled:

* Python3
* [pipenv](https://pipenv.pypa.io/en/latest/install/#installing-pipenv)

To set everything up run:

```bash
pipenv install --dev
```

And afterwards to enter the virtual environment:

```bash
pipenv shell
```

The backend can then be started using

```bash
python aergia.py
```

In your editor you can set as code formatter [black](https://github.com/psf/black).

## Code overview
`aergia.py` just starts the backend and ties everything together. The REST API endpoints are specified here.

## Models
For each database table a Model file should be created using [FlasktSQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/).
The `*API` classes define the logic for the REST API using [Flask-RESTful](https://flask-restful.readthedocs.io/), actually not much code is needed here as the underlying framework is doing all the work for us.

`Note:` in the example model `models/resumees.py` is currently a lot of deprecated logic in the `generateFeatures()` method which can be safely removed, as the features should be precalculated and be imported together with the dataset directly into the database. 
So this backend can and should assume that the features are already existent.

## REST API
To communicate with the frontend the backend provides a REST API.
In `aergia.py` the endpoints are defined, which in turn refer to the specified endpoints in the model.
To test the Api without the frontend you can use f. e. curl:
```
curl http://127.0.0.1:5000/api/resumees/2
```

## test.db
The file `datasetPreparer.py` was used to initially populate the sqlite database with the Resumee dataset. 
In a later version this should be removed by a frontend enabling the users to easily add new datasets.
Note that by now only the raw data is stored in the database, it has to be adjusted of course to contain the features as new rows in addition to the original data.
