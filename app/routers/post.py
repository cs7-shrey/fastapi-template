from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils, oauth2
from ..database import get_db
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

# def get_post(id: int, db: Session = Depends(get_db), response_model=schemas.SocialMediaPostReponse, current_user: schemas.UserOut = Depends(oauth2.get_current_user)):
@router.get('/{id}')
def get_post(id: int, db: Session = Depends(get_db), current_user: schemas.UserOut = Depends(oauth2.get_current_user)):
    # post = find_post(id)
    results = db.query(models.Post, func.count(models.Vote.post_id)).join(models.Vote, models.Post.id == models.Vote.post_id,
    isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    # print(db.query(models.Post).filter(models.Post.id == id))      # this gives out a SQL query
    print(current_user.id)
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    post = {"Post": results[0].__dict__, "votes": results[1]} 
    print(results)
    return {"post_detail": post}

# @router.get('/', response_model=list[schemas.PostOut])
@router.get('/')
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0):
    posts_query = db.query(models.Post, func.count(models.Vote.post_id)).join(models.Vote, models.Post.id == models.Vote.post_id,
    isouter=True).group_by(models.Post.id).limit(limit).offset(skip)
    results = posts_query.all()
    # print(posts_query)
    # print(results[0])
    posts = [{"Post": i[0].__dict__, "votes": i[1]} for i in results]
    print(posts[0])
    return posts

# ______________________________________________________________________________________________________________________________
# creating a post request
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.SocialMediaPostReponse)                             # setting the default response status code to 201
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.UserOut = Depends(oauth2.get_current_user)):
    # using get_current_user as a dependency lets fastapi do the error handling for us
    # post = models.Post(title=new_post.title, content=new_post.content, published = new_post.published)
    new_post = models.Post(**post.dict(), owner_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post                                                                 # can't use double quotes inside here

# _________________________________________________________________________________________________________________________________
# creating a put request
@router.put('/{id}')
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), response_model=schemas.SocialMediaPostReponse, current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    reqd_post = post_query.first()
    if reqd_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    if not post_query.first().owner_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform the action")
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return {"data": post_query.first()}

#_____________________________________________________________________________________________________________________________________
# creating a delete request
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)                  # setting the default response status code to 204
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    if post_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    if not post_query.first().owner_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform the action")
    print(post_query)
    post_query.delete(synchronize_session=False)
    db.commit()
    return
