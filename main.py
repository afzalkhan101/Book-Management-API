from fastapi import FastAPI, Depends, HTTPException, Query, Cookie
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import Book

Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_token_header(token: str = Query(...)):
    if token != "mysecret":
        raise HTTPException(status_code=403, detail="Invalid Token")
    return token

class CommonQueryParams:
    def __init__(self, skip: int = 0, limit: int = 10):
        self.skip = skip
        self.limit = limit

def query_extractor(q: str | None = None):
    return q

def query_or_cookie_extractor(
    q: str = Depends(query_extractor), last_query: str | None = Cookie(default=None)
):
    return q or last_query


@app.post("/books/", dependencies=[Depends(get_token_header)])
def create_book(title: str, author: str, db: Session = Depends(get_db)):
    book = Book(title=title, author=author)
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

@app.get("/books/")
def list_books(
    commons: CommonQueryParams = Depends(),
    db: Session = Depends(get_db),
    search: str = Depends(query_or_cookie_extractor)
):
    query = db.query(Book)
    if search:
        query = query.filter(Book.title.contains(search))
    books = query.offset(commons.skip).limit(commons.limit).all()
    return books
