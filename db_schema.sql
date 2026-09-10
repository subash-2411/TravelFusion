-- TravelFusion AI Database Schema
-- Compatible with MySQL and SQLite (via standard translation in database.py)

CREATE DATABASE IF NOT EXISTS travelfusion_db;
USE travelfusion_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. UserProfiles Table
CREATE TABLE IF NOT EXISTS UserProfiles (
    user_id INT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    avatar_url VARCHAR(255) DEFAULT '/static/images/default-avatar.png',
    default_budget DECIMAL(10,2) DEFAULT 2000.00,
    default_first_mile VARCHAR(20) DEFAULT 'auto',
    default_last_mile VARCHAR(20) DEFAULT 'auto',
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- 3. Drivers Table
CREATE TABLE IF NOT EXISTS Drivers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    license_number VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NULL,
    is_online INT DEFAULT 0, -- 0: Offline, 1: Online
    rating DECIMAL(3,2) DEFAULT 5.00,
    balance DECIMAL(10,2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, blocked
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Vehicles Table
CREATE TABLE IF NOT EXISTS Vehicles (
    driver_id INT PRIMARY KEY,
    vehicle_type VARCHAR(20) NOT NULL, -- auto, cab, bike
    vehicle_number VARCHAR(20) UNIQUE NOT NULL,
    vehicle_model VARCHAR(50) NOT NULL,
    FOREIGN KEY (driver_id) REFERENCES Drivers(id) ON DELETE CASCADE
);

-- 5. TravelPlans Table
CREATE TABLE IF NOT EXISTS TravelPlans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    source VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    travel_date DATE NOT NULL,
    budget DECIMAL(10,2) NOT NULL,
    search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- 6. Bookings Table
CREATE TABLE IF NOT EXISTS Bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    travel_plan_id INT NOT NULL,
    user_id INT NOT NULL,
    total_fare DECIMAL(10,2) NOT NULL,
    passenger_name VARCHAR(100) NULL,
    passenger_age INT NULL,
    passenger_gender VARCHAR(20) NULL,
    passenger_phone VARCHAR(20) NULL,
    passenger_email VARCHAR(255) NULL,
    status VARCHAR(20) DEFAULT 'upcoming', -- upcoming, active, completed, cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (travel_plan_id) REFERENCES TravelPlans(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- 6a. BookingPassengers Table (For Multi-passenger support)
CREATE TABLE IF NOT EXISTS BookingPassengers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    passenger_name VARCHAR(100) NOT NULL,
    passenger_age INT NOT NULL,
    passenger_gender VARCHAR(20) NOT NULL,
    seat_number VARCHAR(10) NULL,
    FOREIGN KEY (booking_id) REFERENCES Bookings(id) ON DELETE CASCADE
);

-- 7. BusBookings Table
CREATE TABLE IF NOT EXISTS BusBookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    bus_number VARCHAR(20) NOT NULL,
    operator_name VARCHAR(100) NOT NULL,
    seat_number VARCHAR(10) NOT NULL,
    departure_time DATETIME NOT NULL,
    arrival_time DATETIME NOT NULL,
    fare DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES Bookings(id) ON DELETE CASCADE
);

-- 8. TrainBookings Table
CREATE TABLE IF NOT EXISTS TrainBookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    train_number VARCHAR(20) NOT NULL,
    train_name VARCHAR(100) NOT NULL,
    coach_number VARCHAR(10) NOT NULL,
    seat_number VARCHAR(10) NOT NULL,
    departure_time DATETIME NOT NULL,
    arrival_time DATETIME NOT NULL,
    fare DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES Bookings(id) ON DELETE CASCADE
);

-- 9. FlightBookings Table
CREATE TABLE IF NOT EXISTS FlightBookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    flight_number VARCHAR(20) NOT NULL,
    airline_name VARCHAR(100) NOT NULL,
    seat_number VARCHAR(10) NOT NULL,
    gate VARCHAR(10) NOT NULL,
    departure_time DATETIME NOT NULL,
    arrival_time DATETIME NOT NULL,
    fare DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES Bookings(id) ON DELETE CASCADE
);

-- 10. RideBookings Table
CREATE TABLE IF NOT EXISTS RideBookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    driver_id INT NULL,
    vehicle_type VARCHAR(20) NOT NULL, -- auto, cab, bike
    fare DECIMAL(10,2) NOT NULL,
    otp VARCHAR(6) NOT NULL,
    status VARCHAR(20) DEFAULT 'requested', -- requested, accepted, active, completed, rejected
    rating INT DEFAULT NULL,
    feedback TEXT DEFAULT NULL,
    FOREIGN KEY (booking_id) REFERENCES Bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (driver_id) REFERENCES Drivers(id) ON DELETE SET NULL
);

-- 11. Notifications Table
CREATE TABLE IF NOT EXISTS Notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    is_read INT DEFAULT 0, -- 0: Unread, 1: Read
    notification_type VARCHAR(20) NOT NULL, -- booking, emergency, promo, general
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- 12. EmergencyContacts Table
CREATE TABLE IF NOT EXISTS EmergencyContacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    relationship VARCHAR(50) NOT NULL,
    is_active INT DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- 13. EmergencyAlerts Table
CREATE TABLE IF NOT EXISTS EmergencyAlerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    booking_id INT NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    status VARCHAR(20) DEFAULT 'active', -- active, resolved
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (booking_id) REFERENCES Bookings(id) ON DELETE SET NULL
);

-- 14. TripTracking Table
CREATE TABLE IF NOT EXISTS TripTracking (
    booking_id INT PRIMARY KEY,
    current_latitude DECIMAL(10, 7) NOT NULL,
    current_longitude DECIMAL(10, 7) NOT NULL,
    current_leg VARCHAR(50) NOT NULL, -- first_mile, long_distance, last_mile, completed
    eta_minutes INT NOT NULL,
    status VARCHAR(50) NOT NULL, -- in_transit, boarding, delayed, completed
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES Bookings(id) ON DELETE CASCADE
);

-- 15. TravelHistory Table
CREATE TABLE IF NOT EXISTS TravelHistory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    booking_id INT NOT NULL,
    travel_date DATE NOT NULL,
    source VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    fare DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (booking_id) REFERENCES Bookings(id) ON DELETE CASCADE
);

-- 16. Admin Table
CREATE TABLE IF NOT EXISTS Admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    last_login TIMESTAMP NULL
);

-- 17. Payments Table
CREATE TABLE IF NOT EXISTS Payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    razorpay_order_id VARCHAR(100) NULL,
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES Bookings(id) ON DELETE CASCADE
);

-- 18. Transactions Table
CREATE TABLE IF NOT EXISTS Transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    payment_id INT NOT NULL,
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    method VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'success',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (payment_id) REFERENCES Payments(id) ON DELETE CASCADE
);

-- 19. Tickets Table
CREATE TABLE IF NOT EXISTS Tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    ticket_file_path VARCHAR(255) NOT NULL,
    qr_code_path VARCHAR(255) NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES Bookings(id) ON DELETE CASCADE
);

-- 20. Cancellations Table
CREATE TABLE IF NOT EXISTS Cancellations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    cancellation_id VARCHAR(50) UNIQUE NOT NULL,
    reason TEXT NULL,
    refund_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES Bookings(id) ON DELETE CASCADE
);

-- ==========================================
-- SEED DATA FOR DEMONSTRATION & TESTING
-- ==========================================

-- Seed Admin
INSERT INTO Admin (username, email, password_hash)
VALUES ('Narmu', 'Narmu@travelfusion.ai', 'pbkdf2:sha256:260000$adminhashpwd');

-- Seed Users
INSERT INTO Users (id, email, phone, password_hash, status) VALUES (1, 'user1@gmail.com', '+919876543210', 'pbkdf2:sha256:260000$adminhashpwd', 'active');
INSERT INTO Users (id, email, phone, password_hash, status) VALUES (2, 'user2@gmail.com', '+919999999999', 'pbkdf2:sha256:260000$adminhashpwd', 'active');

INSERT INTO UserProfiles (user_id, full_name, avatar_url, default_budget, default_first_mile, default_last_mile)
VALUES (1, 'Steve Rogers', '/static/images/avatar1.png', 3500.00, 'cab', 'auto');
INSERT INTO UserProfiles (user_id, full_name, avatar_url, default_budget, default_first_mile, default_last_mile)
VALUES (2, 'Bruce Wayne', '/static/images/avatar2.png', 10000.00, 'cab', 'cab');

-- Seed Drivers (Exactly 10 Demo Drivers as per specification)

-- AUTO DRIVERS
INSERT INTO Drivers (id, name, phone, license_number, password_hash, is_online, rating, balance, status)
VALUES (1, 'Murugan', '+919111111111', 'DL-AUTO-001', 'pbkdf2:sha256:260000$adminhashpwd', 1, 4.8, 150.00, 'approved');
INSERT INTO Vehicles (driver_id, vehicle_type, vehicle_number, vehicle_model) VALUES (1, 'auto', 'KA-01-A-1111', 'Bajaj RE E-Tec');

INSERT INTO Drivers (id, name, phone, license_number, password_hash, is_online, rating, balance, status)
VALUES (2, 'Selvakumar', '+919111111112', 'DL-AUTO-002', 'pbkdf2:sha256:260000$adminhashpwd', 1, 4.6, 120.00, 'approved');
INSERT INTO Vehicles (driver_id, vehicle_type, vehicle_number, vehicle_model) VALUES (2, 'auto', 'KA-01-A-2222', 'TVS King');

INSERT INTO Drivers (id, name, phone, license_number, password_hash, is_online, rating, balance, status)
VALUES (3, 'Arul Raj', '+919111111113', 'DL-AUTO-003', 'pbkdf2:sha256:260000$adminhashpwd', 1, 4.9, 300.00, 'approved');
INSERT INTO Vehicles (driver_id, vehicle_type, vehicle_number, vehicle_model) VALUES (3, 'auto', 'KA-01-A-3333', 'Piaggio Ape');

INSERT INTO Drivers (id, name, phone, license_number, password_hash, is_online, rating, balance, status)
VALUES (4, 'Vignesh', '+919111111114', 'DL-AUTO-004', 'pbkdf2:sha256:260000$adminhashpwd', 1, 4.5, 80.00, 'approved');
INSERT INTO Vehicles (driver_id, vehicle_type, vehicle_number, vehicle_model) VALUES (4, 'auto', 'KA-01-A-4444', 'Bajaj Maxima');

-- CAB DRIVERS
INSERT INTO Drivers (id, name, phone, license_number, password_hash, is_online, rating, balance, status)
VALUES (5, 'Kavin Raj', '+919222222222', 'DL-CAB-001', 'pbkdf2:sha256:260000$adminhashpwd', 1, 4.9, 820.00, 'approved');
INSERT INTO Vehicles (driver_id, vehicle_type, vehicle_number, vehicle_model) VALUES (5, 'cab', 'KA-03-C-5555', 'Maruti Suzuki Dzire');

INSERT INTO Drivers (id, name, phone, license_number, password_hash, is_online, rating, balance, status)
VALUES (6, 'Harish', '+919222222223', 'DL-CAB-002', 'pbkdf2:sha256:260000$adminhashpwd', 1, 4.8, 620.00, 'approved');
INSERT INTO Vehicles (driver_id, vehicle_type, vehicle_number, vehicle_model) VALUES (6, 'cab', 'KA-03-C-6666', 'Hyundai Aura');

INSERT INTO Drivers (id, name, phone, license_number, password_hash, is_online, rating, balance, status)
VALUES (7, 'Nithin Kumar', '+919222222224', 'DL-CAB-003', 'pbkdf2:sha256:260000$adminhashpwd', 1, 4.7, 450.00, 'approved');
INSERT INTO Vehicles (driver_id, vehicle_type, vehicle_number, vehicle_model) VALUES (7, 'cab', 'KA-03-C-7777', 'Tata Tigor EV');

-- BIKE DRIVERS
INSERT INTO Drivers (id, name, phone, license_number, password_hash, is_online, rating, balance, status)
VALUES (8, 'Rithvik', '+919333333333', 'DL-BIKE-001', 'pbkdf2:sha256:260000$adminhashpwd', 1, 4.7, 45.00, 'approved');
INSERT INTO Vehicles (driver_id, vehicle_type, vehicle_number, vehicle_model) VALUES (8, 'bike', 'KA-05-B-8888', 'Ola S1 Pro');

INSERT INTO Drivers (id, name, phone, license_number, password_hash, is_online, rating, balance, status)
VALUES (9, 'Dharshan', '+919333333334', 'DL-BIKE-002', 'pbkdf2:sha256:260000$adminhashpwd', 1, 4.5, 35.00, 'approved');
INSERT INTO Vehicles (driver_id, vehicle_type, vehicle_number, vehicle_model) VALUES (9, 'bike', 'KA-05-B-9999', 'Honda Activa');

INSERT INTO Drivers (id, name, phone, license_number, password_hash, is_online, rating, balance, status)
VALUES (10, 'Sai Karthik', '+919333333335', 'DL-BIKE-003', 'pbkdf2:sha256:260000$adminhashpwd', 1, 4.8, 110.00, 'approved');
INSERT INTO Vehicles (driver_id, vehicle_type, vehicle_number, vehicle_model) VALUES (10, 'bike', 'KA-05-B-1010', 'Ather 450X');

-- Seed Emergency Contact
INSERT INTO EmergencyContacts (user_id, name, phone, relationship, is_active)
VALUES (1, 'Tony Stark', '+919800000000', 'Friend', 1);

-- Seed Notifications
INSERT INTO Notifications (user_id, title, message, is_read, notification_type)
VALUES (1, 'Welcome to TravelFusion AI!', 'Your account has been successfully configured. Start planning your journey now.', 0, 'general');

-- 21. FavoriteLocations Table
CREATE TABLE IF NOT EXISTS FavoriteLocations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    label VARCHAR(50) NOT NULL, -- Home, Office, College, Other
    address VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- Seed Favorite Locations for User 1
INSERT INTO FavoriteLocations (user_id, label, address, latitude, longitude)
VALUES (1, 'Home', 'Pondicherry Rock Beach', 11.9338, 79.8354);
INSERT INTO FavoriteLocations (user_id, label, address, latitude, longitude)
VALUES (1, 'Office', 'Thavalakuppam Junction', 11.8744, 79.7997);

