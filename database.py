from sqlalchemy import create_engine
from sqlalchemy.orm import create_session , Session
from sqlalchemy.ext.declarative import declarative_base
from fastapi import Depends
from typing import Annotated


engine = create_engine('postgresql://postgres:admin123@localhost:5432/Book-Store')

session_local = create_session(bind=engine , autocommit=False , autoflush=False)

base = declarative_base()

def get_db(): # generative function
    db = session_local

    try:
        yield db
    finally:
        db.close_all()


db_dependency = Annotated[Session , Depends(get_db)]