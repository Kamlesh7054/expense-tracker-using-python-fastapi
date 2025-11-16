from typing import Optional
from fastapi import FastAPI, HTTPException, status, responses, Response
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

class Post(BaseModel):
    title: str
    content: str
    published: bool = True # default value is true
    # rating: Optional[int] = None # optional field


while True:

    try:
        # connect to an existing database with a cursor that returns dictionary-like rows
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres',
                                password='1234', cursor_factory=RealDictCursor)
        cursor = conn.cursor() # create a cursor object to interact with the database
        print("Database connection was successfull")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error:", error)
        time.sleep(1)


app = FastAPI()
'''.get() is http method for retrieving data from a server. there are multiple http
 methods like post, put, delete etc
 -> and "/" is the path for the root endpoint of the api
 -> if there two root endpoints it will give first one only
 '''

# creating a list of posts as a sample database
my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1},
            {"title": "favorite food", "content": "I love burger", "id": 2}]

# Function to find a post by id; returns the post dictionary if found, otherwise None
def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p

@app.get("/") 
def read_root():
    return {"message" : "Welcome to xyz_social_app!!!!"}

@app.get("/posts")# this endpoint will return a list of posts
def get_posts():
    return {"data": my_posts}

# @app.post("/posts") # this endpoint will create a new post
# def create_post(post: Post):
#     # print(post.published)
#     # print(post.title)
#     # print(post.rating)
#     print(post)
#     print(post.dict())# to convert pydantic model to dictionary
#     return {"data": "new post"}

@app.post("/posts", status_code = status.HTTP_201_CREATED) # this endpoint will create a new post
def create_post(post: Post):
    post_dict = post.dict() # convert pydantic model to dictionary
    post_dict['id'] = randrange(0, 1000000) # generate a random id for the post
    my_posts.append(post_dict) # add the new post to the list of posts
    return {"data": post_dict} # return the newly created post


#retriving one individual post by id
@app.get("/posts/{id}") # path parameter
def get_post(id: int):
    post = find_post(id)
    if not post:
        #handle error if post not found using HTTPException; 
        # you should import HTTPException and status from fastapi
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT) # delete a post by id
def delete_post(id: int):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    my_posts.remove(post)
    # return {"message": "post deleted successfully"}
    return Response(status_code=status.HTTP_204_NO_CONTENT) # no content to return

def find_post_index(id):
    """
    Returns the index of the post with the given id in my_posts, or None if not found.
    """
    for index, p in enumerate(my_posts):
        if p['id'] == id:
            return index
    return None

@app.put("/posts/{id}") # update a post by id
def update_post(id: int, post: Post):
    index = find_post_index(id)
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"post with id: {id} does not exist") 
    post_dict = post.dict()
    post_dict['id'] = id
    my_posts[index] = post_dict
    return {"data": post_dict}
    
