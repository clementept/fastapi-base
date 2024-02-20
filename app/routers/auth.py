from datetime import UTC, datetime

import pytz
from fastapi import APIRouter, Cookie, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.models.user import UserModel
from app.schemas.login import LoginResponseSchema, RefreshAccessTokenResponseSchema

from ..backend import database
from ..services import crypto, oauth2

router = APIRouter(tags=["Auth"])


@router.post("/login", response_model=LoginResponseSchema)
async def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):
    user = (
        db.query(UserModel).filter(UserModel.email == user_credentials.username).first()
    )

    if not user or not crypto.verify_hash(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is not active"
        )

    access_token = oauth2.create_access_token(data={"user_id": user.id})
    refresh_token = oauth2.create_refresh_token(db, user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/login/refresh", response_model=RefreshAccessTokenResponseSchema)
async def refresh(
    refresh_token: str = Cookie(None),
    db: Session = Depends(database.get_db),
):
    exception = HTTPException(status_code=401, detail="Invalid refresh token")

    token_hash = str(hash(str(refresh_token)))

    user = db.query(UserModel).filter(UserModel.refresh_token == token_hash).first()

    if not user:
        raise exception

    token_expire_object = datetime.fromisoformat(user.refresh_token_expires)
    token_expire_utc = token_expire_object.replace(tzinfo=pytz.utc)

    if token_hash != user.refresh_token or token_expire_utc <= datetime.now(UTC):
        raise exception

    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}
