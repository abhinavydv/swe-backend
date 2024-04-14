from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.db import get_db
from models import user
from schema.user import User as UserTable


router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/login")
def login():
    pass

@router.post("/register")
def register(user: user.User, db: Session = Depends(get_db)):
    print(user)
    u = UserTable(fisrt_name=user.first_name,last_name=user.last_name, email=user.email, password=user.password, profile_img = user.profile_img)
    # Hash password and add password and salt separately
    db.add(u)
    db.commit()
    db.refresh(u)

    return {"status": "successfully registered user"}

@router.get("/login")
def get_logged_user():
    pass

@router.get("/logout")
def logout():
    pass
