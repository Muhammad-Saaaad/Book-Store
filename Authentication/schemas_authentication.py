from pydantic import BaseModel
from typing import Literal
from fastapi import Form
from enum import Enum

class UserType(str, Enum):
    buyer = "buyer"
    seller = "seller"

class user_input(BaseModel):
    email : str
    username :str
    password :str
    user_type : UserType

    @classmethod
    def as_form(cls, email : str = Form(...) ,username: str = Form(...), password: str = Form(...), user_type: UserType = Form(...)):
        return cls(email = email , username=username, password=password, user_type=user_type)
    
class signUp_output(BaseModel):
    email : str
    username : str
    password : str
    user_type : str

    class Config:
        from_attributes = True