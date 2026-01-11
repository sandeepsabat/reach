#validators.py
from pydantic import BaseModel, EmailStr, constr
from typing import Optional

class RegisterModel(BaseModel):
    name: constr(min_length=1, max_length=100)
    email: EmailStr
    password: constr(min_length=6)
    role:constr(min_length=1, max_length=100)

class LoginModel(BaseModel):
    email: EmailStr
    password: constr(min_length=1)

class UpdateModel(BaseModel):
    name: Optional[constr(min_length=1, max_length=100)] = None
    email: Optional[EmailStr] = None
    password: Optional[constr(min_length=6)] = None
    role:constr(min_length=1, max_length=100) = None
