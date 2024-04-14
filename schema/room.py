from config import db
from sqlalchemy import Column, Integer, Float, ForeignKey


# TODO: change this to fit our requirements
class Room(db.Base):
    __tablename__ = "rooms"

    room_id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id"), unique=True,nullable=False)
    room_type = Column(Integer, nullable=False)
    number_of_rooms = Column(Integer)
    price = Column(Float,nullable=False)
    amenities = Column(Integer)
    