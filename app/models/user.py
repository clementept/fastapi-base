from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String
from sqlalchemy.sql.expression import false, func, null

from ..backend.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=false())
    activation_code = Column(String, nullable=True, server_default=null())
    refresh_token = Column(String, nullable=True)
    refresh_token_expires = Column(String, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=func.now())
