from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from ..models.user import UserRole


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    role: UserRole
    empleado_id: Optional[int] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None
    empleado_id: Optional[int] = None
    active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole
    empleado_id: Optional[int] = None
    active: bool
    password_changed: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class ResetPasswordRequest(BaseModel):
    user_id: int
    new_password: str = Field(..., min_length=8)
