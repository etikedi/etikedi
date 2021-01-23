from datetime import timedelta
from typing import Optional

from email_validator import validate_email, EmailNotValidError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..config import ACCESS_TOKEN_EXPIRE_MINUTES, app, db
from ..models import User, Token, UserInDB, UserNewPW
from ..utils import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
    generate_password,
    get_current_active_admin,
)

user_router = APIRouter()


@app.post("/token", response_model=Token, tags=["Users & Auth"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
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


@user_router.get("/me", response_model=UserInDB)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@user_router.post("/add_user", response_model=UserNewPW)
async def add_user(username: str,
                   email: str,
                   full_name: Optional[str] = None,
                   current_user: User = Depends(get_current_active_admin)):
    """
    Add new user. New user is automatically set active and as role worker. A random password is assigned.

    :str full_name: Optional: full name of the user \\
    :str email: email for user, needs to follow email format\\
    :str username: intended username for new user\\
    :return User and random PW in cleartext
    """

    users = db.query(User).filter(User.username == username).count()
    if users > 0:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="The user name {} already exists. Choose another user name!".format(username),
        )

    try:
        valid = validate_email(email, check_deliverability=False)
        email = valid.email
    except EmailNotValidError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="The e-mail {} is not valid. Reason: {}".format(email, e),
        )

    # set random PW
    password = generate_password()
    hashed_password = get_password_hash(password)

    # automatically active and worker
    new_user = User(username=username, email=email, roles='worker', password=hashed_password, fullname=full_name)
    db.add(new_user)
    db.commit()

    user = db.query(User).filter(User.username == username).first()
    return {"username": user.username,
            "email": user.email,
            "full_name": user.fullname,
            "disabled": user.is_active,
            "new_password": password}
