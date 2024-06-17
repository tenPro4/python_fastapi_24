from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response,status
from fastapi.security import OAuth2PasswordRequestForm

from app import utils

from .. import models,schemas,oauth2
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    tags=["Authentication"]
)

@router.post("/login")
def login(credential:OAuth2PasswordRequestForm = Depends(),db:Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.email ==credential.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid credential")
    
    if not utils.verify(credential.password,user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid credential")
    

    token = oauth2.create_access_token(data = {"user_id":user.id})

    return {"access_token":token,"token_type":"bearer"}
