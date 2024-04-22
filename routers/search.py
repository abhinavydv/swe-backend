from fastapi import APIRouter, Depends, Response, Cookie
from sqlalchemy.orm import Session,joinedload
from sqlalchemy import func,text,or_,and_
from config.db import get_db
from models import hotel
from schema.hotel import Hotel as HotelTable
from schema.room import Room as RoomTable
from schema.user import User as UserTable
from schema.review import Review as ReviewTable
from schema.room import Room as RoomTable
from schema.room_amenity import RoomAmenity
from schema.hotel_photo import HotelPhoto as PhotoTable
from schema.wishlist import Wishlist
from routers.user import get_logged_partner,get_logged_customer
from typing import List

router = APIRouter(
    prefix="/search",
    tags=["search"],
)

# Need to test properly
def get_available_rooms(hotel_id, date_range: hotel.DateRange,db: Session = Depends(get_db)):
    query = text(
        """ SELECT 
                rooms.* , 
                total_rooms - COALESCE((
                SELECT SUM(number_of_rooms) 
                FROM booking_rooms 
                JOIN bookings ON booking_rooms.booking_id = bookings.booking_id 
                WHERE bookings.hotel_id = :hotel_id 
                AND (
                    bookings.check_in_date BETWEEN :start_date AND :end_date
                    OR bookings.check_out_date BETWEEN :start_date AND :end_date
                    OR :start_date BETWEEN bookings.check_in_date AND bookings.check_out_date
                ) 
                AND booking_rooms.room_id = rooms.room_id
                GROUP BY booking_rooms.room_id
            ), 0) AS number_of_available_rooms
            FROM rooms 
            WHERE hotel_id = :hotel_id
            AND total_rooms > (
                SELECT COALESCE(SUM(number_of_rooms), 0) 
                FROM booking_rooms 
                JOIN bookings ON booking_rooms.booking_id = bookings.booking_id 
                WHERE bookings.hotel_id = :hotel_id 
                AND (
                    bookings.check_in_date BETWEEN :start_date AND :end_date
                    OR bookings.check_out_date BETWEEN :start_date AND :end_date
                    OR :start_date BETWEEN bookings.check_in_date AND bookings.check_out_date
                ) 
                GROUP BY booking_rooms.room_id
            ); """
        )
    
        # Parameters for the query
    params = {
        "hotel_id": hotel_id,
        "start_date": date_range.start_date,
        "end_date": date_range.end_date
    }

    avail_rooms = db.execute(query, params)

    return avail_rooms


# need to test properly
@router.post('/{query}')
def get_hotels(query: str, db: Session = Depends(get_db)):
    h = db.query(HotelTable).filter(or_(HotelTable.city == query, HotelTable.hotel_name == query, HotelTable.locality == query )).all()
    hotel_obj = []

    if not h:
        return {"status": "Error", "message": "No results", "alert": True}
    
    for hotel_row in h:
        # if not get_available_rooms(hotel_row.hotel_id, query.date_range, db):
        #     continue
        
        rating = db.query(func.avg(ReviewTable.rating)).filter(ReviewTable.hotel_id == hotel_row.hotel_id).scalar()
        lowest_price = db.query(func.min(RoomTable.price)).filter(RoomTable.hotel_id == hotel_row.hotel_id).scalar()
        photo = db.query(PhotoTable.photo_url).filter(PhotoTable.hotel_id == hotel_row.hotel_id).first()

        if not lowest_price:
            lowest_price = 0
        
        if not rating:
            rating = 0
        
        if not photo:
            photo = ""

        obj = hotel.HotelSearch(
            hotel_id = hotel_row.hotel_id,
            address = hotel_row.address,
            amenities = str(hotel_row.amenities),
            hotel_name = hotel_row.hotel_name,
            lowest_price = lowest_price,
            rating=rating,
            img_path=photo
        )
        
        hotel_obj.append(obj)

    if not hotel_obj:
        return {"status": "Error", "message": "No results", "alert": True}

    return {"status": "OK", "message": "Found hotels", "alert": False, "hotels" : hotel_obj}
    

@router.post('/filters')
def get_hotels_with_filters():
    pass

# need to test properly
@router.post('/get_hotel_page')
def get_hotel_page(hotel_id, date_range: hotel.DateRange,db: Session = Depends(get_db)):
    h = db.query(HotelTable).filter(hotel_id == HotelTable.hotel_id).first()

    if not h:
        return {"status": "Error", "message": "hotel not found", "alert": True}
    
    hotel_photos = db.query(PhotoTable.photo_url).filter(PhotoTable.hotel_id == hotel_id).all()

    avail_rooms = get_available_rooms(hotel_id,date_range,db)

    available_rooms = []

    for room in avail_rooms:
        a = db.query(RoomAmenity).filter(RoomAmenity.room_id == room.room_id).all()
        r = hotel.Room(
            bed_type = room.bed_type,
            max_occupancy = room.max_occupancy,
            price = room.price,
            room_type = room.room_type,
            amenities = a
        )
        
        available_rooms.append(r)
    
    h_page = hotel.HotelPage(
        hotel_name = h.hotel_name,
        amenities = h.amenities,
        description = h.description,
        available_rooms = available_rooms,
        photos = hotel_photos
    )
    
    return {"status": "OK", "message": "Found hotel details", "alert": False, "hotel_page" : h_page}

@router.post('/add_to_wishlist')
def add_to_wishlist(hotel_id, customer = Depends(get_logged_customer),db: Session = Depends(get_db)):
    if not db.query(HotelTable).filter(HotelTable.hotel_id == hotel_id).first():
        return {"status": "Error", "message": "hotel not found", "alert": True}
    
    w = Wishlist(
        hotel_id = hotel_id,
        user_id = customer.user_id
    )

    db.add(w)
    db.commit()
    db.refresh()

    return {"status": "OK", "message": "added to wishlist successfully", "alert": False}

@router.post('/delete_from_wishlist')
def delete_from_wishlist(hotel_id, customer = Depends(get_logged_customer),db: Session = Depends(get_db)):
    if not db.query(HotelTable).filter(HotelTable.hotel_id == hotel_id).first():
        return {"status": "Error", "message": "hotel not found", "alert": True}
    
    w = db.query(Wishlist).filter(and_(Wishlist.hotel_id == hotel_id, Wishlist.user_id == customer.user_id)).first()

    if not w:
        return {"status": "Error", "message": "wishlist entry not found", "alert": True}
    
    db.delete(w)
    db.commit()

    return {"status": "OK", "message": "deleted wishlist entry successfully", "alert": False}

@router.get('/view_wishlist')
def view_wishlist(customer = Depends(get_logged_customer),db: Session = Depends(get_db)):
    w = db.query(Wishlist).filter(Wishlist.user_id == customer.user_id).all()

    w = (
        db.query(Wishlist,HotelTable).join(HotelTable, Wishlist.hotel_id == HotelTable.hotel_id)
        .filter(Wishlist.user_id == customer.user_id).all()
    )

    if not w:
        return {"status": "Error", "message": "wishlist is empty", "alert": True}
    
    hotel_obj = []
    
    for hotel_row in w:
        rating = db.query(func.avg(ReviewTable.rating)).filter(ReviewTable.hotel_id == hotel_row.hotel_id).scalar()
        lowest_price = db.query(func.min(RoomTable.price)).filter(RoomTable.hotel_id == hotel_row.hotel_id).scalar()
        photo = db.query(PhotoTable.photo_url).filter(PhotoTable.hotel_id == hotel_row.hotel_id).first()

        if not lowest_price:
            lowest_price = 0
        
        if not rating:
            rating = 0
        
        if not photo:
            photo = ""

        obj = hotel.HotelSearch(
            hotel_id = hotel_row.hotel_id,
            address = hotel_row.address,
            amenities = str(hotel_row.amenities),
            hotel_name = hotel_row.hotel_name,
            lowest_price = lowest_price,
            rating=rating,
            img_path=photo
        )
        
        hotel_obj.append(obj)

    
    return {"status": "OK", "message": "Found hotels in wishlist", "alert": False, "wishlist" : hotel_obj}
    
    
    

    

    

    

    

    