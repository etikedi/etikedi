from datetime import timedelta
from typing import List

from email_validator import validate_email, EmailNotValidError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..config import ACCESS_TOKEN_EXPIRE_MINUTES, app, db, MINIMAL_PASSWORD_LENGTH
from ..models import User, Token, UserNewPW, BaseUserSchema, BaseUserWithIDSchema
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


@user_router.get("", response_model=List[BaseUserWithIDSchema])
async def get_all_users(current_user: User = Depends(get_current_active_user)):
    return db.query(User).all()


@user_router.get("/me", response_model=BaseUserWithIDSchema)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@user_router.post("", response_model=UserNewPW)
async def add_user(dto: BaseUserSchema, current_user: User = Depends(get_current_active_admin)):
    """
    Add new user. New user is automatically set active and as role worker. A random password is assigned.

    :str full_name: Optional: full name of the user \\
    :str email: email for user, needs to follow email format\\
    :str username: intended username for new user\\
    :return User and random PW in cleartext
    """
    users = db.query(User).filter(User.username == dto.username).count()
    if users > 0:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="The user name {} already exists. Choose another username!".format(dto.username),
        )

    try:
        validate_email(dto.email, check_deliverability=False)
    except EmailNotValidError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="The e-mail {} is not valid. Reason: {}".format(dto.email, e),
        )

    # set random PW
    password = generate_password()
    hashed_password = get_password_hash(password)

    # automatically active and worker
    new_user = User(
        username=dto.username,
        email=dto.email,
        roles=dto.roles,
        password=hashed_password,
        fullname=dto.fullname
    )
    db.add(new_user)
    db.commit()

    new_user.new_password = password
    return new_user


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
    user.new_password = new_password

    return user


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
            detail="Your Password is too short. Please choose a password with at least {} characters".format(
                MINIMAL_PASSWORD_LENGTH),
        )

    current_user.password = get_password_hash(new_password)
    db.commit()

    return current_user


@user_router.put("/{user_id}", response_model=BaseUserSchema)
async def change_user_data(user_id: int,
                           dto: BaseUserSchema,
                           current_user: User = Depends(get_current_active_admin)):
    """
    Changes user data, activation status or roles of user with user id.

    :str user_id: id of the user whose data is to be changed\\
    :str username: \\
    :str email: \\
    :str fullname: \\
    :bool is_active: \\
    :str new_role: role or new role to be set, Parameter in Request Body
    """
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The User {} does not exist.".format(user_id),
        )

    # Change activation status
    if user.is_active != dto.is_active:
        if not dto.is_active and 'admin' in user.roles:
            can_disable_admin(user)

        user.is_active = dto.is_active

    # Change status of another user to new role
    if user.roles != dto.roles:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="The User {} is not active. Please activate the user first".format(user_id),
            )

        if 'admin' in user.roles:
            can_disable_admin(user)

        user.roles = dto.roles

    # Change username
    if user.username != dto.username:
        username_in_db = db.query(User).filter(User.username == dto.username).count()
        if username_in_db:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="The username {} already exists. Please choose another username".format(dto.username),
            )

        user.username = dto.username

    # Change fullname
    if dto.fullname:
        user.fullname = dto.fullname

    # Change email
    if dto.email is not None and user.email != dto.email:
        try:
            valid = validate_email(dto.email, check_deliverability=False)
            user.email = valid.email
        except EmailNotValidError as e:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="The e-mail {} is not valid. Reason: {}".format(dto.email, e),
            )

    db.commit()

    return get_user_by_id(user_id)
