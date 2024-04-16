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
            number_of_available_rooms = room.number_of_rooms,
            total_rooms = room.number_of_rooms,
            price = room.price,
            amenities = int(room.amenities)
        )
        db.add(r)

    db.commit()

    return {"message": "Hotel and rooms added successfully"}

@router.post('/edit_hotel')
def edit_hotel(hotel_id, hotel: hotel.Hotel, rooms: List[hotel.Room] ,owner = Depends(get_logged_user),db: Session = Depends(get_db)):
    h = db.query(HotelTable).filter(HotelTable.hotel_id == hotel_id).first()

    if not h:
        return {"error":"hotel not found"}
    
    # Update the hotel information with the new data
    h.hotel_name = hotel.hotel_name
    h.property_paper_path = hotel.property_paper_path
    h.description = hotel.description
    h.pincode = hotel.pincode
    h.locality = hotel.locality
    h.address = hotel.address
    h.city = hotel.city
    h.state = hotel.state
    h.country = hotel.country
    h.amenities = int(hotel.amenities)
    h.tag_list = hotel.tag_list

    for room in rooms:
        r = db.query(RoomTable).filter(RoomTable.hotel_id == hotel_id and RoomTable.room_type==room.room_type).first()

        # Room type not present add in the rooms db
        if not r:
            r = RoomTable(
                hotel_id = hotel_id,
                room_type = room.room_type,
                number_of_available_rooms = room.number_of_rooms,
                total_rooms = room.number_of_rooms,
                price = room.price,
                amenities = int(room.amenities)
            )
            db.add(r) 

        # update existing room type
        else:
            r.room_type = room.room_type,
            r.total_rooms = room.number_of_rooms,
            r.price = room.price,
            r.amenities = int(room.amenities)

    db.commit()

    return {"message": "hotel and rooms edited successfully"}

@router.post('/delete_room_type')
def delete_room(hotel_id,room_type,db: Session = Depends(get_db)):
    r = db.query(RoomTable).filter(RoomTable.hotel_id == hotel_id and RoomTable.room_type==room_type).first()

    if not r:
        return {"error": "room tpe not found"}
    
    db.delete(r)
    db.commit()

    return {"message": "room deleted successfully"}

@router.post('/delete_hotel')
def delete_hotel(hotel_id,db: Session = Depends(get_db)):
    h = db.query(HotelTable).filter(HotelTable.hotel_id == hotel_id).first()

    if not h:
        return {"error":"hotel not found"}
    
    db.delete(h)

    db.commit()

    return {"hotel deleted success"}
            
    
    



    



    
