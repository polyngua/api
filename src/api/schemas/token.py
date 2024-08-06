from pydantic import BaseModel


class TokenOut(BaseModel):
    access_token: str
    token_type: str


class CookieTokenResponse(BaseModel):
    success: bool
