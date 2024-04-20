from pydantic import BaseModel


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

class Room(BaseModel):
    room_type: int
    number_of_rooms: int
    price: float
    amenities: str

class HotelSearch(BaseModel):
    hotel_id: int
    hotel_name: int
    address: str
    amenities: str
    lowest_price: float
    rating: int
    img_path: str

class SearchQuery(BaseModel):
    text: str
    check_in_date: str
    check_out_date: str
    filters: str

    
