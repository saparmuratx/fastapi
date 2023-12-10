import time
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.params import Body

from sqlalchemy.orm import Session
from pydantic import BaseModel

import psycopg2
from psycopg2.extras import RealDictCursor

from icecream import ic

from .database import engine, get_db
from . import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


my_posts = [
    {
        "id": 0,
        "title": "default title",
        "content": "offensive content",
        "published": False,
        "rating": None,
    }
]

while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fastapi",
            user="altair",
            password="tobehonest",
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        ic("Connection to POSTGRES DATABASE successfull!")
        break
    except Exception as e:
        ic("connection to database failed")
        print(f"Error was: {e}")
        time.sleep(2)


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.get("/posts/{id}")
async def get_post(id: int, response: Response):
    select_one = "select * from posts where id = %s"

    cursor.execute(select_one, (id,))

    data = cursor.fetchone()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found!",
        )

    return {"data": data}


@app.get("/posts")
async def get_posts():
    try:
        select_all = "select * from posts where published = true"
        cursor.execute(select_all)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return {"data": cursor.fetchall()}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post):
    insert_query = (
        "insert into posts(title, content, published) values (%s, %s, %s) returning *"
    )

    cursor.execute(
        insert_query,
        (post.title, post.content, post.published),
    )

    data = cursor.fetchone()

    conn.commit()

    return {"data": data}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    delete_query = "delete from posts where id = %s returning *"

    cursor.execute(delete_query, (id,))

    data = cursor.fetchone()

    conn.commit()

    # ic(data)

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found!",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
async def update_post(id: int, post: Post):
    update_query = "update posts set title = %s, content = %s, published = %s where id = %s returning *"

    cursor.execute(
        update_query,
        (post.title, post.content, post.published, id),
    )

    data = cursor.fetchone()

    conn.commit()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found!",
        )

    return {"data": data}


@app.get("/sqlalchemy")
async def test(db: Session = Depends(get_db)):
    pass
