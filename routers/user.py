from fastapi import APIRouter, Depends, Response, Cookie
from sqlalchemy import update
from sqlalchemy.orm import Session
from config.db import get_db
from models import user
from schema.user import User as UserTable
import hashlib
import secrets


router = APIRouter(
    prefix="/users",
    tags=["users"],
)

def generate_cookie(user_id, email_id):
    secret = secrets.token_bytes(256)
    return hashlib.sha256(secret+str(user_id).encode()+str(email_id).encode()).hexdigest()

@router.post("/login")
def login(res: Response,login_req: user.LoginRequest, db: Session = Depends(get_db)):
    u = db.query(UserTable).filter(UserTable.email_id == login_req.email).first()

    if not u:
        return {"error": "email id doesn't exist"}

    hashed_password = hashlib.sha256((login_req.password + u.salt).encode()).hexdigest()

    # Compare the newly hashed password with the stored hashed password
    if hashed_password == u.password:
        cookie = generate_cookie(u.user_id, u.email_id)
        res.set_cookie(
            key='auth',
            value=cookie,
            max_age=1000 * 60 * 60 * 24,
            httponly=True
        )
        u.cookie = cookie
        stmt = update(UserTable).where(UserTable.user_id == u.user_id).values(cookie=cookie)
        db.execute(stmt)
        db.commit()

        return {"status": "login successful"}

    else:
        return {"error": "incorrect password"}


@router.post("/register")
def register(user: user.User, db: Session = Depends(get_db)):

    if db.query(UserTable).filter(UserTable.email_id == user.email).first():
        return {"error": "user already exists"}

    ## Email verification left

    # Generate a random salt
    salt = secrets.token_hex(16)  # Generate a 16-byte salt (32 characters when represented in hexadecimal)

    # Concatenate the password and salt
    hashed_password = hashlib.sha256((user.password + salt).encode()).hexdigest()

    u = UserTable(
        first_name=user.first_name,
        last_name=user.last_name, 
        email_id=user.email, 
        password=hashed_password,
        salt=salt,
        role=user.role,
        profile_image_path = user.profile_img    # Left - Store the actual image in file system 
    )

    cookie = generate_cookie(u.user_id, u.email_id)
    u.cookie = cookie

    db.add(u)
    db.commit()
    db.refresh(u)

    return {"status": "successfully registered user"}

@router.get("/logged_customer")
def get_logged_user(auth: str = Cookie(None), db: Session = Depends(get_db)):
    if auth is None:
        return {"error": "user not logged in"}   # Redirect to login

    u = db.query(UserTable).filter(UserTable.cookie == auth and UserTable.role == "customer").first()
    if not u:
        return {"error": "user not found"}
    
    return u

@router.get('/logged_partner')
def get_logged_partner(auth: str = Cookie(None), db: Session = Depends(get_db)):
    if auth is None:
        return {"error": "user not logged in"}   # Redirect to login

    u = db.query(UserTable).filter(UserTable.cookie == auth and UserTable.role == "partner").first()
    if not u:
        return {"error": "user not found"}
    
    return u

@router.get("/logout")
def logout(res: Response):
    res.delete_cookie(key="auth")
    return {"message": "logout successful"}

