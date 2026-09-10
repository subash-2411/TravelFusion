import sqlite3
import json
import os
import sys

def mock_logic():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get active trip for driver 1 (assuming driver ID is 1, let's just get any active trip)
    cursor.execute("""
        SELECT rb.*, p.source, p.destination, b.total_fare as booking_total_fare, p.budget as plan_budget,
               b.passenger_name as rider_name, b.passenger_phone as rider_phone 
        FROM RideBookings rb 
        JOIN Bookings b ON rb.booking_id = b.id 
        JOIN TravelPlans p ON b.travel_plan_id = p.id 
        WHERE rb.status IN ('accepted', 'active')
        ORDER BY rb.id DESC LIMIT 1
    """)
    row = cursor.fetchone()
    if not row:
        print("No active trip found.")
        return
        
    active_trip = dict(row)
    print("DB active_trip leg_type:", active_trip.get('leg_type'))
    print("DB active_trip source:", active_trip.get('source'))
    
    # Mock fallback legs
    def generate_dynamic_fallback_legs(source_city, dest_city, is_driver=False):
        return [
            {"source": source_city, "destination": f"{source_city} Transit Hub", "mode": "auto", "leg_type": "first_mile", "start_coords": [1, 1], "end_coords": [2, 2]},
            {"source": f"{source_city} Transit Hub", "destination": f"{dest_city} Drop Hub", "mode": "bus", "leg_type": "long_distance", "start_coords": [2, 2], "end_coords": [3, 3]},
            {"source": f"{dest_city} Drop Hub", "destination": dest_city, "mode": "auto", "leg_type": "last_mile", "start_coords": [3, 3], "end_coords": [4, 4]}
        ]
        
    legs = generate_dynamic_fallback_legs(active_trip['source'].split(',')[0], active_trip['destination'].split(',')[0], is_driver=True)
    print(f"Fallback generated legs count: {len(legs)}")
    
    # Apply logic from app.py
    if len(legs) == 3:
        if 'leg_type' not in legs[0]: legs[0]['leg_type'] = 'first_mile'
        if 'leg_type' not in legs[1]: legs[1]['leg_type'] = 'long_distance'
        if 'leg_type' not in legs[2]: legs[2]['leg_type'] = 'last_mile'
    elif len(legs) == 1:
        if 'leg_type' not in legs[0]: legs[0]['leg_type'] = 'first_mile'
        
    driver_leg_type = active_trip.get('leg_type')
    driver_legs = []
    if driver_leg_type:
        driver_legs = [leg for leg in legs if leg.get('leg_type') == driver_leg_type]
        
    if driver_legs:
        legs = driver_legs
    elif legs:
        legs = [legs[0]]
        
    if legs:
        active_trip['source'] = legs[0].get('source', active_trip['source'])
        active_trip['destination'] = legs[0].get('destination', active_trip['destination'])
        
    print(f"Final legs count: {len(legs)}")
    print(f"Final active_trip source: {active_trip['source']}")
    print(f"Final active_trip dest: {active_trip['destination']}")
    print(f"Final legs JSON: {json.dumps(legs)}")

mock_logic()
