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
    profile_img: str

class LoginRequest(BaseModel):
    email: str
    password: str
