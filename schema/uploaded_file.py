from config import db
from sqlalchemy import Column, Integer, String, ForeignKey


class UploadedFile(db.Base):
    __tablename__ = "uploaded_files"

    file_id = Column(String, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
