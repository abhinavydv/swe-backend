from config import db
from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint


# TODO: change this to fit our requirements
class BookingRoom(db.Base):
    __tablename__ = "booking_rooms"

    booking_id = Column(Integer, ForeignKey("bookings.booking_id"), unique=True,nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.room_id"), unique=True,nullable=False)
    room_type = Column(Integer,nullable=False)
    number_of_rooms = Column(Integer, nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint('booking_id', 'room_id'),
    )
    