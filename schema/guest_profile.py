from config import db
from sqlalchemy import Column, Integer, String, ForeignKey


# TODO: change this to fit our requirements
class GuestProfile(db.Base):
    __tablename__ = "guest_profiles"

    guest_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True,nullable=False)
    guest_name = Column(String, nullable=False)
    age = Column(Integer)
    gender = Column(String)
    