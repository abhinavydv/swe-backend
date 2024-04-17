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
    prefix="/search",
    tags=["search"],
)

@router.post('/{city}')
def get_hotels(city: str):
    pass

@router.post('/filters')
def get_hotels_with_filters():
    pass
    