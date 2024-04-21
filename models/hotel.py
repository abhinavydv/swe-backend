from pydantic import BaseModel
from typing import List


class Hotel(BaseModel):
    hotel_name: str
    property_paper_path: str
    description: str
    pincode: str
    locality: str
    address: str
    city: str
    state: str
    country: str
    amenities: str
    tag_list: str

class RoomAmenities(BaseModel):
    amenity: str
    quality: str

class Room(BaseModel):
    room_type: int
    number_of_rooms: int
    bed_type: str
    max_occupancy: int
    price: float
    amenities: List[RoomAmenities]


class HotelSearch(BaseModel):
    hotel_id: int
    hotel_name: int
    address: str
    amenities: str
    lowest_price: float
    rating: int
    img_path: str

class HotelPage(BaseModel):
    hotel_name: str
    description: str
    amenities: str
    photos: List[str]
    available_rooms: List[Room]

class DateRange(BaseModel):
    start_date: str
    end_date: str

class SearchQuery(BaseModel):
    text: str
    date_range: DateRange

class SearchQueryWithFilter(BaseModel):
    text: str
    date_range: DateRange
    filters: str



    
