-- Users
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
	email_id VARCHAR(255),
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255),
    password VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
	profile_image_path VARCHAR(255)
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
    FOREIGN KEY (owner_id) REFERENCES users(user_id)   -- Foreign Key

);

-- KYP
CREATE TABLE kyp (
	user_id INTEGER PRIMARY KEY,
	pan_number VARCHAR(255) ,
	aadhar_photo_path VARCHAR(255),
	hotelling_license VARCHAR(255),
	account_number VARCHAR(512),
    ifsc_code VARCHAR(512),
    FOREIGN KEY (user_id) REFERENCES users(user_id)  -- Foreign Key

);

-- Room
CREATE TABLE rooms (
	room_id SERIAL PRIMARY KEY,
	hotel_id INTEGER NOT NULL,
	room_type INTEGER NOT NULL,
	price FLOAT NOT NULL,
	number_of_rooms INTEGER,
    amenities INTEGER,
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id)  -- Foreign Key
	
);

-- Booking
CREATE TABLE bookings (
	booking_id SERIAL PRIMARY KEY,
	hotel_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	amount FLOAT NOT NULL,
	from_date DATE NOT NULL,
	to_date  DATE NOT NULL,
	room_type INTEGER NOT NULL,
    number_of_rooms INTEGER DEFAULT 1,
    status SMALLINT,
    transaction_id INTEGER,
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id),  -- Foreign Key
    FOREIGN KEY (user_id) REFERENCES users(user_id)   -- Foreign Key
);

-- Guest Profiles
CREATE TABLE guest_profiles (
	guest_id SERIAL PRIMARY KEY,
	guest_name VARCHAR(255) NOT NULL,
	user_id INTEGER NOT NULL,
    age INTEGER,
    gender VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id)   -- Foreign Key
	
);

-- Booking guests
CREATE TABLE booking_guests (
	booking_id INTEGER NOT NULL,
	guest_id INTEGER NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id), -- Foreign Key
    FOREIGN KEY (guest_id) REFERENCES guest_profiles(guest_id), -- Foreign Key
    PRIMARY KEY (booking_id,guest_id)
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
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id),  -- Foreign Key
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id),       -- Foreign Key
    FOREIGN KEY (user_id) REFERENCES users(user_id)           -- Foreign Key
);

-- Wishlist
CREATE TABLE wishlist (
    user_id INTEGER NOT NULL,
	hotel_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),  -- Foreign Key
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id),   -- Foreign Key
    PRIMARY KEY (user_id,hotel_id)
);

-- Hotel Photos
CREATE TABLE hotel_photos (
    photo_id SERIAL PRIMARY KEY,
    hotel_id INTEGER NOT NULL,
    photo_url VARCHAR(255) NOT NULL,
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id)    -- Foreign Key
);

-- Tags
CREATE TABLE tags (
    tag_id SERIAL PRIMARY KEY,
    tag_name VARCHAR(255) NOT NULL
);

-----