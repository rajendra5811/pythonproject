from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    name: str
    age: int
    phone: str

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int

class UpdateUser():
    name: Optional[str] = None
    age: Optional[int] = None
    phone: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
        