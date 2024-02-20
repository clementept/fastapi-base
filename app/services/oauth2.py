import random
import secrets
import string
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.models.user import UserModel
from app.schemas.auth_token import TokenDataSchema

from ..backend import database
from ..backend.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.jwt_secret_key
ALGORYTHM = settings.jwt_algorythm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_MINUTES = settings.jwt_refresh_token_expire_minutes


def create_refresh_token(db, user_id):
    rand_token = secrets.token_urlsafe(30)

    token_hash = str(hash(rand_token))

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    user.refresh_token = token_hash
    user.refresh_token_expires = datetime.now(UTC) + timedelta(
        minutes=REFRESH_TOKEN_EXPIRE_MINUTES
    )

    db.commit()
    db.refresh(user)

    return rand_token


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORYTHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORYTHM])
        id: int = payload.get("user_id")

        if id is None:
            raise credentials_exception

        token_data = TokenDataSchema(id=str(id))
    except JWTError:
        raise credentials_exception

    return token_data


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = verify_access_token(token, credentials_exception)

    user = db.query(UserModel).filter(UserModel.id == token.id).first()

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not active",
        )

    return user
