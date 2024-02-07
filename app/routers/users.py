from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.services import oauth2
from ..backend import database
from app.models.user import UserModel
from app.schemas.user import UserCreateSchema, UserResponseSchema

from ..services import crypto

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserResponseSchema)
def create_user(user: UserCreateSchema, db: Session = Depends(database.get_db)):
    hashed_password = crypto.create_hash(user.password)
    user.password = hashed_password

    new_user = UserModel(**user.model_dump())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/me", response_model=UserResponseSchema)
def me(current_user: int = Depends(oauth2.get_current_user)):
    print(current_user)
    return current_user


@router.get("/{id}", response_model=UserResponseSchema)
def get_user(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    user = db.query(UserModel).filter(UserModel.id == id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found"
        )

    return user
