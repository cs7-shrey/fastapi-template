from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional 
from random import randrange
import psycopg
from psycopg.rows import dict_row
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()           

# creating a class to validate input schema


# ___________________________________________________________________________________________________________________________

# creating a decorator that turns root function into an API endpoint respoindint to GET requests at the root path
@app.get('/')      
def root():
    return {"message": "Hello, World"}                                                                     # returning a JSON response   

@app.get('/posts/{id}')
def get_post(id: int, db: Session = Depends(get_db), response_model=schemas.SocialMediaPostReponse):
    # post = find_post(id)
    post = db.query(models.Post).filter(models.Post.id == id).first()
    print(db.query(models.Post).filter(models.Post.id == id))      # this gives out a SQL query
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    print(post)
    return {"post_detail": post}

@app.get('/posts', response_model=list[schemas.SocialMediaPostReponse])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    print(posts)
    return posts

# ______________________________________________________________________________________________________________________________
# creating a post request
@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.SocialMediaPostReponse)                             # setting the default response status code to 201
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # post = models.Post(title=new_post.title, content=new_post.content, published = new_post.published)
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post                                                                 # can't use double quotes inside here

# _________________________________________________________________________________________________________________________________
# creating a put request
@app.put('/posts/{id}')
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), response_model=schemas.SocialMediaPostReponse):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    reqd_post = post_query.first()
    if reqd_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    conn.commit()
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return {"data": post_query.first()}

#_____________________________________________________________________________________________________________________________________
# creating a delete request
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)                  # setting the default response status code to 204
def delete_post(id: int, db: Session = Depends(get_db)):
    # deleted_post = cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (id, )).fetchone()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    if post_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    print(post_query)
    post_query.delete(synchronize_session=False)
    db.commit()
    return

# -----------------------------------------------------------------------------------------------------------------------------------

@app.post('/users', status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # hash the password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()        
    db.refresh(new_user)          # gets data from db and stores it into new_user variable, not needed when response_model specified
    return new_user

@app.get('/users/{id}', response_model=schemas.UserOut)
def get_(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} does not exist")
    return user