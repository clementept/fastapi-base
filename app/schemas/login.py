from pydantic import BaseModel


class LoginResponseSchema(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class RefreshAccessTokenResponseSchema(BaseModel):
    access_token: str
    token_type: str
