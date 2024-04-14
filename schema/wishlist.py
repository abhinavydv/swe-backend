from config import db
from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint


# TODO: change this to fit our requirements
class Wishlist(db.Base):
    __tablename__ = "wishlist"

    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id"), unique=True,nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True,nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint('hotel_id', 'user_id'),
    )
    