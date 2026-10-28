from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    display_name: str
    xp: int
    level: int
    xp_into_level: int
    xp_per_level: int
    created_at: datetime


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    username: str = Field(pattern=r"^[A-Za-z0-9_]{3,20}$")
    display_name: str = Field(min_length=2, max_length=40)
    password: str = Field(min_length=8, max_length=72)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return value.lower()

    @field_validator("display_name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) < 2:
            raise ValueError("Display name is too short.")
        return cleaned

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        has_letter = any(character.isalpha() for character in value)
        has_digit = any(character.isdigit() for character in value)
        if not has_letter or not has_digit:
            raise ValueError("Password must include a letter and a number.")
        return value


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=1, max_length=72)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()
