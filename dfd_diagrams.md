# TravelFusion AI – Data Flow Diagrams (DFD)

This document contains the Level 0 (Context) and Level 1 Data Flow Diagrams for the TravelFusion AI application.

---

## DFD Level 0: Context Diagram

The Context Diagram represents the system as a single process and maps all external inputs and outputs.

```mermaid
flowchart TD
    %% Entities
    U[User]
    D[Driver]
    A[Admin]
    AI[AI & Maps API]

    %% System
    TF((TravelFusion AI Ecosystem))

    %% Data Flows (User)
    U -- "Travel Planner Inputs (Src, Dst, Budget)" --> TF
    U -- "Auth Details & OTP" --> TF
    U -- "Leg Booking Request" --> TF
    U -- "SOS Trigger Notification" --> TF
    TF -- "AI Multi-Leg Recommendations" --> U
    TF -- "Booking Invoices & ETA Updates" --> U
    TF -- "Emergency Contacts Alerts" --> U

    %% Data Flows (Driver)
    D -- "Registration & License Documents" --> TF
    D -- "Online/Offline Status Switch" --> TF
    D -- "Accept/Reject Ride Confirmation" --> TF
    TF -- "Ride Requests Details" --> D
    TF -- "Map Navigation Path & Coordinates" --> D
    TF -- "Trip Earnings & Rating Reports" --> D

    %% Data Flows (Admin)
    A -- "Manage Users & Approve Drivers" --> TF
    A -- "SOS Alerts Resolutions" --> TF
    TF -- "Active SOS Flags & Analytics" --> A
    TF -- "Generated Periodic Reports" --> A

    %% Data Flows (External APIs)
    TF -- "Prompt & Locations Coordinates" --> AI
    AI -- "Leg Routing Paths & Gemini Responses" --> TF
```

---

## DFD Level 1: Process Diagram

The Level 1 DFD decomposes the system into core sub-processes, identifying data stores and data paths.

```mermaid
flowchart TD
    %% Entities
    User[User]
    Driver[Driver]
    Admin[Admin]
    AI_API[Gemini / Maps API]

    %% Processes
    P1((1.0 User Auth & Profiles))
    P2((2.0 AI Route Engine))
    P3((3.0 Booking Core))
    P4((4.0 Trip Tracking))
    P5((5.0 Driver Dispatch))
    P6((6.0 Emergency SOS))
    P7((7.0 Admin Portal))

    %% Data Stores
    DB[("MySQL / SQLite Database")]

    %% P1 Flows
    User -- "Login credentials" --> P1
    P1 <--> DB
    P1 -- "User session" --> User

    %% P2 Flows
    User -- "Enter (Source, Destination, Budget)" --> P2
    P2 <--> DB
    P2 -- "Request path options" --> AI_API
    AI_API -- "Geocoded coordinates & options" --> P2
    P2 -- "Display cheapest/fastest route list" --> User

    %% P3 Flows
    User -- "Confirms bookings" --> P3
    P3 <--> DB
    P3 -- "Issues ticket cards & itinerary" --> User

    %% P4 Flows
    User -- "Live tracking view" --> P4
    P4 <--> DB
    P4 -- "Provides location updates & ETAs" --> User

    %% P5 Flows
    Driver -- "Toggle Online & Accept Rides" --> P5
    P5 <--> DB
    P5 -- "Allocates booking ID & path" --> Driver

    %% P6 Flows
    User -- "Press SOS button" --> P6
    P6 <--> DB
    P6 -- "Alarms emergency contacts" --> User
    P6 -- "Flags active emergency in DB" --> DB
    P6 -- "Forwards alarm panel" --> Admin

    %% P7 Flows
    Admin -- "Approve drivers & retrieve charts" --> P7
    P7 <--> DB
    P7 -- "Discharges metrics & CSV reports" --> Admin
```
