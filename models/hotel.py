from pydantic import BaseModel


class Hotel(BaseModel):
    owner_id: int
    hotel_name: str
    property_paper_path: str
    description: str
    pincode: str
    locality: str
    address: str
    city: str
    state: str
    country: str
    amenities: int
    tag_list: str
