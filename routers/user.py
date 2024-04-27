from fastapi import APIRouter, Depends, Response, Cookie
from fastapi import UploadFile,File
from sqlalchemy import update,or_,and_
from sqlalchemy.orm import Session
from config.db import get_db
from config.gdrive import create_file,delete_file,get_file
from models import user
from schema.user import User as UserTable
from schema.kyp import KYP as KYPTable
from schema.hotel import Hotel as HotelTable
from schema.wishlist import Wishlist
import hashlib
import secrets
import os
import random
import smtplib, ssl

# Email verification using OTP

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

UPLOAD_FOLDER = "uploads"

def generate_cookie(user_id, email_id):
    secret = secrets.token_bytes(256)
    return hashlib.sha256(secret+str(user_id).encode()+str(email_id).encode()).hexdigest()

@router.post("/login")
def login(res: Response, login_req: user.LoginRequest, db: Session = Depends(get_db)):

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
            secure=True
        )
        u.cookie = cookie
        stmt = update(UserTable).where(UserTable.user_id == u.user_id).values(cookie=cookie)
        db.execute(stmt)
        db.commit()

        return {"status": "OK", "message": "login successful", "alert": False}

    else:
        return {"status": "Error", "message": "Email or password incorrect", "alert": True}

@router.post("/otp")
def generate_otp(user: user.OTP):

    otp = random.randint(100000,1000000)

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = os.getenv('EMAIL')
    receiver_email = user.email 
    password = os.getenv('PASSWORD')
    message = f"""\
    Subject: OTP Verification (Wanderlust.com)

    Your One-Time Password is {otp}"""

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        try:
            server.sendmail(sender_email, receiver_email, message)
        except Exception as e:
            return {"status": "ERROR", "otp": ""}
    
    return {"status": "OK", "otp":str(otp)}

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
        samesite="none",
        secure=True,
    )

    u.cookie = cookie

    db.add(u)

    if user.role == "partner":
        k = KYPTable(
            user_id = u.user_id,
            pan_number = "",
            aadhar_number = "",
            aadhar_photo_path = "",
            hotelling_license = "",
            account_number = "",
            ifsc_code = ""
        )
        db.add(k)

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
        first_name=u.first_name if u.first_name else "",
        last_name=u.last_name if u.last_name else "",
        email=u.email_id,
        dob=u.dob if u.dob else "",
        gender=u.gender if u.gender else "",
        phone_number=u.phone_number if u.phone_number else "",
        nationality=u.nationality if u.nationality else "",
        cookie=u.cookie if u.cookie else "",
        profile_img=u.profile_image_path if u.profile_image_path is not None else "",
        role=u.role
    )
    return {"status": "OK", "message": "user found", "alert": False, "user": user_details}
    # return user_details

@router.get("/logged_customer")
def get_logged_customer(auth: str = Cookie(None), db: Session = Depends(get_db)):
    if auth is None:
        #return {"status": "Error", "message": "user not logged in", "alert": False}   # Redirect to login
        return

    u = db.query(UserTable).filter(and_(UserTable.cookie == auth ,UserTable.role == "customer")).first()
    if not u:
        #return {"status": "Error", "message": "user not found", "alert": False}
        return
    
    user_details = user.UserWithoutPassword(
        user_id=u.user_id,
        first_name=u.first_name if u.first_name else "",
        last_name=u.last_name if u.last_name else "",
        email=u.email_id,
        dob=u.dob if u.dob else "",
        gender=u.gender if u.gender else "",
        phone_number=u.phone_number if u.phone_number else "",
        nationality=u.nationality if u.nationality else "",
        cookie=u.cookie if u.cookie else "",
        profile_img=u.profile_image_path if u.profile_image_path is not None else "",
        role=u.role
    )

    #return {"status": "OK", "message": "user found", "alert": False, "user": user_details}
    return user_details

# works
@router.get('/logged_partner')
def get_logged_partner(auth: str = Cookie(None), db: Session = Depends(get_db)):
    if auth is None:
        return None
        #return {"status": "Error", "message": "user not logged in", "alert": False}   # Redirect to login

    u = db.query(UserTable).filter(and_(UserTable.cookie == auth ,UserTable.role == "partner")).first()
    if not u:
        return None
        #return {"status": "Error", "message": "user not found", "alert": False}
    
    user_details = user.UserWithoutPassword(
        user_id=u.user_id,
        first_name=u.first_name if u.first_name else "",
        last_name=u.last_name if u.last_name else "",
        email=u.email_id,
        dob=u.dob if u.dob else "",
        gender=u.gender if u.gender else "",
        phone_number=u.phone_number if u.phone_number else "",
        nationality=u.nationality if u.nationality else "",
        cookie=u.cookie if u.cookie else "",
        profile_img=u.profile_image_path if u.profile_image_path is not None else "",
        role=u.role
    )
    
    return user_details
    #return {"status": "OK", "message": "user found", "alert": False, "user": user_details}

# works 
@router.post('/change_password')
def change_password(passwords: user.ChangePassword, user = Depends(get_logged_user),db: Session = Depends(get_db)):
    if user is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    
    user = user["user"]

    u = db.query(UserTable).filter(UserTable.user_id == user.user_id).first()

    # Concatenate the password and salt
    hashed_password = hashlib.sha256((passwords.new_password + u.salt).encode()).hexdigest()

    old_hashed_password = hashlib.sha256((passwords.old_password + u.salt).encode()).hexdigest()

    if old_hashed_password != u.password:
        return {"status": "Error", "message": "Incorrect password", "alert": True}

    stmt = update(UserTable).where(UserTable.user_id == user.user_id).values(password=hashed_password)
    db.execute(stmt)
    db.commit()

    return {"status": "OK", "message": "Changed password successfully", "alert": False}

# works
@router.post('/edit_profile')
def edit_profile(profile: user.Profile, user = Depends(get_logged_user),db: Session = Depends(get_db)):
    if user is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    
    user = user["user"]
    
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

# works
@router.post('/add_profile_photo')
def add_profile_photo(photo: UploadFile = File(...), user = Depends(get_logged_user),db: Session = Depends(get_db)):
    if user is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    user = user["user"]

    if not photo:
        return {"status": "Error", "message": "file not found", "alert": True}

    # Create destination folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER + "/profile_photos", exist_ok=True)
    
    file_path = os.path.join(UPLOAD_FOLDER + "/profile_photos", photo.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(photo.file.read())

    image_path = create_file(photo.filename, file_path)

    #os.remove(file_path)

    stmt = update(UserTable).where(UserTable.user_id == user.user_id).values(profile_image_path = image_path)
    db.execute(stmt)

    db.commit()

    return {"status": "OK", "message": "added photo", "alert": False}


# works
@router.post('/kyp_other_data')
def add_kyp(kyp: user.KYP, partner = Depends(get_logged_partner),db: Session = Depends(get_db)):
    if partner is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}

    update_stmt = update(KYPTable).where(KYPTable.user_id == partner.user_id).values(
        pan_number = kyp.pan_number,
        aadhar_number = kyp.aadhar_number,
        aadhar_photo_path = kyp.aadhar_photo_path,
        hotelling_license = kyp.hotelling_license,
        account_number = kyp.account_number,
        ifsc_code = kyp.ifsc_code
    )

    db.execute(update_stmt)
    # db.add(k)
    db.commit()

    return {"status": "OK", "message": "KYP is successfull", "alert": False}

# works
@router.post('/kyp_aadhar')
def add_aadhar(aadhar_photo: UploadFile = File(...), partner = Depends(get_logged_partner),db: Session = Depends(get_db)):
    if partner is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}

    if not aadhar_photo:
        return {"status": "Error", "message": "file not found", "alert": True}

    # Create destination folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER + "/aadhar_photos", exist_ok=True)

    file_path = os.path.join(UPLOAD_FOLDER + "/aadhar_photos", aadhar_photo.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(aadhar_photo.file.read())

    image_path = create_file(aadhar_photo.filename, file_path)

    #os.remove(file_path)

    stmt = update(KYPTable).where(KYPTable.user_id == partner.user_id).values(aadhar_photo_path = image_path)
    db.execute(stmt)
    db.commit()

    return {"status": "OK", "message": "Aadhar added", "alert": False}

# works  
@router.post('/kyp_hotel_license')
def add_aadhar(hotel_license: UploadFile = File(...) , partner = Depends(get_logged_partner),db: Session = Depends(get_db)):
    if partner is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    
    if not hotel_license:
        return {"status": "Error", "message": "file not found", "alert": True}

    # Create destination folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER + "/hotel_license", exist_ok=True)
    
    file_path = os.path.join(UPLOAD_FOLDER + "/hotel_license", hotel_license.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(hotel_license.file.read())

    doc_path = create_file(hotel_license.filename, file_path)

    #os.remove(file_path)

    stmt = update(KYPTable).where(KYPTable.user_id == partner.user_id).values(hotelling_license = doc_path)
    db.execute(stmt)
    db.commit()

    return {"status": "OK", "message": "Hotelling license added", "alert": False}

# works
@router.get('/get_kyp')
def get_kyp(partner = Depends(get_logged_partner),db: Session = Depends(get_db)):
    if partner is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    
    k = db.query(KYPTable).filter(KYPTable.user_id == partner.user_id).first()

    if not k:
        return {"status": "Error", "message": "KYP not found", "alert": True}
    
    return {"status": "OK", "message": "KYP found", "alert": False, "kyp": k}

# works
@router.get("/logout")
def logout(res: Response):
    res.delete_cookie(key="auth")
    return {"status": "OK", "message": "logout successful", "alert": False}

# not tested
# if partner deleted all hotels also deleted ?? Delete profile photos, kyp docs, hotel docs
@router.get("/delete_account")
def delete_account(user = Depends(get_logged_user),db: Session = Depends(get_db)):
    if user is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    user = user["user"]
    db.delete(db.query(UserTable).filter(UserTable.user_id == user.user_id).first())
    db.commit()

    return {"status": "OK", "message": "account deleted", "alert": False}


    

