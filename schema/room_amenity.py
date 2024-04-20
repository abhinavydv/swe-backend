from config import db
from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint


# TODO: change this to fit our requirements
class RoomAmenity(db.Base):
    __tablename__ = "room_amenities"

    room_id = Column(Integer, ForeignKey("rooms.room_id"), unique=True,nullable=False)
    amenity = Column(String,nullable=False)
    quality = Column(String)  # good, bad

    __table_args__ = (
        PrimaryKeyConstraint('room_id', 'amenity'),
    )