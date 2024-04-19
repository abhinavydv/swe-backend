from fastapi import APIRouter, Depends, Response, Cookie
from sqlalchemy.orm import Session
from sqlalchemy import func
from config.db import get_db
from models import hotel
from schema.hotel import Hotel as HotelTable
from schema.room import Room as RoomTable
from schema.user import User as UserTable
from schema.review import Review as ReviewTable
from schema.room import Room as RoomTable
from schema.hotel_photo import HotelPhoto as PhotoTable
from routers.user import get_logged_partner,get_logged_customer
from typing import List

router = APIRouter(
    prefix="/search",
    tags=["search"],
)

@router.post('/{query}')
def get_hotels(query: str,db: Session = Depends(get_db)):
    h = db.query(HotelTable).filter(HotelTable.hotel_name == query or HotelTable.city == query or HotelTable.locality == query).all()
    hotel_obj = []

    if not h:
        return {"status": "Error", "message": "No results", "alert": True}
    
    for hotel_row in h:
        obj = hotel.HotelSearch()
        rating = db.query(func.avg(ReviewTable.rating)).filter(ReviewTable.hotel_id == hotel_row.hotel_id).scalar()
        lowest_price = db.query(func.min(RoomTable.price)).filter(RoomTable.hotel_id == hotel_row.hotel_id).scalar()
        photo = db.query(PhotoTable.photo_url).filter(PhotoTable.hotel_id == hotel_row.hotel_id).first()
        
        obj.hotel_id = hotel_row.hotel_id
        obj.address = hotel_row.address
        obj.amenities = str(hotel_row.amenities)
        obj.city = hotel_row.city
        obj.country = hotel_row.country
        obj.description = hotel_row.description
        obj.hotel_name = hotel_row.hotel_name
        obj.state = hotel_row.state
        obj.locality = hotel_row.locality
        obj.pincode = hotel_row.pincode
        obj.tag_list = hotel_row.tag_list
        obj.lowest_price = lowest_price
        obj.rating = rating
        obj.img_path = photo

        hotel_obj.append(obj)

    
    return {"status": "OK", "message": "Found hotels", "alert": False, "hotels" : hotel_obj}
    


@router.post('/filters')
def get_hotels_with_filters():
    pass
    