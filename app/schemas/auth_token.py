from typing import Optional

from pydantic import BaseModel


class TokenDataSchema(BaseModel):
    id: Optional[str] = None
