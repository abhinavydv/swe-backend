from config import db
from sqlalchemy import Column, Integer, String


# TODO: change this to fit our requirements
class User(db.Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    dob = Column(String)
    phone_number = Column(String)
    gender = Column(String)
    nationality = Column(String)
    password = Column(String)
    salt = Column(String)
    role = Column(String)   # customer or partner
    profile_image_path = Column(String)
    cookie = Column(String)
