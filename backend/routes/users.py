from datetime import timedelta
from typing import Optional, List

from email_validator import validate_email, EmailNotValidError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..config import ACCESS_TOKEN_EXPIRE_MINUTES, app, db, MINIMAL_PASSWORD_LENGTH
from ..models import User, Token, UserInDB, UserNewPW, BaseUserSchema, UserWithRole, NewRole
from ..utils import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
    generate_password,
    get_current_active_admin,
    get_user_by_id,
    can_disable_admin
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


@user_router.get("", response_model=List[UserWithRole])
async def get_all_users(current_user: User = Depends(get_current_active_user)):
    return db.query(User).all()


@user_router.get("/me", response_model=UserWithRole)
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
            detail="The user name {} already exists. Choose another username!".format(username),
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
            "fullname": user.fullname,
            "is_active": user.is_active,
            "new_password": password}


@user_router.post("/{user_id}/disable_user", response_model=BaseUserSchema)
async def disable_user(user_id: int, current_user: User = Depends(get_current_active_admin)):
    """
    Disable user through admin.

    :int user_id:\\
    :return user
    """
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The User {} does not exist.".format(user_id),
        )

    if 'admin' in user.roles:
        can_disable_admin(user)

    user.is_active = False
    db.commit()

    return db.query(User).filter(User.id == user_id).first()


@user_router.post("/{user_id}/activate_user", response_model=BaseUserSchema)
async def activate_user(user_id: int, current_user: User = Depends(get_current_active_admin)):
    """
    Enable user through admin.

    :int user_id:\\
    :return user
    """
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The User {} does not exist.".format(user_id),
        )

    user.is_active = True
    db.commit()

    user = db.query(User).filter(User.id == user_id).first()
    return user


@user_router.post("/{user_id}/reset_password", response_model=UserNewPW)
async def reset_password(user_id: int, current_user: User = Depends(get_current_active_admin)):
    """
    Reset password for user with user_id through admin.

    :int user_id: \\
    :return user and new cleartext pw
    """

    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The User {} does not exist.".format(user_id),
        )

    new_password = generate_password()
    hashed_password = get_password_hash(new_password)

    user.password = hashed_password
    db.commit()

    return {"username": user.username,
            "email": user.email,
            "fullname": user.fullname,
            "is_active": user.is_active,
            "new_password": new_password}


@user_router.post("/change_password", response_model=BaseUserSchema)
async def change_password(new_password: str, current_user: User = Depends(get_current_active_user)):
    """
    Change password of the current user.

    :str new_password: new password\\
    :return user
    """
    if len(new_password) < MINIMAL_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Your Password is too short. Please choose a password with at least {} characters".format(MINIMAL_PASSWORD_LENGTH),
        )

    hashed_password = get_password_hash(new_password)
    current_user.password = hashed_password
    db.commit()

    return current_user


@user_router.post("/{user_id}/roles", response_model=UserWithRole)
async def make_user_admin(user_id: int, new_role: NewRole, current_user: User = Depends(get_current_active_admin)):
    """
    Change status of another user to admin

    :int user_id: Id of User to be made admin
    :return user and its new role
    """
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The User {} does not exist.".format(user_id),
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="The User {} is not active. Please activate the user first".format(user_id),
        )

    if 'admin' in user.roles:
        can_disable_admin(user)

    user.roles = new_role.roles
    db.commit()

    user = get_user_by_id(user_id)
    return user


@user_router.post("/{user_id}/change_data", response_model=BaseUserSchema)
async def change_user_data(user_id: int,
                           current_user: User = Depends(get_current_active_admin),
                           username: Optional[str] = None,
                           fullname: Optional[str] = None,
                           email: Optional[str] = None):
    """
    Change data for a user. Changeable data includes username, fullname and email, or a combination of them.

    :int user_id: user_id of user whose data is to be changed\\
    :str username: Optional: new username for user with user_id\\
    :str fullname: Optional: new fullname for user with user_id\\
    :str email: Optional: new email for user with user_id\\
    :return user
    """
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The User {} does not exist.".format(user_id),
        )

    # change username
    if username:
        username_in_db = db.query(User).filter(User.username == username).count()
        if username_in_db:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="The username {} already exists. Please choose another username".format(username),
            )

        user.username = username

    # change fullname
    if fullname:
        user.fullname = fullname

    # change email
    if email:
        try:
            valid = validate_email(email, check_deliverability=False)
            email = valid.email
        except EmailNotValidError as e:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="The e-mail {} is not valid. Reason: {}".format(email, e),
            )
        user.email = email

    db.commit()

    user = get_user_by_id(user_id)
    return user
