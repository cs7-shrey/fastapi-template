from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.middleware import Middleware

# from sqlalchemy.orm import Session
from . import models
from .database import engine
from .routers import post, user, auth, vote

# models.Base.metadata.create_all(bind=engine)                                                # creates database tables if they don't exist
app = FastAPI()           

app.include_router(post.router)                                                                 # importing all of the routes from post
app.include_router(user.router)                                                                 # importing all of the routes from users
app.include_router(auth.router)                                                                 # importing all of the routes from auth
app.include_router(vote.router)

# creating a decorator that turns root function into an API endpoint respoindint to GET requests at the root path
@app.get('/')      
def root():
    return {"message": "Hello, World"}                                                                     # returning a JSON response   

