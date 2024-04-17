from fastapi import APIRouter, Depends, Response, Cookie
from sqlalchemy import update
from sqlalchemy.orm import Session
from config.db import get_db
from models import user
from schema.user import User as UserTable
from schema.kyp import KYP as KYPTable
from schema.hotel import Hotel as HotelTable
from schema.wishlist import Wishlist
import hashlib
import secrets

# Email verification using OTP
# Saving images and documents in a folder and their paths in db


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
        dob=user.dob,
        phone_number=user.phone_number,
        gender=user.gender,
        nationality=user.nationality,
        password=hashed_password,
        salt=salt,
        role=user.role
        #profile_image_path = user.profile_img    # Left - Store the actual image in file system 
    )

    cookie = generate_cookie(u.user_id, u.email_id)
    u.cookie = cookie

    db.add(u)
    db.commit()
    db.refresh(u)

    return {"status": "successfully registered user"}

@router.get("/logged_customer")
def get_logged_customer(auth: str = Cookie(None), db: Session = Depends(get_db)):
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

@router.post('/edit_profile')
def edit_profile(profile: user.Profile, user = Depends(get_logged_partner or get_logged_customer),db: Session = Depends(get_db)):
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

    return {"message" : "edited profile successfully"}


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

    return {"status": "kyp is successfull"}

@router.get('/get_kyp')
def get_kyp(partner = Depends(get_logged_partner),db: Session = Depends(get_db)):
    k = db.query(KYPTable).filter(KYPTable.user_id == partner.user_id).first()

    if not k:
        return {"error": "kyp not done"}
    
    return k

@router.post('/add_to_wishlist')
def add_to_wishlist(hotel_id, customer = Depends(get_logged_customer),db: Session = Depends(get_db)):
    if not db.query(HotelTable).filter(HotelTable.hotel_id == hotel_id).first():
        return {"error": "hotel not found"}
    
    w = Wishlist(
        hotel_id = hotel_id,
        user_id = customer.user_id
    )

    db.add(w)
    db.commit()
    db.refresh()

    return {"message" : "added to wishlist successfully"}

@router.post('/delete_from_wishlist')
def delete_from_wishlist(hotel_id, customer = Depends(get_logged_customer),db: Session = Depends(get_db)):
    if not db.query(HotelTable).filter(HotelTable.hotel_id == hotel_id).first():
        return {"error": "hotel not found"}
    
    w = db.query(Wishlist).filter(Wishlist.hotel_id == hotel_id and Wishlist.user_id == customer.user_id).first()

    if not w:
        return {"error" : "wishlist entry not found"}
    
    db.delete(w)
    db.commit()

    return {"message" : "deleted wishlist entry successfully"}

@router.get('/view_wishlist')
def view_wishlist(customer = Depends(get_logged_customer),db: Session = Depends(get_db)):
    w = db.query(Wishlist).filter(Wishlist.user_id == customer.user_id).all()

    if not w:
        return {"error" : "wishlist is empty"}
    
    return w
    

@router.get("/logout")
def logout(res: Response):
    res.delete_cookie(key="auth")
    return {"message": "logout successful"}

