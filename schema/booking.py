from config import db
from sqlalchemy import Column, Integer, Float, Date, ForeignKey


# TODO: change this to fit our requirements
class Booking(db.Base):
    __tablename__ = "bookings"

    booking_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id"), nullable=False)
    amount = Column(Float, nullable=False)
    from_date = Column(Date,nullable=False)
    to_date = Column(Date,nullable=False)
    status = Column(Integer)   # -1 - cancel, 0 - booked, 1 - staying, 2 - completed
    transaction_id  = Column(Integer)

