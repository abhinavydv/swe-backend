from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os


load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SWESession = sessionmaker(autocommit=False, autoflush=True, bind=engine)

Base = declarative_base()

def get_db():
    db = SWESession()
    try:
        yield db
    finally:
        db.close()
