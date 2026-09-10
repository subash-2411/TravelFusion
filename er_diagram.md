# TravelFusion AI – Entity-Relationship (ER) Diagram

This diagram displays the database structure for TravelFusion AI. It defines the tables, primary keys (`PK`), foreign keys (`FK`), and entity relationships.

```mermaid
erDiagram
    USERS ||--|| USER_PROFILES : "has profile"
    USERS ||--o{ TRAVEL_PLANS : "creates"
    USERS ||--o{ BOOKINGS : "places"
    USERS ||--o{ NOTIFICATIONS : "receives"
    USERS ||--o{ EMERGENCY_CONTACTS : "defines"
    USERS ||--o{ EMERGENCY_ALERTS : "triggers"
    
    DRIVERS ||--|| VEHICLES : "drives"
    DRIVERS ||--o{ RIDE_BOOKINGS : "fulfills"
    
    TRAVEL_PLANS ||--o{ BOOKINGS : "results in"
    
    BOOKINGS ||--o| BUS_BOOKINGS : "includes bus"
    BOOKINGS ||--o| TRAIN_BOOKINGS : "includes train"
    BOOKINGS ||--o| FLIGHT_BOOKINGS : "includes flight"
    BOOKINGS ||--o| RIDE_BOOKINGS : "includes local ride"
    BOOKINGS ||--o| TRIP_TRACKING : "tracked by"
    BOOKINGS ||--o{ EMERGENCY_ALERTS : "associated with"
    BOOKINGS ||--o{ TRAVEL_HISTORY : "logged in"

    USERS {
        int id PK
        string email
        string phone
        string status
        timestamp created_at
    }

    USER_PROFILES {
        int user_id PK, FK
        string full_name
        string avatar_url
        decimal default_budget
        string default_first_mile
        string default_last_mile
    }

    DRIVERS {
        int id PK
        string name
        string phone
        string license_number
        int is_online
        decimal rating
        decimal balance
        string status
        timestamp created_at
    }

    VEHICLES {
        int driver_id PK, FK
        string vehicle_type
        string vehicle_number
        string vehicle_model
    }

    TRAVEL_PLANS {
        int id PK
        int user_id FK
        string source
        string destination
        date travel_date
        decimal budget
        timestamp search_time
    }

    BOOKINGS {
        int id PK
        int travel_plan_id FK
        int user_id FK
        decimal total_fare
        string status
        timestamp created_at
    }

    BUS_BOOKINGS {
        int booking_id PK, FK
        string bus_number
        string operator_name
        string seat_number
        datetime departure_time
        datetime arrival_time
        decimal fare
    }

    TRAIN_BOOKINGS {
        int booking_id PK, FK
        string train_number
        string train_name
        string coach_number
        string seat_number
        datetime departure_time
        datetime arrival_time
        decimal fare
    }

    FLIGHT_BOOKINGS {
        int booking_id PK, FK
        string flight_number
        string airline_name
        string seat_number
        string gate
        datetime departure_time
        datetime arrival_time
        decimal fare
    }

    RIDE_BOOKINGS {
        int booking_id PK, FK
        int driver_id FK
        string vehicle_type
        decimal fare
        string otp
        string status
    }

    NOTIFICATIONS {
        int id PK
        int user_id FK
        string title
        text message
        int is_read
        string notification_type
        timestamp created_at
    }

    EMERGENCY_CONTACTS {
        int id PK
        int user_id FK
        string name
        string phone
        string relationship
        int is_active
    }

    EMERGENCY_ALERTS {
        int id PK
        int user_id FK
        int booking_id FK
        decimal latitude
        decimal longitude
        string status
        timestamp created_at
    }

    TRIP_TRACKING {
        int booking_id PK, FK
        decimal current_latitude
        decimal current_longitude
        string current_leg
        int eta_minutes
        string status
        timestamp updated_at
    }

    TRAVEL_HISTORY {
        int id PK
        int user_id FK
        int booking_id FK
        date travel_date
        string source
        string destination
        decimal fare
        string status
    }

    ADMIN {
        int id PK
        string username
        string email
        string password_hash
        timestamp last_login
    }
```
