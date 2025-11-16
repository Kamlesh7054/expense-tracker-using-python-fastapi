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
        time.sleep(2)


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
    cursor.execute("""select * from posts""")# execute the SQL query to fetch all posts but not storing the result
    posts = cursor.fetchall() # fetch all the results from the executed query
    # print(posts)
    return {"data": posts}

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
    cursor.execute("""insert into posts (title, content, published) values(%s, %s, %s) returning *""",
                    (post.title, post.content, post.published))
    new_post = cursor.fetchone() # fetch the newly created post
    conn.commit() # commit the transaction to save changes to the database
    return {"data": new_post} # return the newly created post


#retriving one individual post by id
@app.get("/posts/{id}") # path parameter
def get_post(id: int):
    cursor.execute("""select * from posts where id = %s""", (str(id))) # execute the SQL query to fetch post by id
    post = cursor.fetchone() # fetch the result from the executed query
    if not post:
        #handle error if post not found using HTTPException; 
        # you should import HTTPException and status from fastapi
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT) # delete a post by id
def delete_post(id: int):
    cursor.execute("""delete from posts where id = %s returning *""", (str(id)))
    delete_post = cursor.fetchone()
    conn.commit()

    if delete_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} does not exist")
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
    cursor.execute("""update posts set title = %s, content = %s, published = %s where id = %s
                   returning *""", (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"post with id: {id} does not exist") 
    
    return {"data": updated_post}
    
