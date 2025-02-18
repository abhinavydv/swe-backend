import traceback
from fastapi import APIRouter, Depends, Response, Cookie
from sqlalchemy.orm import Session
from sqlalchemy import delete, update,or_,and_
from config.db import get_db
from models import hotel
from schema.hotel import Hotel as HotelTable
from schema.room import Room as RoomTable
from schema.user import User as UserTable
from schema.room_amenity import RoomAmenity
from schema.hotel_photo import HotelPhoto as PhotoTable
from routers.user import get_logged_partner
from typing import List
from config.gdrive import create_file
import os

router = APIRouter(
    prefix="/hotels",
    tags=["hotels"],
)

UPLOAD_FOLDER = 'uploads'

# works
@router.post("/add_hotel")
def add_hotel(hotel: hotel.Hotel, owner = Depends(get_logged_partner),db: Session = Depends(get_db)):
    try:
        if owner is None:
            return {"status": "Error", "message": "user not logged in", "alert": True}

        h = HotelTable(
            owner_id = owner.user_id,
            hotel_name = hotel.hotel_name,
            description = hotel.description,
            property_paper_path = hotel.property_paper_path,
            pincode = hotel.pincode,
            locality = hotel.locality,
            address = hotel.address,
            city = hotel.city,
            state = hotel.state,
            country = hotel.country,
            amenities = hotel.amenities,
            tag_list = hotel.tag_list
        )

        db.add(h)
        db.commit()

        hotel_id = h.hotel_id
        
        for room in hotel.rooms:
            r = RoomTable(
                hotel_id = hotel_id,
                room_type = room.room_type,
                bed_type = room.bed_type,
                max_occupancy = room.max_occupancy,
                number_of_available_rooms = room.total_rooms,
                total_rooms = room.total_rooms,
                price = room.price,
                amenities = room.room_amenities
            )

            db.add(r)
            db.commit()
            # room_id = r.room_id
            # for amenity in room.room_amenities:
            #     a = RoomAmenity(
            #         room_id = room_id,
            #         amenity = amenity.amenity,
            #         quality = amenity.quality
            #     )
            #     db.add(a)
        
        for photo in hotel.property_images:
            p = PhotoTable(
                hotel_id = hotel_id,
                photo_url = photo
            )
            db.add(p)
        
        db.commit()

        return {"status": "OK", "message": "Added hotel successfully", "alert": False}
    except Exception as e:
        traceback.print_exc()
        return {"status": "Error", "message": str(e), "alert": True}

# not tested - not used
@router.post('/property_paper')
def add_property_paper(property_paper: hotel.PropertyPaper,partner = Depends(get_logged_partner),db: Session = Depends(get_db)):
    if partner is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}

    h = db.query(HotelTable).filter(and_(HotelTable.hotel_id == property_paper.hotel_id ,HotelTable.owner_id == partner.user_id)).first()

    if not h:
        return {"status": "Error", "message": "hotel not found", "alert": True}

    if not property_paper.property_paper:
        return {"status": "Error", "message": "file not found", "alert": True}

    # Create destination folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER + "/propert_papers", exist_ok=True)

    file_path = os.path.join(UPLOAD_FOLDER + "/property_papers", property_paper.property_paper.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(property_paper.property_paper.file.read())

    property_path = create_file(property_paper.property_paper.filename, file_path)

    #os.remove(file_path)

    h.property_paper_path = property_path if property_path else ""

    db.commit()

    return {"status": "OK", "message": "added property paper", "alert": False}

# not tested    
@router.post('/add_hotel_photos')
def add_hotel_photos(photos: hotel.HotelPhotos,partner = Depends(get_logged_partner),db: Session = Depends(get_db)):
    if partner is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    
    h = db.query(HotelTable).filter(and_(HotelTable.hotel_id == photos.hotel_id ,HotelTable.owner_id == partner.user_id)).first()

    if not h:
        return {"status": "Error", "message": "hotel not found", "alert": True}
    
    # Create destination folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER + "/hotel_photos", exist_ok=True)
    
    for photo in photos:
        if not photo:
            return {"status": "Error", "message": "file not found", "alert": True}

        file_path = os.path.join(UPLOAD_FOLDER + "/hotel_photos", photo.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(photo.file.read())

        image_path = create_file(photo.filename, file_path)

        # os.remove(file_path)

        p = PhotoTable(
            hotel_id = photos.hotel_id,
            photo_url = image_path
        )

        db.add(p)
        db.commit()

    return {"status": "OK", "message": "added hotel photos", "alert": False}


# not tested
@router.post('/edit_hotel/{hotel_id}')
def edit_hotel(hotel_id, hotel: hotel.Hotel,owner = Depends(get_logged_partner),db: Session = Depends(get_db)):
    # Adding photos
    # Tag List parsing
    if owner is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}

    h = db.query(HotelTable).filter(and_(HotelTable.hotel_id == hotel_id ,HotelTable.owner_id == owner.user_id)).first()

    if not h:
        return {"status": "Error", "message": "hotel not found", "alert": True}

    # Update the hotel information with the new data
    h.hotel_name = hotel.hotel_name
    h.description = hotel.description
    h.pincode = hotel.pincode
    h.locality = hotel.locality
    h.address = hotel.address
    h.city = hotel.city
    h.state = hotel.state
    h.country = hotel.country
    h.amenities = hotel.amenities
    h.tag_list = hotel.tag_list

    for room in hotel.rooms:
        r = db.query(RoomTable).filter(and_(RoomTable.hotel_id == hotel_id,RoomTable.room_type==room.room_type)).first()

        # Room type not present add in the rooms db
        if not r:
            r = RoomTable(
                hotel_id = hotel_id,
                room_type = room.room_type,
                bed_type = room.bed_type,
                max_occupancy = room.max_occupancy,
                number_of_available_rooms = room.total_rooms,
                total_rooms = room.total_rooms,
                price = room.price,
                amenities = room.room_amenities
            )
            db.add(r) 

            # for amenity in room.amenities:
            #     a = RoomAmenity(
            #         room_id = r.room_id,
            #         amenity = amenity.amenity,
            #         quality = amenity.quality
            #     )
            #     db.add(a)
            # db.commit()
                
        # update existing room type
        else:
            r.room_type = room.room_type
            r.total_rooms = room.total_rooms
            r.bed_type = room.bed_type
            r.max_occupancy = room.max_occupancy
            r.price = room.price
            r.amenities = room.room_amenities
            # for amenity in room.amenities:
            #     stmt = update(RoomAmenity).where(RoomAmenity.room_id == r.room_id).values(
            #         amenity = amenity.amenity,
            #         quality = amenity.quality
            #     )
            #     db.execute(stmt)

    images_in_db = list(map(lambda img: img.photo_url, db.query(PhotoTable).filter(PhotoTable.hotel_id == hotel_id).all()))
    print(images_in_db, hotel.property_images)
    for image_url in hotel.property_images:
        if image_url not in images_in_db:
            img = PhotoTable(
                hotel_id = hotel_id,
                photo_url = image_url
            )
            db.add(img)

    for image_url in images_in_db:
        if image_url not in hotel.property_images:
            print(image_url)
            stmt = delete(PhotoTable).where(
                PhotoTable.photo_url == image_url,
                PhotoTable.hotel_id == hotel_id
            )
            db.execute(stmt)

    db.commit()

    return {"status": "OK", "message": "Edited hotel successfully", "alert": False}

# change into one object
@router.post('/delete_room_type')
def delete_room(hotel_id,room_type,owner = Depends(get_logged_partner),db: Session = Depends(get_db)):
    if owner is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}

    if not db.query(HotelTable).filter(and_(HotelTable.hotel_id == hotel_id ,HotelTable.owner_id == owner.user_id)).first():
        return {"status": "Error", "message": "hotel not found", "alert": True}

    r = db.query(RoomTable).filter(and_(RoomTable.hotel_id == hotel_id ,RoomTable.room_type==room_type)).first()

    if not r:
        return {"status": "Error", "message": "room type not found", "alert": True}

    db.delete(r)
    db.commit()

    return {"status": "OK", "message": "Deleted room successfully", "alert": False}

# works
@router.post("/view_hotel")
def view_hotel(hotel_id: hotel.HotelId, partner = Depends(get_logged_partner),db: Session = Depends(get_db)):
    if partner is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    h = db.query(HotelTable).filter(and_(HotelTable.hotel_id == hotel_id.hotel_id ,HotelTable.owner_id == partner.user_id)).first()

    if not h:
        return {"status": "Error", "message": "hotel not found", "alert": True}

    return {"status": "OK", "message": "Listing found", "alert": False, "listings": h}

# not tested
@router.get('/view_listings')
def view_listings(partner = Depends(get_logged_partner),db: Session = Depends(get_db)):
    if partner is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}
    h = db.query(HotelTable).filter(HotelTable.owner_id == partner.user_id).all()

    if not h:
        return {"status": "Error", "message": "hotels not found", "alert": True}

    return {"status": "OK", "message": "Listing found", "alert": False, "listings": h}

# works
@router.post('/delete_hotel')
def delete_hotel(hotel_id: hotel.HotelId, owner = Depends(get_logged_partner),db: Session = Depends(get_db)):
    if owner is None:
        return {"status": "Error", "message": "user not logged in", "alert": True}

    h = db.query(HotelTable).filter(and_(HotelTable.hotel_id == hotel_id.hotel_id ,HotelTable.owner_id == owner.user_id)).first()

    if not h:
        return {"status": "Error", "message": "hotel not found", "alert": True}

    db.delete(h)

    db.commit()

    return {"status": "OK", "message": "Deleted room successfully", "alert": False}


@router.post("/get_rooms")
def get_rooms(hotel_id: hotel.HotelId, db: Session = Depends(get_db)):
    rooms = db.query(RoomTable).filter(RoomTable.hotel_id == hotel_id.hotel_id).all()

    return {"status": "OK", "message": "Rooms found", "alert": False, "rooms": rooms}


@router.post("/get_images")
def get_images(hotel_id: hotel.HotelId, db: Session = Depends(get_db)):
    photos = db.query(PhotoTable).filter(PhotoTable.hotel_id == hotel_id.hotel_id).all()

    return {"status": "OK", "message": "Images found", "alert": False, "images": photos}
