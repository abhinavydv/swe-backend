from pydantic import BaseModel


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
    profile_picture: str


class Profile(BaseModel):
    first_name: str
    last_name: str
    email: str
    dob: str
    phone_number: str
    gender: str
    nationality: str
    profile_img: str

class LoginRequest(BaseModel):
    email: str
    password: str

class KYP(BaseModel):
    pan_number: str
    hotelling_license: str
    aadhar_photo_path: str
    account_number: str
    ifsc_code: str
