from datetime import datetime
from pydantic import BaseModel,ConfigDict


class UserBase(BaseModel):
    employee_code: str
    user_name: str
    role: str
    is_active: bool = True


class UserCreate(UserBase):
    password:str


class UserUpdate(BaseModel):
    employee_code: str | None = None
    user_name: str | None = None
    role: str | None = None
    is_active: bool | None = None
    password:str | None=None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active:bool
    created_at: datetime    