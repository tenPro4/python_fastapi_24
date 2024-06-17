from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer
import jwt

from app import models
from . import database
from sqlalchemy.orm import Session

from app.schemas import TokenData, UserResponse
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db:Session = Depends(database.get_db)
    ):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    ),

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except jwt.InvalidTokenError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == token_data.user_id).first()

    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    return current_user