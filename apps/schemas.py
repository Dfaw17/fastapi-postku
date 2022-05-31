from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr


class Account(BaseModel):
    name: str
    email: str
    pwd: str
    phone: str

    class Config:
        orm_mode = True
