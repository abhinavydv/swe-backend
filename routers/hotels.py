from fastapi import APIRouter, Depends, Response, Cookie
from sqlalchemy.orm import Session
from config.db import get_db
from models import hotel
from schema.hotel import Hotel as HotelTable
from schema.room import Room as RoomTable
from routers.user import get_logged_user
from typing import List

router = APIRouter(
    prefix="/hotels",
    tags=["hotels"],
)

@router.get("/{city}")
def get_hotels(city: str):
    pass

@router.post("/add_hotel")
def add_hotel(hotel: hotel.Hotel, rooms: List[hotel.Room] ,owner = Depends(get_logged_user),db: Session = Depends(get_db)):
    h = HotelTable(
        owner_id = owner.user_id,
        hotel_name = hotel.hotel_name,
        property_paper_path = hotel.property_paper_path,
        description = hotel.description,
        pincode = hotel.pincode,
        locality = hotel.locality,
        address = hotel.address,
        city = hotel.city,
        state = hotel.state,
        country = hotel.country,
        amenities = int(hotel.amenities),
        tag_list = hotel.tag_list
    )

    db.add(h)
    db.commit()
    db.refresh(h)

    for room in rooms:
        r = RoomTable(
            hotel_id = h.hotel_id,
            room_type = room.room_type,
            number_of_rooms = room.number_of_rooms,
            price = room.price,
            amenities = int(room.amenities)
        )
        db.add(r)

    db.commit()

    return {"message": "Hotel and rooms added successfully"}


    



    
