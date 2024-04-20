from fastapi import APIRouter, Depends, Response, Cookie
from sqlalchemy.orm import Session
from sqlalchemy import update
from config.db import get_db
from models import hotel
from schema.hotel import Hotel as HotelTable
from schema.room import Room as RoomTable
from schema.user import User as UserTable
from schema.room_amenity import RoomAmenity
from routers.user import get_logged_partner
from typing import List

router = APIRouter(
    prefix="/hotels",
    tags=["hotels"],
)


@router.post("/add_hotel")
def add_hotel(hotel: hotel.Hotel, rooms: List[hotel.Room] ,owner = Depends(get_logged_partner),db: Session = Depends(get_db)):
    # Adding photos
    # Tag List parsing

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
    
    for room in rooms:
        r = RoomTable(
            hotel_id = h.hotel_id,
            room_type = room.room_type,
            bed_type = room.bed_type,
            number_of_available_rooms = room.number_of_rooms,
            total_rooms = room.number_of_rooms,
            price = room.price,
        )

        db.add(r)
        for amenity in room.amenities:
            a = RoomAmenity(
                room_id = r.room_id,
                amenity = amenity.amenity,
                quality = amenity.quality
            )
            db.add(a)
    
    db.commit()

    return {"status": "OK", "message": "Added hotel successfully", "alert": False}

@router.post('/edit_hotel')
def edit_hotel(hotel_id, hotel: hotel.Hotel, rooms: List[hotel.Room] ,owner = Depends(get_logged_partner),db: Session = Depends(get_db)):
    # Adding photos
    # Tag List parsing
    
    h = db.query(HotelTable).filter(HotelTable.hotel_id == hotel_id and HotelTable.owner_id == owner.user_id).first()

    if not h:
        return {"status": "Error", "message": "hotel not found", "alert": True}
    
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
                bed_type = room.bed_type,
                number_of_available_rooms = room.number_of_rooms,
                total_rooms = room.number_of_rooms,
                price = room.price,
            )
            db.add(r) 
            
            for amenity in room.amenities:
                a = RoomAmenity(
                    room_id = r.room_id,
                    amenity = amenity.amenity,
                    quality = amenity.quality
                )
                db.add(a)
            db.commit()
                
        # update existing room type
        else:
            r.room_type = room.room_type,
            r.total_rooms = room.number_of_rooms,
            r.price = room.price,
            for amenity in room.amenities:
                stmt = update(RoomAmenity).where(RoomAmenity.room_id == r.room_id).values(
                    amenity = amenity.amenity,
                    quality = amenity.quality
                )
                db.execute(stmt)

    db.commit()

    return {"status": "OK", "message": "Edited hotel successfully", "alert": False}

@router.post('/delete_room_type')
def delete_room(hotel_id,room_type,owner = Depends(get_logged_partner),db: Session = Depends(get_db)):
    
    if not db.query(HotelTable).filter(HotelTable.hotel_id == hotel_id and HotelTable.owner_id == owner.user_id).first():
        return {"status": "Error", "message": "hotel not found", "alert": True}
    
    r = db.query(RoomTable).filter(RoomTable.hotel_id == hotel_id and RoomTable.room_type==room_type).first()

    if not r:
        return {"status": "Error", "message": "room type not found", "alert": True}
    
    db.delete(r)
    db.commit()

    return {"status": "OK", "message": "Deleted room successfully", "alert": False}

@router.post("/view hotel")
def view_hotel(hotel_id,partner = Depends(get_logged_partner),db: Session = Depends(get_db)):
    h = db.query(HotelTable).filter(HotelTable.hotel_id == hotel_id and HotelTable.owner_id == partner.user_id).first()

    if not h:
        return {"status": "Error", "message": "hotel not found", "alert": True}
    
    return h

@router.get('/view_listings')
def view_listings(partner = Depends(get_logged_partner),db: Session = Depends(get_db)):
    h = db.query(HotelTable).filter(HotelTable.owner_id == partner.user_id).all()

    if not h:
        return {"status": "Error", "message": "hotels not found", "alert": True}
    
    return h

@router.post('/delete_hotel')
def delete_hotel(hotel_id,owner = Depends(get_logged_partner),db: Session = Depends(get_db)):
    
    h = db.query(HotelTable).filter(HotelTable.hotel_id == hotel_id and HotelTable.owner_id == owner.user_id).first()

    if not h:
        return {"status": "Error", "message": "hotel not found", "alert": True}
    
    db.delete(h)

    db.commit()

    return {"status": "OK", "message": "Deleted room successfully", "alert": False}
            
    
    



    



    
