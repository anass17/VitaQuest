from pydantic import BaseModel, EmailStr, Field
from typing import Literal


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters"
    )


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    first_name: str
    last_name: str
    role: Literal["USER", "ADMIN"]
