from config import db
from sqlalchemy import Column, Integer, Float, Date, ForeignKey


# TODO: change this to fit our requirements
class Booking(db.Base):
    __tablename__ = "bookings"

    booking_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True,nullable=False)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id"), unique=True,nullable=False)
    amount = Column(Float, nullable=False)
    from_date = Column(Date,nullable=False)
    to_date = Column(Date,nullable=False)
    room_type = Column(Integer, nullable=False)
    number_of_rooms = Column(Integer,default=1)
    status = Column(Integer)
    transaction_id  = Column(Integer)

    