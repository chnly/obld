import utils

from users.main import get_users
from users.models import User

from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt

from users.utils import pwd_context

app_token = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


oauth2_schema = OAuth2PasswordBearer(tokenUrl="/token")


def verity_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def jwt_get_user(db, username: str):
    for user in db:
        if username in user.username:
            return user


def jwt_authenticate_user(db, username: str, password: str):
    user = jwt_get_user(db=db, username=username)
    if not user:
        return False
    if not verity_password(plain_password=password, hashed_password=user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(claims=to_encode,
                             key=utils.config['token']['SECRET_KEY'],
                             algorithm=utils.config['token']['ALGORITHM'])
    return encoded_jwt


@app_token.post("/", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = jwt_authenticate_user(db=get_users(), username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=utils.config['token']['ACCESS_TOKEN_EXPIRE_MINUTES'])
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def jwt_get_current_user(token: str = Depends(oauth2_schema)):
    credentials_exception = HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token=token,
                             key=utils.config['token']['SECRET_KEY'],
                             algorithms=utils.config['token']['ALGORITHM'])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = jwt_get_user(db=get_users(), username=username)
    if user is None:
        raise credentials_exception
    del user.hashed_password
    return user


@app_token.get("/me")
async def jwt_read_users_me(current_user: User = Depends(jwt_get_current_user)):
    return current_user
