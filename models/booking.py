from pydantic import BaseModel
from typing import List
from models.hotel import DateRange

class GuestProfile(BaseModel):
    guest_name: str
    gender: str
    age: int

class RoomDetails(BaseModel):
    room_type: int
    number_of_rooms: int

# class BookingDetails(BaseModel):
#     hotel_id: int
#     check_in_date: str
#     check_out_date: str
#     rooms: List[RoomDetails]
#     bill: float

# class BookingGuests(BaseModel):
#     guests: List[int]
#     transaction_id: int
    

class BookingDetails(BaseModel):
    hotel_id: int
    date_range: DateRange
    rooms: List[RoomDetails]
    guests: List[int]
    bill: float
    transaction_id: int


class Review(BaseModel):
    booking_id: int
    title: str
    description: str
    rating: int
    

    
