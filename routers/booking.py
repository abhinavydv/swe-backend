from fastapi import APIRouter, Depends, Response, Cookie
from sqlalchemy.orm import Session
from sqlalchemy import update,or_,and_
from config.db import get_db
from models import hotel,booking,user
from schema.hotel import Hotel as HotelTable
from datetime import datetime
from schema.room import Room as RoomTable
from schema.user import User as UserTable
from schema.booking import Booking as BookingTable
from schema.booking_guest import BookingGuest
from schema.guest_profile import GuestProfile
from schema.review import Review as ReviewTable
from schema.booking_room import BookingRoom
from routers.search import get_available_rooms
from routers.user import get_logged_partner,get_logged_customer
from typing import List

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
)

def get_available_room_by_type(available_rooms,room_type):
    # Iterate through the result set and find the row with the specified room_id
    for row in available_rooms:
        if row.room_type == room_type:
            return row
    
    # If room_id is not found, return None or handle accordingly
    return None

# works
@router.post('/add_guest')
def add_guest_profile(guest: booking.GuestProfile,customer = Depends(get_logged_customer), db: Session = Depends(get_db)):
    if customer is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    
    g = GuestProfile(
        user_id = customer.user_id,
        guest_name = guest.guest_name,
        gender = guest.gender,
        age = guest.age
    )
    db.add(g)
    db.commit()
    db.refresh(g)
    return {"status": "OK", "message": "Guest added successfully", "alert": False}

# works
@router.post('/edit_guest')
def edit_guest_profile(guest: booking.EditGuestProfile,customer = Depends(get_logged_customer), db: Session = Depends(get_db)):
    if customer is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    
    g = db.query(GuestProfile).filter(and_(GuestProfile.guest_id == guest.guest_id ,GuestProfile.user_id == customer.user_id)).first()
    if not g:
        return {"status": "Error", "message": "guest not found", "alert": True}
    
    stmt = update(GuestProfile).where(GuestProfile.guest_id == guest.guest_id).values(
        guest_name = guest.guest_name,
        gender = guest.gender,
        age = guest.age
    )

    db.execute(stmt)
    db.commit()

    return {"status": "OK", "message": "Guest edited successfully", "alert": False}

# works
@router.post('/delete_guest')
def delete_guest_profile(guest_id: int, customer = Depends(get_logged_customer), db: Session = Depends(get_db)):
    if customer is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    
    g = db.query(GuestProfile).filter(and_(GuestProfile.guest_id == guest_id,GuestProfile.user_id == customer.user_id)).first()
    if not g:
        return {"status": "Error", "message": "guest not found", "alert": True}
    
    db.delete(g)
    db.commit()

    return {"status": "OK", "message": "Guest deleted successfully", "alert": False}

# works
@router.get('/get_guests')
def get_guests(customer = Depends(get_logged_customer), db: Session = Depends(get_db)):
   if customer is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
   
   g = db.query(GuestProfile).filter(GuestProfile.user_id == customer.user_id).all()

   if not g:
       return {"status": "Error", "message": "no guests found", "alert": True}
   
   return {"status": "OK", "message": "Guests found", "alert": False, "guests": g}


# works
# Need to test more
@router.post('/book')
def book_hotel(details: booking.BookingDetails, customer = Depends(get_logged_customer), db: Session = Depends(get_db)):
    if customer is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    
    h = db.query(HotelTable).filter(details.hotel_id == HotelTable.hotel_id).first()
    if not h:
        return {"status": "Error", "message": "hotel not found", "alert": True}
    
    rooms = []

    dates = details.date_range.split('__')

    start_date = datetime.strptime(dates[0], "%Y-%m-%d")
    end_date = datetime.strptime(dates[1],"%Y-%m-%d")

    available_rooms = get_available_rooms(details.hotel_id,start_date,end_date,db)
    
    for room in details.rooms:
        a_room = get_available_room_by_type(available_rooms,room.room_type)
        if not a_room:
            return {"status": "Error", "message": "room type not found", "alert": True}
        
        if a_room.number_of_available_rooms < room.number_of_rooms:
            return {"status": "Error", "message": "rooms not available", "alert": True}

        
        rooms.append(a_room.room_id)
    
    b = BookingTable(
        user_id = customer.user_id,
        hotel_id = details.hotel_id,
        amount = details.bill,
        from_date = start_date,
        to_date = end_date,
        status = 0,
        transaction_id = details.transaction_id
    )

    db.add(b)
    db.commit()
    
    booking_id = b.booking_id

    for i in range(len(details.rooms)):
        r = BookingRoom(
            booking_id = booking_id,
            room_id = rooms[i],
            room_type = details.rooms[i].room_type,
            number_of_rooms = details.rooms[i].number_of_rooms

        )

        db.add(r)

    for guest in details.guests:
        g = BookingGuest(
            booking_id = booking_id,
            guest_id = guest
        )

        db.add(g)
    
    db.commit()

    return {"status": "OK", "message": "booking successful", "alert": False}

# works
@router.post('/cancel')
def cancel_booking(booking_id: int ,customer = Depends(get_logged_customer), db: Session = Depends(get_db)):
    if customer is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    
    b = db.query(BookingTable).filter(and_(BookingTable.booking_id == booking_id,BookingTable.user_id == customer.user_id)).first()
    if not b:
        return {"status": "Error", "message": "booking not found", "alert": True}
    
    rooms = db.query(BookingRoom).filter(BookingRoom.booking_id == booking_id).all()
    if not rooms:
        return {"status": "Error", "message": "rooms not found", "alert": True}
    
    for room in rooms:
        db.delete(room)
    
    b.status = -1
    
    db.commit()

    return {"status": "OK", "message": "booking cancellation successful", "alert": False}

# works
@router.post('/get_booking')
def get_booking_details(booking_id: int, customer = Depends(get_logged_customer), db: Session = Depends(get_db)):
    if customer is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    
    b = db.query(BookingTable).filter(and_(BookingTable.booking_id == booking_id,BookingTable.user_id == customer.user_id)).first()
    if not b:
        return {"status": "Error", "message": "booking not found", "alert": True}
    
    return {"status": "OK", "message": "booking found", "alert": False, "booking": b}

# need to test more once booking data is added.
@router.get('/past_bookings')
def get_past_bookings(customer = Depends(get_logged_customer), db: Session = Depends(get_db)):
    if customer is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    
    b = ( 
            db.query(BookingTable,ReviewTable,HotelTable)
            .join(ReviewTable, BookingTable.booking_id == ReviewTable.booking_id)
            .join(HotelTable, BookingTable.hotel_id == HotelTable.hotel_id)
            .filter(BookingTable.user_id == customer.user_id).all()
        )

    if not b:
        return {"status": "Error", "message": "no past bookings", "alert": True}
    
    bookings = []

    for book,rev,h in b:
      
        book = booking.PastBooking(
            booking_id=book.booking_id,
            hotel_id=h.hotel_id,
            hotel_name=h.hotel_name if h.hotel_name else "",
            hotel_location=h.address if h.address else "",
            check_in_date=str(book.from_date) if book.from_date else "",
            check_out_date=str(book.to_date) if book.to_date else "",
            bill=book.bill if book.bill else 0,
            reviewExists=True if rev.description is not None else False,
            review=rev.description if rev.description is not None else "",
            rating= rev.rating if rev.rating is not None else 0
        )

        bookings.append(book)

    
    return {"status": "OK", "message": "past bookings found", "alert": False, "past_bookings": bookings}


