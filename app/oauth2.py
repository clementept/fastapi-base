from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth_token import TokenData

from . import database
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.jwt_secret_key
ALGORYTHM = settings.jwt_algorythm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_access_token_expire_minutes


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

        token_data = TokenData(id=str(id))
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

    user = db.query(User).filter(User.id == token.id).first()

    return user
