from pydantic import BaseModel, Field
from typing import Optional
from enums.roles import Roles

class TestUser(BaseModel):
    email: str = Field(..., min_length=3)
    fullName: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8, max_length=20)
    passwordRepeat: str = Field(..., min_length=8, max_length=20)
    roles: list[Roles]
    verified: Optional[bool] = None
    banned: Optional[bool] = None
