from pydantic import BaseModel, Field, field_validator, ValidationError, EmailStr
from email_validator import validate_email
from typing import List, Optional
from datetime import timedelta


class CreateTask(BaseModel):
    title: str
    description: str
    priority: int
    tag_ids: List[int] = []


class CreateUser(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str
    is_admin: bool = False

    @field_validator('email')
    def validate_email(cls, v):
        try:
            validate_email(v)
            return v
        except ValidationError:
            raise ValidationError('Email must be unique.')



class TaskBase(BaseModel):
    id: int
    title: str
    description: str
    priority: int
    complete: bool
    owner_id: int

class TagBase(BaseModel):
    id: int
    name: str

class TagSchema(TagBase):
    tasks: List[TaskBase]
class UserBase(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
class TaskSchema(TaskBase):
    owner: UserBase
    tags: List[TagBase]

class UserSchema(UserBase):
    tasks: List[TaskBase]

class UpdateTask(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    complete: Optional[bool] = None
    tag_ids: Optional[List[int]] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    id: int
    username: str
    email: str

class UpdateUser(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_admin: Optional[bool] = None
    password: Optional[str] = None

class RefreshRequest(BaseModel):
    refresh_token: str

class CreateUpdateTag(BaseModel):
    name: str

