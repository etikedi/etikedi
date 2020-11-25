from .database import db
from .logger import logger

fake_users_db = {
    "ernst_haft": {
        "username": "ernst_haft",
        "full_name": "Ernst Haft",
        "email": "ernsthaft@example.com",
        "hashed_password": "$2b$12$2TfAuYT9tMAbhc5vRKZs5uLEcUNRtwDPUFuhqDqiRK7XufHV/S4a.",
        "disabled": False,
    },
    "anna_lühse": {
        "username": "anna_lühse",
        "full_name": "Anna Lühse",
        "email": "annalühse@example.com",
        "hashed_password": "$2b$12$0jILJK2b1vIoQCfWcU4U1.6X9M16F68WAQW4.BqsNJ69iiZFc.HAC",
        "disabled": False,
    },
    "mario_nette": {
        "username": "mario_nette",
        "full_name": "Mario Nette",
        "email": "marionette@example.com",
        "hashed_password": "$2b$12$0jILJK2b1vIoQCfWcU4U1.6X9M16F68WAQW4.BqsNJ69iiZFc.HAC",
        "disabled": False,
    },
}
