# TravelFusion

TravelFusion is a comprehensive, multi-modal transport and ride-booking application. It provides an intelligent routing engine to suggest the best travel options (Bike, Auto, Cab, Bus, Train, Flight) based on distance, budget, and the number of passengers.

## Features

- **User Portal**: Users can search for routes, book rides, view their upcoming and past trips, manage favorite locations, and emergency contacts.
- **Driver Portal**: Drivers can register, go online to receive ride requests, complete trips with OTP verification, and track their earnings.
- **Admin Console**: Administrators can monitor users, drivers, active bookings, and system statistics.
- **AI Route Planner**: Calculates the most efficient multi-modal travel plans (First Mile, Long Distance, Last Mile) using distance calculations and real-world heuristics.
- **Real-time Ride Tracking**: Monitors active trips and provides OTP-based ride verification.
- **Emergency Alerts**: Built-in SOS feature for traveler safety.

## Technology Stack

- **Backend**: Python with a Custom Flask-like framework (`custom_flask.py`)
- **Database**: SQLite (`database.py`)
- **Frontend**: HTML, CSS, JavaScript (Templates)
- **External APIs**: 
  - OSRM (Open Source Routing Machine) for accurate distance calculations
  - OpenStreetMap Nominatim for geocoding

## Getting Started

1. Ensure you have Python installed on your Windows machine.
2. The project directory contains `.bat` files to quickly start and stop the server:
   - Run `Start_App.bat` to launch the application.
   - Run `Stop_Server.bat` to stop the server gracefully.
3. Access the application in your browser (default port is usually set in `app.py` or `config.py`).
4. **Logins:**
   - **User Login**: `/login`
   - **Driver Login**: `/driver-login`
   - **Admin Login**: `/admin-login` (Use credentials provided in your system config)

## Project Structure

- `app.py`: Main application entry point handling routes and logic.
- `database.py` & `db_schema.sql`: Database management and schema definitions.
- `custom_flask.py`: Custom web framework handling requests and routing.
- `notification_service.py`: Handles sending notifications to users and drivers.
- `templates/`: Contains all the HTML templates for the UI.
- `static/`: Contains static assets like CSS, JS, and images.

## License

This project is proprietary.
