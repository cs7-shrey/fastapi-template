from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional 
from random import randrange
import psycopg
from psycopg.rows import dict_row
# from psycopg_binary import RealDictCursor


app = FastAPI()           

# creating a class to validate input schema
class SocialMediaPost(BaseModel):
    title: str
    content: str
    published: bool=True

try:
    conn = psycopg.connect("dbname=fastapi user=postgres password=shrey@32200227", row_factory=dict_row)
    cursor = conn.cursor()
    print("Database connection was successful")
except Exception as e:
    print("An exception occured", e)


# ___________________________________________________________________________________________________________________________

# creating a decorator that turns root function into an API endpoint respoindint to GET requests at the root path
@app.get('/')      
def root():
    return {"message": "Hello, World"}                                                                     # returning a JSON response   

@app.get('/posts/{id}')
def get_post(id: int, response: Response):
    # post = find_post(id)
    post = cursor.execute("""SELECT * FROM posts WHERE id = %s""", (id,)).fetchall()
    if not post:
        # response.status_code = 404
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"post with id: {id} was not found"}
        # instead of doing what's all above, we raise an HTTP exception
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    print(post)
    return {"post_detail": post}

@app.get('/posts')
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    print(posts)
    return {"data": posts}

# ______________________________________________________________________________________________________________________________
# creating a post request
@app.post("/posts", status_code=status.HTTP_201_CREATED)                             # setting the default response status code to 201
def create_posts(new_post: SocialMediaPost):
    print(post_dict)
    post_success = cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", 
    (new_post.title, new_post.content, new_post.published)).fetchone()
    conn.commit()   
    print(post_success)
    return {"data": post_success}                                                                   # can't use double quotes inside here
# problem: the user can send whatever data they want

# _________________________________________________________________________________________________________________________________
# creating a put request
@app.put('/posts/{id}')
def update_post(id: int, post: SocialMediaPost):
    updated_post = cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
     (post.title, post.content, post.published, id)).fetchone()
    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    conn.commit()
    return {"data": updated_post}

#_____________________________________________________________________________________________________________________________________
# creating a delete request
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)                  # setting the default response status code to 204
def delete_post(id: int):
    deleted_post = cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (id, )).fetchone()
    if delete_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    conn.commit()
    return