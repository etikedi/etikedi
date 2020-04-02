# Backend
The backend features a REST API, built using [Flask](https://flask.palletsprojects.com/) and [Flask-RESTful](https://flask-restful.readthedocs.io/). 
For server side data storage a local SQLite database, stored at `test.db` is being used.

You need the following software preinstalled:

* Python3
* [pipenv](https://pipenv.pypa.io/en/latest/install/#installing-pipenv)

To set everything up run:

```bash
pipenv install
```

And afterwards to enter the virtual environment:

```bash
pipenv shell
```

The backend can then be started using

```bash
python aergia.py
```

As of now

The files `datasetPreparer.py` were used to initially populate the sqlite databes with the Resumee dataset and can be safely removed in the future.
