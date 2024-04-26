from pydantic import BaseModel
from fastapi import UploadFile,File


class User(BaseModel):
    first_name: str
    last_name: str
    email: str
    dob: str
    phone_number: str
    gender: str
    nationality: str
    password: str
    role: str
class OTP(BaseModel):
    email: str
class UserWithoutPassword(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: str
    dob: str
    phone_number: str
    gender: str
    nationality: str
    role: str
    cookie: str
    profile_img: str

class Profile(BaseModel):
    first_name: str
    last_name: str
    email: str
    dob: str
    phone_number: str
    gender: str
    nationality: str
    
class LoginRequest(BaseModel):
    email: str
    password: str

class KYP(BaseModel):
    pan_number: str
    aadhar_number: str
    account_number: str
    ifsc_code: str

class ChangePassword(BaseModel):
    old_password: str
    new_password: str
