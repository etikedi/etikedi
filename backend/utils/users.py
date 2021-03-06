import random
import string
from datetime import timedelta, datetime
from typing import Optional

from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError

from ..config import pwd_context, SECRET_KEY, ALGORITHM, oauth2_scheme, db
from ..models import User


def generate_password():
    password_characters = string.ascii_letters + string.digits + string.punctuation
    password_length = 8
    random_character_list = [random.choice(password_characters) for i in range(password_length)]
    password = "".join(random_character_list)
    return password


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user_by_id(user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return user


def get_user(username: str):
    user = db.query(User).filter(User.username == username).first()
    if user:
        return user


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
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


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
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
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter_by(username=username).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_admin(current_user: User = Depends(get_current_active_user)):
    if current_user.roles != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the necessary authorisations for this action. Please contact your admin!"
        )
    return current_user


def can_disable_admin(admin: User):
    other_active_admins = db.query(User).filter(
        User.roles == "admin",
        User.is_active == True,
        User.id != admin.id
    ).count()
    if not other_active_admins:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="You can not demote this account. There needs to be at least 1 active admin.",
        )
