from config import db
from sqlalchemy import Column, Integer, String, ForeignKey


# TODO: change this to fit our requirements
class HotelPhoto(db.Base):
    __tablename__ = "hotel_photos"

    photo_id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id"), nullable=False)
    photo_url = Column(String, nullable=False)
 
    