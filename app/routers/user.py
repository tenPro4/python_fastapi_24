from fastapi import Depends, HTTPException, status,APIRouter

from .. import models,schemas,utils
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.UserResponse)
def create_user(user:schemas.UserCreate,db: Session = Depends(get_db)):
    new_user = models.User(**user.model_dump())

    hashed_pass = utils.hash(user.password)
    new_user.password = hashed_pass

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/{id}",response_model=schemas.UserResponse)
def get_postById(id:int,db: Session = Depends(get_db)):
    # new_post = models.Post(title=post.title,content=post.content,published=post.published)
    
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='user no found')

    return user
