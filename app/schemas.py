# defines schemas for request/response validation
from pydantic import BaseModel, EmailStr
from datetime import datetime
from pydantic.types import conint
from typing_extensions import TypedDict


class SocialMediaPost(BaseModel):
    title: str
    content: str
    published: bool=True

# class CreatePost(BaseModel):
#     title: str
#     content: str
#     published: bool = True

# class UpdatePost(BaseModel):
#     title: str
#     content: str
#     published: bool

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    
class SocialMediaPostReponse(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut
    votes: int

class PostOut(BaseModel):
    # send out a dictionary with the following fields
    dict['Post': SocialMediaPost, 'votes': int]
    
    # remove any of the fields which you don't want to send back
    
    # not needed anymore
    # class Config:
    #     from_attributes = True         # writing this for pydantic to sqlalchemy models instead of dictionaries

# _____________________________________________________________________________________________________________________________-

class UserCreate(BaseModel):
    email: EmailStr
    password: str


    # class Config /\ not needed

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int | None = None

class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)