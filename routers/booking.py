from fastapi import APIRouter, Depends, Response, Cookie
from sqlalchemy.orm import Session
from config.db import get_db
from models import hotel
from schema.hotel import Hotel as HotelTable
from schema.room import Room as RoomTable
from schema.user import User as UserTable
from routers.user import get_logged_partner,get_logged_customer
from typing import List

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
)

# All booking related functions
# Reviews
# Hotel perforamnce metrics