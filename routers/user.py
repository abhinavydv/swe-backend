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
    u = UserTable(name=user.name, email=user.email, password=user.password)
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
