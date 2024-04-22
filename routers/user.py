from fastapi import APIRouter, Depends, Response, Cookie
from sqlalchemy import update,or_,and_
from sqlalchemy.orm import Session
from config.db import get_db
from models import user
from schema.user import User as UserTable
from schema.kyp import KYP as KYPTable
from schema.hotel import Hotel as HotelTable
from schema.wishlist import Wishlist
import hashlib
import secrets
import os

# Email verification using OTP
# Saving images and documents in a folder and their paths in db


router = APIRouter(
    prefix="/users",
    tags=["users"],
)

UPLOAD_FOLDER = "uploads/profile_images"

def generate_cookie(user_id, email_id):
    secret = secrets.token_bytes(256)
    return hashlib.sha256(secret+str(user_id).encode()+str(email_id).encode()).hexdigest()

@router.post("/login")
def login(res: Response, login_req: user.LoginRequest, db: Session = Depends(get_db)):
    print(res, login_req)

    u = db.query(UserTable).filter(UserTable.email_id == login_req.email).first()

    if not u:
        return {"status": "Error", "message": "Email or password incorrect", "alert": True}

    hashed_password = hashlib.sha256((login_req.password + u.salt).encode()).hexdigest()

    # Compare the newly hashed password with the stored hashed password
    if hashed_password == u.password:
        cookie = generate_cookie(u.user_id, u.email_id)
        res.set_cookie(
            key='auth',
            value=cookie,
            max_age=60 * 60 * 24,
            samesite="lax",
        )
        u.cookie = cookie
        stmt = update(UserTable).where(UserTable.user_id == u.user_id).values(cookie=cookie)
        db.execute(stmt)
        db.commit()

        return {"status": "OK", "message": "login successful", "alert": False}

    else:
        return {"status": "Error", "message": "Email or password incorrect", "alert": True}


@router.post("/register")
def register(res: Response, user: user.User, db: Session = Depends(get_db)):
    print(user)
    if db.query(UserTable).filter(UserTable.email_id == user.email).first():
        return {"status": "Error", "message": "User already exists", "alert": True}

    ## Email verification left

    # Generate a random salt
    salt = secrets.token_hex(16)  # Generate a 16-byte salt (32 characters when represented in hexadecimal)

    # Concatenate the password and salt
    hashed_password = hashlib.sha256((user.password + salt).encode()).hexdigest()

    u = UserTable(
        first_name=user.first_name,
        last_name=user.last_name, 
        email_id=user.email,
        dob=user.dob,
        phone_number=user.phone_number,
        gender=user.gender,
        nationality=user.nationality,
        password=hashed_password,
        salt=salt,
        role=user.role
    )

    cookie = generate_cookie(u.user_id, u.email_id)
    res.set_cookie(
        key='auth',
        value=cookie,
        max_age=60 * 60 * 24,
        samesite="lax",
    )
    u.cookie = cookie

    db.add(u)
    db.commit()
    db.refresh(u)

    return {"status": "OK", "message": "User registered successfully", "alert": False}

@router.get("/logged")
def get_logged_user(auth: str = Cookie(None), db: Session = Depends(get_db)):
    if auth is None:
        return {"status": "Error", "message": "user not logged in", "alert": False}

    u = db.query(UserTable).filter(UserTable.cookie == auth).first()
    if not u:
        return {"status": "Error", "message": "user not found", "alert": False}
    
    user_details = user.UserWithoutPassword(
        user_id=u.user_id,
        first_name=u.first_name,
        last_name=u.last_name,
        email=u.email_id,
        dob=u.dob,
        gender=u.gender,
        phone_number=u.phone_number,
        nationality=u.nationality,
        cookie=u.cookie,
        profile_img=u.profile_image_path,
        role=u.role
    )

    return {"status": "OK", "message": "user found", "alert": False, "user": user_details}

@router.get("/logged_customer")
def get_logged_customer(auth: str = Cookie(None), db: Session = Depends(get_db)):
    if auth is None:
        return {"status": "Error", "message": "user not logged in", "alert": False}   # Redirect to login

    u = db.query(UserTable).filter(UserTable.cookie == auth).first()
    if not u:
        return {"status": "Error", "message": "user not found", "alert": False}
    
    user_details = user.UserWithoutPassword(
        user_id=u.user_id,
        first_name=u.first_name,
        last_name=u.last_name,
        email=u.email_id,
        dob=u.dob,
        gender=u.gender,
        phone_number=u.phone_number,
        nationality=u.nationality,
        cookie=u.cookie,
        profile_img=u.profile_image_path,
        role=u.role
    )

    return {"status": "OK", "message": "user found", "alert": False, "user": user_details}

@router.get('/logged_partner')
def get_logged_partner(auth: str = Cookie(None), db: Session = Depends(get_db)):
    if auth is None:
        return {"status": "Error", "message": "user not logged in", "alert": False}   # Redirect to login

    u = db.query(UserTable).filter(and_(UserTable.cookie == auth ,UserTable.role == "partner")).first()
    if not u:
        return {"status": "Error", "message": "user not found", "alert": False}
    
    user_details = user.UserWithoutPassword(
        user_id=u.user_id,
        first_name=u.first_name,
        last_name=u.last_name,
        email=u.email_id,
        dob=u.dob,
        gender=u.gender,
        phone_number=u.phone_number,
        nationality=u.nationality,
        cookie=u.cookie,
        profile_img=u.profile_image_path,
        role=u.role
    )
    
    return {"status": "OK", "message": "user found", "alert": False, "user": user_details}

@router.post('/edit_profile')
def edit_profile(profile: user.Profile, user = Depends(get_logged_partner or get_logged_customer),db: Session = Depends(get_db)):
    # file_path = os.path.join(UPLOAD_FOLDER, profile.profile_img.filename)
    # with open(file_path, "wb") as buffer:
    #     buffer.write(profile.profile_img.read())
    
    stmt = update(UserTable).where(UserTable.user_id == user.user_id).values(
        first_name = profile.first_name,
        last_name = profile.last_name,
        email_id = profile.email,
        dob = profile.dob,
        phone_number = profile.phone_number,
        gender = profile.gender,
        nationality = profile.nationality,
        profile_image_path = profile.profile_img
    )

    db.execute(stmt)
    db.commit()

    return {"status": "OK", "message": "Edited profile successfully", "alert": False}


@router.post('/kyp')
def add_kyp(kyp: user.KYP, partner = Depends(get_logged_partner),db: Session = Depends(get_db)):
    k = KYPTable(
        user_id = partner.user_id,
        pan_number = kyp.pan_number,
        aadhar_photo_path = kyp.aadhar_photo_path,
        hotelling_license = kyp.hotelling_license,
        account_number = kyp.account_number,
        ifsc_code = kyp.ifsc_code
    )

    db.add(k)
    db.commit()
    db.refresh()

    return {"status": "OK", "message": "KYP is successfull", "alert": False}
    

@router.get('/get_kyp')
def get_kyp(partner = Depends(get_logged_partner),db: Session = Depends(get_db)):
    k = db.query(KYPTable).filter(KYPTable.user_id == partner.user_id).first()

    if not k:
        return {"status": "Error", "message": "KYP not found", "alert": True}
    
    return {"status": "OK", "message": "KYP found", "alert": False, "kyp": k}


@router.get("/logout")
def logout(res: Response):
    res.delete_cookie(key="auth")
    return {"status": "OK", "message": "logout successful", "alert": False}
    

