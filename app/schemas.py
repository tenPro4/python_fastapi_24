import datetime
from pydantic import BaseModel, EmailStr

class UserResponse(BaseModel):
    id:int
    email:str
    created_at:datetime.datetime
    
    class Config:
        from_attributes = True

        
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class Post(BaseModel):
    id:int
    created_at:datetime.datetime
    title: str
    content: str
    published: bool = True
    owner_id:int
    owner: UserResponse

    class Config:
        from_attributes = True

class Post_Response(Post):
    pass

class PostJoinVoteRespond(BaseModel):
    Post:Post
    votes:int

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    password:str

class UserLogin(BaseModel):
    email:EmailStr
    password:str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int | None = None

class Vote(BaseModel):
    post_id:int
    dir: int