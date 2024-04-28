from pydantic import BaseModel
from typing import List
from fastapi import UploadFile,File

class RoomAmenities(BaseModel):
    amenity: str
    quality: str

class Room(BaseModel):
    room_type: int
    total_rooms: int
    bed_type: str
    max_occupancy: int
    price: float
    room_amenities: int

class Hotel(BaseModel):
    hotel_name: str
    description: str
    property_paper_path: str
    pincode: str
    locality: str
    address: str
    city: str
    state: str
    country: str
    amenities: int
    tag_list: str
    rooms: List[Room]
    property_images: List[str]


class PropertyPaper(BaseModel):
    hotel_id: int
    property_paper: UploadFile = File(...)

class HotelPhotos(BaseModel):
    hotel_id: int
    photos: List[UploadFile]

class HotelStatistics(BaseModel):
    avg_rating: int
    total_bookings: int
    earnings: float
    days_of_stay: int

class HotelSearch(BaseModel):
    hotel_id: int
    hotel_name: str
    address: str
    amenities: str
    lowest_price: float
    rating: int
    img_path: str
    is_wishlisted: bool

class HotelPage(BaseModel):
    hotel_name: str
    description: str
    amenities: str
    photos: List[str]
    available_rooms: List[Room]

class DateRange(BaseModel):
    start_date: str
    end_date: str

class HotelPageQuery(BaseModel):
    hotel_id: int
    date_range: DateRange

class SearchQuery(BaseModel):
    text: str
    date_range: str

class SearchQueryWithFilter(BaseModel):
    text: str
    date_range: str
    filters: str

class HotelId(BaseModel):
    hotel_id: int

    
