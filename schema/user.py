from config import db
from sqlalchemy import Column, Integer, String


# TODO: change this to fit our requirements
class User(db.Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
