from config import db
from sqlalchemy import Column, Integer, String, ForeignKey


# TODO: change this to fit our requirements
class Review(db.Base):
    __tablename__ = "reviews"

    review_id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.booking_id"), unique=True,nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True,nullable=False)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id"), unique=True,nullable=False)
    title = Column(String)
    description = Column(String)
    rating = Column(Integer)
    
