from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.models.user import UserModel
from app.schemas.login import LoginResponseSchema

from .. import crypto, database, oauth2

router = APIRouter(tags=["Auth"])


@router.post("/login", response_model=LoginResponseSchema)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):
    user = (
        db.query(UserModel).filter(UserModel.email == user_credentials.username).first()
    )

    exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials"
    )

    if not user or not crypto.verify_hash(user_credentials.password, user.password):
        raise exception

    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}
