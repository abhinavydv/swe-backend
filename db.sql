-- Users
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
	email_id VARCHAR(255),
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255),
    dob VARCHAR(255),
    phone_number VARCHAR(255),
    gender VARCHAR(255),
    nationality VARCHAR(255),
    password VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    role VARCHAR(255),
	profile_image_path VARCHAR(255),
    cookie VARCHAR(255)
);

-- Hotel
CREATE TABLE hotels (
	hotel_id SERIAL PRIMARY KEY,
	hotel_name VARCHAR(255) NOT NULL,
    owner_id INTEGER NOT NULL,
    property_paper_path VARCHAR(255),
	description TEXT,
	pincode VARCHAR(255) NOT NULL,
	locality VARCHAR(255),
	address TEXT NOT NULL,
    city VARCHAR(255) NOT NULL,
    state VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL,
    amenities INTEGER NOT NULL,
    tag_list VARCHAR(512),
    FOREIGN KEY (owner_id) REFERENCES users(user_id) ON DELETE CASCADE -- Foreign Key

);

-- KYP
CREATE TABLE kyp (
	user_id INTEGER PRIMARY KEY,
	pan_number VARCHAR(255) ,
	aadhar_photo_path VARCHAR(255),
	hotelling_license VARCHAR(255),
	account_number VARCHAR(512),
    ifsc_code VARCHAR(512),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE  -- Foreign Key

);

-- Room
CREATE TABLE rooms (
	room_id SERIAL PRIMARY KEY,
	hotel_id INTEGER NOT NULL,
	room_type INTEGER NOT NULL,
	price FLOAT NOT NULL,
	number_of_available_rooms INTEGER,
    total_rooms INTEGER,
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id) ON DELETE CASCADE  -- Foreign Key
	
);

-- Room Amenities
CREATE TABLE rooms_amenities (
	room_id INTEGER NOT NULL,
	amenity VARCHAR(255) NOT NULL,
    quality VARCHAR(255),
    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE CASCADE,  -- Foreign Key
    PRIMARY KEY (room_id,amenity)
	
);

-- Booking
CREATE TABLE bookings (
	booking_id SERIAL PRIMARY KEY,
	hotel_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	amount FLOAT NOT NULL,
	from_date DATE NOT NULL,
	to_date  DATE NOT NULL,
	status SMALLINT,
    transaction_id INTEGER,
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id) ON DELETE CASCADE,  -- Foreign Key
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE   -- Foreign Key
);

-- Guest Profiles
CREATE TABLE guest_profiles (
	guest_id SERIAL PRIMARY KEY,
	guest_name VARCHAR(255) NOT NULL,
	user_id INTEGER NOT NULL,
    age INTEGER,
    gender VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE   -- Foreign Key
	
);

-- Booking guests
CREATE TABLE booking_guests (
	booking_id INTEGER NOT NULL,
	guest_id INTEGER NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE, -- Foreign Key
    FOREIGN KEY (guest_id) REFERENCES guest_profiles(guest_id) ON DELETE CASCADE, -- Foreign Key
    PRIMARY KEY (booking_id,guest_id)
);

-- Booking rooms
CREATE TABLE booking_rooms (
	booking_id INTEGER NOT NULL,
	room_id INTEGER NOT NULL,
    room_type INTEGER NOT NULL,
    number_of_rooms INTEGER NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE, -- Foreign Key
    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE CASCADE, -- Foreign Key
    PRIMARY KEY (booking_id,room_id)
);

-- Reviews
CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY,
	booking_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	hotel_id INTEGER NOT NULL,
	title VARCHAR(255),
	description TEXT,
    rating INTEGER,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE,  -- Foreign Key
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id) ON DELETE CASCADE      -- Foreign Key
);

-- Wishlist
CREATE TABLE wishlist (
    user_id INTEGER NOT NULL,
	hotel_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,  -- Foreign Key
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id) ON DELETE CASCADE,   -- Foreign Key
    PRIMARY KEY (user_id,hotel_id)
);

-- Hotel Photos
CREATE TABLE hotel_photos (
    photo_id SERIAL PRIMARY KEY,
    hotel_id INTEGER NOT NULL,
    photo_url VARCHAR(255) NOT NULL,
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id) ON DELETE CASCADE   -- Foreign Key
);

-- Tags
CREATE TABLE tags (
    tag_id SERIAL PRIMARY KEY,
    tag_name VARCHAR(255) NOT NULL
);

-----
-- DROP TABLE users;
-- DROP TABLE hotels;
-- DROP TABLE hotel_photos;
-- DROP TABLE tags;
-- DROP TABLE bookings;
-- DROP TABLE booking_guests;
-- DROP TABLE wishlist;
-- DROP TABLE reviews;
-- DROP TABLE kyp;
-- DROP TABLE guest_profiles;
-- DROP TABLE rooms;
