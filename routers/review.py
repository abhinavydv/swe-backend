from fastapi import APIRouter, Depends, Response, Cookie
from sqlalchemy.orm import Session
from sqlalchemy import update,func
from config.db import get_db
from models import hotel,booking,user
from schema.hotel import Hotel as HotelTable
from schema.booking import Booking as BookingTable
from schema.user import User as UserTable
from schema.review import Review as ReviewTable
from routers.user import get_logged_partner,get_logged_customer
from datetime import date

router = APIRouter(
    prefix="/review",
    tags=["review"],
)

@router.post('/submit_review')
def submit_review(review: booking.Review, customer = Depends(get_logged_customer), db: Session = Depends(get_db)):
    if customer is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    b = db.query(BookingTable).filter(BookingTable.booking_id == review.booking_id and BookingTable.user_id == customer.user_id).first()

    if not b:
        return {"status": "Error", "message": "booking not found", "alert": True}
    
    today = date.today().strftime("%Y-%m-%d")
    if today <= b.to_date.strftime("%Y-%m-%d"):
        return {"status": "Error", "message": "Stay not completed", "alert": True}
    
    rev = ReviewTable(
        booking_id = review.booking_id,
        user_id = customer.user_id,
        hotel_id = b.hotel_id,
        title = review.title,
        description = review.description,
        rating = review.rating
    )

    db.add(rev)
    db.commit()

    return {"status": "OK", "message": "review submitted successfully", "alert": False}

@router.post('/delete_review')
def delete_review(booking_id: booking.BookingID, customer = Depends(get_logged_customer), db: Session = Depends(get_db)):
    if customer is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    rev = db.query(ReviewTable).filter(ReviewTable.booking_id == booking_id.booking_id and ReviewTable.user_id == customer.user_id).first()

    if not rev:
        return {"status": "Error", "message": "review not found", "alert": True}
    
    db.delete(rev)
    db.commit()

    return {"status": "OK", "message": "review deleted successfully", "alert": False}

@router.post('/get_review')
def get_review(booking_id, customer = Depends(get_logged_customer), db: Session = Depends(get_db)):
    if customer is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    rev = db.query(ReviewTable).filter(ReviewTable.booking_id == booking_id and ReviewTable.user_id == customer.user_id).first()

    if not rev:
        return {"status": "Error", "message": "review not found", "alert": True}
    
    return {"status": "OK", "message": "review found", "alert": False, "reviews": rev}


@router.get('/view_reviews')
def get_all_reviews(hotel_id,partner = Depends(get_logged_partner), db: Session = Depends(get_db)):
    if partner is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    
    revs = db.query(ReviewTable).filter(ReviewTable.hotel_id == hotel_id and ReviewTable.user_id == partner.user_id).all()

    if not revs:
        return {"status": "Error", "message": "reviews not found", "alert": True}
    
    return {"status": "OK", "message": "reviews found", "alert": False, "reviews": revs}


@router.post('/get_statistics')
def get_hotel_statistics(hotel_id,partner = Depends(get_logged_partner), db: Session = Depends(get_db)):
    if partner is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    
    h = db.query(HotelTable).filter(HotelTable.hotel_id == hotel_id and HotelTable.owner_id == partner.user_id).first()
    if not h:
        return {"status": "Error", "message": "hotel not found", "alert": True}
    
    h_stat = hotel.HotelStatistics(
        avg_rating = db.query(func.avg(ReviewTable.rating)).filter(ReviewTable.hotel_id == hotel_id).scalar(),
        total_bookings = db.query(func.count(BookingTable.booking_id)).filter(BookingTable.hotel_id == hotel_id).scalar(),
        earnings = db.query(func.sum(BookingTable.amount)).filter(BookingTable.hotel_id == hotel_id).scalar(),
        days_of_stay = db.query(func.sum(func.age(BookingTable.check_out_date - BookingTable.check_in_date))).filter(BookingTable.hotel_id == hotel_id).scalar()
    )
    
    return {"status": "OK", "message": "statistics calculated", "alert": False, "statistics": h_stat}
    
    
    # avg_rating
    # total bookings
    # total money earnt
    # days of stay over all bookings
    