from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response,status

from app import oauth2

from .. import models,schemas
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/vote",
    tags=["Votes"]
)

@router.get("/",response_model=List[schemas.Post_Response])
def get_posts(db: Session = Depends(get_db),limit:int = 10,skip:int =0,search:Optional[str]=""):
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).offset(skip).limit(limit).all()
    return posts

@router.get("/user/{id}",response_model=List[schemas.Post_Response])
def get_posts(id:int,db: Session = Depends(get_db)):
    posts = db.query(models.Post).filter(models.Post.owner_id == id).all()
    return posts

@router.get("/own",response_model=List[schemas.Post_Response])
def get_posts(db: Session = Depends(get_db),current_user:schemas.UserResponse =Depends(oauth2.get_current_active_user)):

    posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()
    return posts

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.Post_Response)
def create_vote(
                vote:schemas.Vote,
                db: Session = Depends(get_db),
                current_user:schemas.UserResponse =Depends(oauth2.get_current_active_user),
                ):
    
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {vote.post_id} does not exist")

    vote_query = db.query(models.Vote).filter(models.Vote.user_id == current_user.id, models.Vote.post_id == vote.post_id)

    found_vote = vote_query.first()

    if vote.dir == 1:
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="this post alredy voted")
        new_vote = models.Vote(user_id=current_user.id,post_id=vote.post_id)

        db.add(new_vote)
        db.commit()
        db.refresh(new_vote)
        return {"message":"vote successsfully"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="vote not found")
        
        vote_query.delete(synchronize_session=False)
        db.commit()

        return {"message":"vote delete successsfully"}

@router.get("/{id}",response_model=schemas.Post_Response)
def get_postById(id:int,db: Session = Depends(get_db)):
    # new_post = models.Post(title=post.title,content=post.content,published=post.published)
    
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='post no found')

    return post

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
                id:int,
                db: Session = Depends(get_db),
                current_user:schemas.UserResponse =Depends(oauth2.get_current_active_user)
                ):
    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='post no found')
    
    if post.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='unauthorized')
    
    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}")
def update_post(id:int,post:schemas.Post,db: Session = Depends(get_db),current_user:schemas.UserResponse =Depends(oauth2.get_current_active_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)

    exist_post = post_query.first()

    if exist_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='post no found')
    
    if exist_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='unauthorized')
    
    post_query.update(post.model_dump(),synchronize_session=False)

    db.commit()

    return post_query.first()
