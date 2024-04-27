from fastapi import APIRouter, Depends
# from config.gdrive import create_file, delete_file
from config.cloudinary import upload_file, delete_file
from fastapi import UploadFile,File
from models.misc import FileID
from routers.user import get_logged_user
from schema.uploaded_file import UploadedFile
from sqlalchemy import insert, delete
from sqlalchemy.orm import Session
from config.db import get_db
import tempfile
import os
import traceback


router = APIRouter(
    prefix="/misc",
    tags=["misc"],
)


@router.post('/upload_file')
def upload_file_api(file: UploadFile=File(), user=Depends(get_logged_user), db: Session = Depends(get_db)):
    try:
        if user["status"] == "Error":
            print("user not logged in")
            return {"status": "Error", "message": "user not logged in", "alert": True}
        
        user = user["user"]

        tmp = tempfile.mktemp()
        with open(tmp, "wb") as buffer:
            buffer.write(file.file.read())

        file_url = upload_file(tmp)

        os.remove(tmp)

        stmt = insert(UploadedFile).values(file_id=file_url, owner_id=user.user_id)
        db.execute(stmt)
        db.commit()

        return {"status": "OK", "message": "file uploaded successfully", "alert": False, "url": file_url}
    except Exception as e:
        traceback.print_exc()
        return {"status": "Error", "message": str(e), "alert": True}

@router.post("/delete_file")
def delete_file_api(file_id: FileID, user=Depends(get_logged_user), db: Session = Depends(get_db)):
    try:
        if "user" not in user:
            return {"status": "Error", "message": "user not logged in", "alert": True}
        user = user["user"]

        file = db.query(UploadedFile).filter(UploadedFile.file_id == file_id.file_id).first()
        if not file:
            return {"status": "Error", "message": "file not found", "alert": True}

        if file.owner_id != user.user_id:
            return {"status": "Error", "message": "you are not the owner of this file", "alert": True}

        delete_file(file_id.file_id)

        stmt = delete(UploadedFile).where(UploadedFile.file_id == file_id.file_id)
        db.execute(stmt)
        db.commit()

        return {"status": "OK", "message": "file deleted successfully", "alert": False}
    except Exception as e:
        return {"status": "Error", "message": str(e), "alert": True}

