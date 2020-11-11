from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from models.schemas import UserInDB, TokenData, User, Token, DatasetBase
from models.models import Dataset


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


# models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


##############################################################################################################
#                                               Users                                                        #
##############################################################################################################


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


##############################################################################################################
#                                               Dataset                                                      #
##############################################################################################################

@app.get("/api/datasets", response_model=DatasetBase)
async def get_dataset_list():
    """
            This function responds to a request for /api/datasets
            with the complete lists of data sets

            :return:        list of datasets (e.g. dwtc, religious_texts...)
            """
    datasets = Dataset.query.all()
    return DatasetBase(many=True).dump(datasets)


@app.post("/api/datasets", response_model=DatasetBase)
async def post_dataset_list():
    return "TODO"


@app.get("/api/datasets/{dataset_id}", response_model=DatasetBase)
async def get_dataset_details(dataset_id: int):
    return "TODO"


@app.post("/api/datasets/{dataset_id}", response_model=DatasetBase)
async def post_dataset_details(dataset_id: int):
    return "TODO"


##############################################################################################################
#                                                   Labels                                                   #
##############################################################################################################


@app.get("/api/datasets/{dataset_id}/labels")
async def get_labels(dataset_id: int):
    return "TODO"


@app.post("/api/datasets/{dataset_id}/labels")
async def post_labels(dataset_id: int):
    return "TODO"


##############################################################################################################
#                                                   Samples                                                  #
##############################################################################################################

@app.get("/api/sample/{sample_id}")
async def get_sample(sample_id: int):
    return "TODO"


@app.post("/api/sample/{sample_id}")
async def post_sample(sample_id: int):
    return "TODO"


##############################################################################################################
#                                                   Config                                                   #
##############################################################################################################

@app.get("/api/datasets/{dataset_id}/config")
async def get_dataset_config(dataset_id: int):
    return "TODO"


@app.post("/api/datasets/{dataset_id}/config")
async def post_dataset_config(dataset_id: int):
    return "TODO"


##############################################################################################################
#                                                   Importing                                                #
##############################################################################################################

@app.post("/api/datasets/{dataset_id}/import")
async def post_import(dataset_id: int):
    return "TODO"
