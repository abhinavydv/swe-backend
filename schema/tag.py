from config import db
from sqlalchemy import Column, Integer, String


# TODO: change this to fit our requirements
class Tag(db.Base):
    __tablename__ = "tags"

    tag_id = Column(Integer, primary_key=True, index=True)
    tag_name = Column(String,nullable=False)

    
