from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "3fb64e315cf5256245416b77fcf0a3853f60a271680a5b9a6a7f8064594c195d"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

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
    }
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
