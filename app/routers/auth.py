from datetime import UTC, datetime, timedelta

import pytz
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.backend.config import settings
from app.models.user import UserModel
from app.schemas.login import LoginResponseSchema

from ..backend import database
from ..services import crypto, oauth2

router = APIRouter(tags=["Auth"])


def getRoles(user):
    roles = ["user"]
    if user.is_admin:
        roles.append("admin")

    return roles


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

    access_token = oauth2.create_access_token(
        data={"user_id": user.id, "roles": getRoles(user)}
    )
    refresh_token = oauth2.create_refresh_token(db, user.id)

    content = {
        "access_token": access_token,
        "token_type": "bearer",
    }

    cookie_expire = datetime.now(UTC) + timedelta(
        minutes=settings.jwt_refresh_token_expire_minutes
    )

    response = JSONResponse(content=content)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        expires=cookie_expire,
        secure=True,
    )

    return response


@router.get("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    db: Session = Depends(database.get_db),
):
    response.status_code = status.HTTP_204_NO_CONTENT
    response.delete_cookie(
        key="refresh_token", secure=True, samesite=None, httponly=True
    )

    cookies = request.cookies
    refresh_token = cookies.get("refresh_token")

    if not refresh_token:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    token_hash = str(hash(str(refresh_token)))

    user = db.query(UserModel).filter(UserModel.refresh_token == token_hash).first()

    if not user:
        return response

    user.refresh_token = None
    user.refresh_token_expires = None

    db.commit()

    return response


@router.get("/login/refresh", response_model=LoginResponseSchema)
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
        print(f"token_hash: {token_hash} != user token_hash {user.refresh_token}")
        print(f"Expired? {token_expire_utc <= datetime.now(UTC)}")
        raise exception

    access_token = oauth2.create_access_token(
        data={"user_id": user.id, "roles": getRoles(user)}
    )

    return {"access_token": access_token, "token_type": "bearer"}
