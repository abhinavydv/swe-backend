from config import db
from sqlalchemy import Column, Integer, String, ForeignKey


# TODO: change this to fit our requirements
class KYP(db.Base):
    __tablename__ = "kyp"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True,nullable=False)
    pan_number = Column(String)
    aadhar_number = Column(String)
    aadhar_photo_path = Column(String)
    hotelling_license = Column(String)
    account_number = Column(String)
    ifsc_code = Column(String)
    