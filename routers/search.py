from fastapi import APIRouter, Depends, Response, Cookie
from sqlalchemy.orm import Session,joinedload
from sqlalchemy import func,text,or_,and_
from config.db import get_db
from models import hotel
from datetime import datetime
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
def get_available_rooms(hotel_id,start_date,end_date,db):
    # query = text(
    #     """ SELECT 
    #             rooms.* , 
    #             total_rooms - (SELECT COALESCE(SUM(number_of_rooms),0) 
    #             FROM booking_rooms 
    #             JOIN bookings ON booking_rooms.booking_id = bookings.booking_id 
    #             WHERE bookings.hotel_id = :hotel_id 
    #             AND (
    #                 bookings.from_date BETWEEN :start_date AND :end_date
    #                 OR bookings.to_date BETWEEN :start_date AND :end_date
    #                 OR :start_date BETWEEN bookings.from_date AND bookings.to_date
    #             ) 
    #             AND booking_rooms.room_id = rooms.room_id
    #             GROUP BY booking_rooms.room_id
    #         ) AS number_of_available_rooms
    #         FROM rooms 
    #         WHERE hotel_id = :hotel_id
    #         AND total_rooms > (
    #             SELECT COALESCE(SUM(number_of_rooms), 0) 
    #             FROM booking_rooms 
    #             JOIN bookings ON booking_rooms.booking_id = bookings.booking_id 
    #             WHERE bookings.hotel_id = :hotel_id 
    #             AND (
    #                 bookings.from_date BETWEEN :start_date AND :end_date
    #                 OR bookings.to_date BETWEEN :start_date AND :end_date
    #                 OR :start_date BETWEEN bookings.from_date AND bookings.to_date
    #             ) 
    #             GROUP BY booking_rooms.room_id
    #         ); """
    #     )
    
    query = text("""
                    SELECT 
                        rooms.*,
                        total_rooms - COALESCE(sub.total_booked_rooms, 0) AS number_of_available_rooms
                    FROM 
                        rooms 
                    LEFT JOIN (
                        SELECT 
                            booking_rooms.room_id,
                            SUM(number_of_rooms) AS total_booked_rooms
                        FROM 
                            booking_rooms 
                        JOIN 
                            bookings ON booking_rooms.booking_id = bookings.booking_id 
                        WHERE 
                            bookings.hotel_id = :hotel_id 
                            AND (bookings.status = 0 OR bookings.status = 1)
                            AND (
                                bookings.from_date BETWEEN :start_date AND :end_date
                                OR bookings.to_date BETWEEN :start_date AND :end_date
                                OR :start_date BETWEEN bookings.from_date AND bookings.to_date
                            ) 
                        GROUP BY 
                            booking_rooms.room_id
                    ) AS sub ON rooms.room_id = sub.room_id
                    WHERE 
                        rooms.hotel_id = :hotel_id
                        AND rooms.total_rooms > COALESCE(sub.total_booked_rooms, 0);
                """)
    
    # Parameters for the query
    params = {
        "hotel_id": hotel_id,
        "start_date": start_date,
        "end_date": end_date
    }

    avail_rooms = db.execute(query, params).fetchall()

    return avail_rooms

# Function to convert a list of SQLAlchemy RoomAmenity objects to a list of Pydantic RoomAmenities objects
def convert_room_amenities(amenities: list) -> list[hotel.RoomAmenities]:
    return [hotel.RoomAmenities(**amenity.__dict__) for amenity in amenities]


# need to test properly
@router.post('/')
def get_hotels(query: hotel.SearchQuery, user = Depends(get_logged_customer), db: Session = Depends(get_db)):
    h = db.query(HotelTable).filter(or_(HotelTable.city == query.text, HotelTable.hotel_name == query.text, HotelTable.locality == query.text )).all()
    hotel_obj = []

    if user is not None:
        w = db.query(Wishlist).filter(Wishlist.user_id == user.user_id).all()
        if not w:
            is_present = False
        else:
            is_present = True

    else:
        is_present = False

    if not h:
        return {"status": "Error", "message": "No results", "alert": True}
    
    for hotel_row in h:
        # if not get_available_rooms(hotel_row.hotel_id, query.date_range, db):
        #     continue
        
        rating = db.query(func.avg(ReviewTable.rating)).filter(ReviewTable.hotel_id == hotel_row.hotel_id).scalar()
        lowest_price = db.query(func.min(RoomTable.price)).filter(RoomTable.hotel_id == hotel_row.hotel_id).scalar()
        photo = db.query(PhotoTable.photo_url).filter(PhotoTable.hotel_id == hotel_row.hotel_id).first()

        if is_present:
            is_present = any(item.hotel_id == hotel_row.hotel_id for item in w)

        obj = hotel.HotelSearch(
            hotel_id = hotel_row.hotel_id,
            address = hotel_row.address,
            amenities = str(hotel_row.amenities),
            hotel_name = hotel_row.hotel_name,
            lowest_price = lowest_price if lowest_price is not None else 0,
            rating = rating if rating is not None else 0,
            img_path = photo[0] if photo is not None else "",  
            is_wishlisted = is_present
        )
        
        hotel_obj.append(obj)

    if not hotel_obj:
        return {"status": "Error", "message": "No results", "alert": True}

    return {"status": "OK", "message": "Found hotels", "alert": False, "hotels" : hotel_obj}
    

@router.post('/filters')
def get_hotels_with_filters(query: hotel.SearchQueryWithFilter, user = Depends(get_logged_customer),db: Session = Depends(get_db)):
    filter_value = int(query.filters, 2)
    
    h = db.query(HotelTable).filter(
        or_(HotelTable.city == query.text, HotelTable.hotel_name == query.text, HotelTable.locality == query.text)).filter(
            (HotelTable.amenities.op('&')(filter_value)) == filter_value).all()
    hotel_obj = []
    if user is not None:
        w = db.query(Wishlist).filter(Wishlist.user_id == user.user_id).all()
        if not w:
            is_present = False
        else:
            is_present = True

    else:
        is_present = False

    if not h:
        return {"status": "Error", "message": "No results", "alert": True}
    
    for hotel_row in h:
        # if not get_available_rooms(hotel_row.hotel_id, query.date_range, db):
        #     continue
        
        rating = db.query(func.avg(ReviewTable.rating)).filter(ReviewTable.hotel_id == hotel_row.hotel_id).scalar()
        lowest_price = db.query(func.min(RoomTable.price)).filter(RoomTable.hotel_id == hotel_row.hotel_id).scalar()
        photo = db.query(PhotoTable.photo_url).filter(PhotoTable.hotel_id == hotel_row.hotel_id).first()

        if is_present:
            is_present = any(item.hotel_id == hotel_row.hotel_id for item in w)

        obj = hotel.HotelSearch(
            hotel_id = hotel_row.hotel_id,
            address = hotel_row.address,
            amenities = str(hotel_row.amenities),
            hotel_name = hotel_row.hotel_name,
            lowest_price = lowest_price if lowest_price is not None else 0,
            rating = rating if rating is not None else 0,
            img_path = photo[0] if photo is not None else "",  
            is_wishlisted = is_present
        )
        
        hotel_obj.append(obj)

    if not hotel_obj:
        return {"status": "Error", "message": "No results", "alert": True}

    return {"status": "OK", "message": "Found hotels", "alert": False, "hotels" : hotel_obj}

# need to test properly
# works - need to test more once booking data is added
@router.post('/get_hotel_page')
def get_hotel_page(query: hotel.HotelPageQuery,db: Session = Depends(get_db)):
    h = db.query(HotelTable).filter(query.hotel_id == HotelTable.hotel_id).first()
    
    if not h:
        return {"status": "Error", "message": "hotel not found", "alert": True}
    
    hotel_photos = db.query(PhotoTable.photo_url).filter(PhotoTable.hotel_id == query.hotel_id).all()

    if hotel_photos is None:
        hotel_photos = []
    else:
        hotel_photos = [photo[0] for photo in hotel_photos]

    start_date = datetime.strptime(query.date_range.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(query.date_range.end_date,"%Y-%m-%d")

    avail_rooms = get_available_rooms(query.hotel_id,start_date,end_date,db)

    available_rooms = []

    if not avail_rooms:
        return {"status": "Error", "message": "No rooms available", "alert": True}

    for room in avail_rooms:
        a = db.query(RoomAmenity).filter(RoomAmenity.room_id == room.room_id).all()

        r = hotel.Room(
            bed_type = room.bed_type if room.bed_type else "",
            number_of_rooms=room.number_of_available_rooms,
            max_occupancy = room.max_occupancy if room.max_occupancy else 0,
            price = room.price if room.price else 0,
            room_type = room.room_type,
            amenities = convert_room_amenities(a) if a is not None else []
        )
        
        available_rooms.append(r)
    
    h_page = hotel.HotelPage(
        hotel_name = h.hotel_name if h.hotel_name else "",
        amenities = str(h.amenities) if h.amenities else "",
        description = h.description if h.description else "",
        available_rooms = available_rooms,
        photos = hotel_photos 
    )
    
    return {"status": "OK", "message": "Found hotel details", "alert": False, "hotel_page" : h_page}

#works
@router.post('/add_to_wishlist')
def add_to_wishlist(hotel_id: hotel.HotelId, customer = Depends(get_logged_customer),db: Session = Depends(get_db)):
    if customer is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    
    if not db.query(HotelTable).filter(HotelTable.hotel_id == hotel_id.hotel_id).first():
        return {"status": "Error", "message": "hotel not found", "alert": True}
    
    w = Wishlist(
        hotel_id = hotel_id.hotel_id,
        user_id = customer.user_id
    )

    db.add(w)
    db.commit()
    db.refresh(w)

    return {"status": "OK", "message": "added to wishlist successfully", "alert": False}

#works
@router.post('/delete_from_wishlist')
def delete_from_wishlist(hotel_id: hotel.HotelId, customer = Depends(get_logged_customer),db: Session = Depends(get_db)):
    if customer is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    
    if not db.query(HotelTable).filter(HotelTable.hotel_id == hotel_id.hotel_id).first():
        return {"status": "Error", "message": "hotel not found", "alert": True}
    
    w = db.query(Wishlist).filter(and_(Wishlist.hotel_id == hotel_id.hotel_id, Wishlist.user_id == customer.user_id)).first()

    if not w:
        return {"status": "Error", "message": "wishlist entry not found", "alert": True}
    
    db.delete(w)
    db.commit()

    return {"status": "OK", "message": "deleted wishlist entry successfully", "alert": False}

# Works
@router.get('/view_wishlist')
def view_wishlist(customer = Depends(get_logged_customer),db: Session = Depends(get_db)):
    #w = db.query(Wishlist).filter(Wishlist.user_id == customer.user_id).all()
    if customer is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}

    w = (
        db.query(Wishlist,HotelTable).join(HotelTable, Wishlist.hotel_id == HotelTable.hotel_id)
        .filter(Wishlist.user_id == customer.user_id).all()
    )

    if not w:
        return {"status": "Error", "message": "wishlist is empty", "alert": True}
    
    hotel_obj = []
    
    for _,hotel_row in w:
        rating = db.query(func.avg(ReviewTable.rating)).filter(ReviewTable.hotel_id == hotel_row.hotel_id).scalar()
        lowest_price = db.query(func.min(RoomTable.price)).filter(RoomTable.hotel_id == hotel_row.hotel_id).scalar()
        photo = db.query(PhotoTable.photo_url).filter(PhotoTable.hotel_id == hotel_row.hotel_id).first()

        obj = hotel.HotelSearch(
            hotel_id = hotel_row.hotel_id,
            address = hotel_row.address if hotel_row.address else "",
            amenities = str(hotel_row.amenities) if hotel_row.amenities else "",
            hotel_name = hotel_row.hotel_name if hotel_row.hotel_name else "",
            lowest_price = lowest_price if lowest_price is not None else 0,
            rating = rating if rating is not None else 0,
            img_path = photo[0] if photo is not None else "",  
            is_wishlisted = True
        )
        
        hotel_obj.append(obj)

    
    return {"status": "OK", "message": "Found hotels in wishlist", "alert": False, "wishlist" : hotel_obj}
    
    
    

    

    

    

    

    