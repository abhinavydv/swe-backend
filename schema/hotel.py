from config import db
from sqlalchemy import Column, Integer, String, ForeignKey


# TODO: change this to fit our requirements
class Hotel(db.Base):
    __tablename__ = "hotels"

    hotel_id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.user_id"), unique=True,nullable=False)
    hotel_name = Column(String, nullable=False)
    property_paper_path = Column(String)
    description = Column(String)
    pincode = Column(String, nullable=False)
    locality = Column(String)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    country = Column(String, nullable=False)
    amenities = Column(Integer, nullable=False)
    tag_list = Column(String)
