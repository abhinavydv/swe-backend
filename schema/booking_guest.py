from config import db
from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint


# TODO: change this to fit our requirements
class BookingGuest(db.Base):
    __tablename__ = "booking_guests"

    booking_id = Column(Integer, ForeignKey("bookings.booking_id"), unique=True,nullable=False)
    guest_id = Column(Integer, ForeignKey("guests.guest_id"), unique=True,nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint('booking_id', 'guest_id'),
    )
    