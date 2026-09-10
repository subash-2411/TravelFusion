let dashboardMap;
let pickupMarker, dropMarker;
let routeLine;

const START_LAT = 20.5937; // India Center
const START_LNG = 78.9629;
const ZOOM_LEVEL = 5;

// Custom Icons
const pickupIcon = L.divIcon({
    html: '<i class="bi bi-geo-alt-fill text-primary" style="font-size: 2rem; filter: drop-shadow(0 2px 5px rgba(0,0,0,0.5));"></i>',
    className: 'custom-div-icon',
    iconSize: [30, 42],
    iconAnchor: [15, 42]
});

const dropIcon = L.divIcon({
    html: '<i class="bi bi-geo-fill text-danger" style="font-size: 2rem; filter: drop-shadow(0 2px 5px rgba(0,0,0,0.5));"></i>',
    className: 'custom-div-icon',
    iconSize: [30, 42],
    iconAnchor: [15, 42]
});

document.addEventListener('DOMContentLoaded', () => {
    initMap();
    setupAutocomplete('pickup_input', 'pickup_suggestions', 'source_lat', 'source_lng', 'pickup');
    setupAutocomplete('drop_input', 'drop_suggestions', 'dest_lat', 'dest_lng', 'drop');

    const plannerForm = document.getElementById('plannerForm');
    if (plannerForm) {
        plannerForm.addEventListener('submit', (e) => {
            const lat1 = document.getElementById('source_lat').value;
            const lng1 = document.getElementById('source_lng').value;
            const lat2 = document.getElementById('dest_lat').value;
            const lng2 = document.getElementById('dest_lng').value;

            if (!lat1 || !lng1 || !lat2 || !lng2) {
                e.preventDefault();
                if (typeof showNotification === 'function') {
                    showNotification('Select Locations', 'Please select valid Pickup and Dropoff locations from the suggestions list before planning your trip.', 'danger');
                } else {
                    alert('Please select valid Pickup and Dropoff locations from the suggestions list.');
                }
            }
        });
    }
});

let streetLayer, satelliteLayer, classicLayer;
let currentLayerType = 'street';

function initMap() {
    dashboardMap = L.map('dashboardMap', { 
        zoomControl: false,
        attributionControl: false,
        doubleClickZoom: false
    }).setView([START_LAT, START_LNG], ZOOM_LEVEL);
    
    // Add Zoom Control at bottom right
    L.control.zoom({ position: 'bottomright' }).addTo(dashboardMap);

    // Real Google Maps Street View tiles for a realistic look
    streetLayer = L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
        maxZoom: 20
    });

    // Real Google Maps Satellite Hybrid tiles for realistic satellite look
    satelliteLayer = L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', {
        maxZoom: 20
    });

    // Classic OpenStreetMap tiles
    classicLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19
    });

    // Add default layer
    streetLayer.addTo(dashboardMap);

    // Add custom floating layer toggle button control
    const LayerToggleControl = L.Control.extend({
        options: { position: 'topright' },
        onAdd: function() {
            const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
            container.style.backgroundColor = 'rgba(15, 23, 42, 0.85)';
            container.style.backdropFilter = 'blur(10px)';
            container.style.border = '1px solid rgba(255, 255, 255, 0.15)';
            container.style.borderRadius = '8px';
            container.style.cursor = 'pointer';
            container.style.padding = '6px 12px';
            container.style.color = '#fff';
            container.style.fontSize = '0.8rem';
            container.style.fontWeight = 'bold';
            container.style.display = 'flex';
            container.style.alignItems = 'center';
            container.style.gap = '6px';
            container.style.boxShadow = '0 4px 15px rgba(0,0,0,0.3)';

            container.innerHTML = '<i class="bi bi-globe2 text-info"></i> <span id="mapLayerText">Satellite</span>';

            L.DomEvent.disableClickPropagation(container);
            
            container.onclick = () => {
                if (currentLayerType === 'street') {
                    dashboardMap.removeLayer(streetLayer);
                    satelliteLayer.addTo(dashboardMap);
                    currentLayerType = 'satellite';
                    document.getElementById('mapLayerText').innerText = 'Street View';
                } else {
                    dashboardMap.removeLayer(satelliteLayer);
                    streetLayer.addTo(dashboardMap);
                    currentLayerType = 'street';
                    document.getElementById('mapLayerText').innerText = 'Satellite';
                }
            };
            return container;
        }
    });
    
    dashboardMap.addControl(new LayerToggleControl());
    
    dashboardMap.on('contextmenu', function(e) {
        showManualLocationPopup(e.latlng);
    });
    
    dashboardMap.on('dblclick', function(e) {
        showManualLocationPopup(e.latlng);
    });
}

window.setManualLocation = async function(lat, lng, type) {
    dashboardMap.closePopup();
    
    // Reverse geocode to get a readable name
    let name = "Manual Location";
    try {
        const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`);
        const data = await res.json();
        if(data && data.display_name) {
            const parts = data.display_name.split(',');
            name = parts.slice(0,3).join(',').trim();
        }
    } catch(err) {
        console.error(err);
    }
    
    const inputId = type === 'pickup' ? 'pickup_input' : 'drop_input';
    const latId = type === 'pickup' ? 'source_lat' : 'dest_lat';
    const lngId = type === 'pickup' ? 'source_lng' : 'dest_lng';
    
    document.getElementById(inputId).value = name;
    document.getElementById(latId).value = lat;
    document.getElementById(lngId).value = lng;
    
    updateMapMarker(type, lat, lng, name);
    
    if (typeof showNotification === 'function') {
        showNotification('Location Set', `${type === 'pickup' ? 'Pickup' : 'Drop'} location set manually.`, 'success');
    }
};

function showManualLocationPopup(latlng) {
    L.popup()
        .setLatLng(latlng)
        .setContent(`
            <div class="text-center p-2" style="min-width:150px;">
                <h6 class="mb-3 text-dark fw-bold">Set Location Here</h6>
                <button class="btn btn-sm w-100 mb-2 text-white" style="background:var(--accent-blue);border:none;" onclick="setManualLocation(${latlng.lat}, ${latlng.lng}, 'pickup')">
                    <i class="bi bi-geo-alt-fill me-1"></i> Set as Pickup
                </button>
                <button class="btn btn-sm w-100 text-white" style="background:var(--danger-red);border:none;" onclick="setManualLocation(${latlng.lat}, ${latlng.lng}, 'drop')">
                    <i class="bi bi-geo-fill me-1"></i> Set as Drop
                </button>
            </div>
        `)
        .openOn(dashboardMap);
}

// Autocomplete Logic
function setupAutocomplete(inputId, suggestionsId, latId, lngId, type) {
    const input = document.getElementById(inputId);
    const suggestionsBox = document.getElementById(suggestionsId);
    let timeout = null;

    input.addEventListener('input', (e) => {
        clearTimeout(timeout);
        const query = e.target.value.trim();
        
        if (query.length < 3) {
            suggestionsBox.style.display = 'none';
            return;
        }

        timeout = setTimeout(async () => {
            try {
                // Typo cleanup helper
                let cleanedQuery = query.toLowerCase();
                cleanedQuery = cleanedQuery.replace("assumentpark", "amusement park");
                cleanedQuery = cleanedQuery.replace("assument park", "amusement park");
                cleanedQuery = cleanedQuery.replace("asument park", "amusement park");
                cleanedQuery = cleanedQuery.replace("asumentpark", "amusement park");
                cleanedQuery = cleanedQuery.replace("wonderla", "wonderla amusement park");

                // Get dynamic map bounds to bias results locally (like Chennai/TN)
                let boundsBias = "";
                if (dashboardMap) {
                    const bounds = dashboardMap.getBounds();
                    boundsBias = `&viewbox=${bounds.getWest()},${bounds.getNorth()},${bounds.getEast()},${bounds.getSouth()}`;
                }

                // Nominatim API constrained to India with local map bias
                const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(cleanedQuery)}&countrycodes=in&limit=10${boundsBias}`);
                const data = await res.json();
                
                suggestionsBox.innerHTML = '';
                if (data.length > 0) {
                    data.forEach(item => {
                        const div = document.createElement('div');
                        div.className = 'p-2 cursor-pointer border-bottom border-secondary border-opacity-25 text-white suggestion-item';
                        div.style.fontSize = '0.9rem';
                        div.style.cursor = 'pointer';
                        
                        // Parse address smartly
                        const addressParts = item.display_name.split(',');
                        const name = addressParts[0].trim();
                        const detailedName = addressParts.slice(0, 3).join(',').trim();
                        const full = item.display_name;
                        
                        div.innerHTML = `<i class="bi bi-geo me-2 text-muted"></i><strong>${name}</strong><br><small class="text-muted" style="font-size:0.75rem;">${full}</small>`;
                        
                        div.onclick = () => {
                            input.value = detailedName;
                            document.getElementById(latId).value = item.lat;
                            document.getElementById(lngId).value = item.lon;
                            suggestionsBox.style.display = 'none';
                            
                            updateMapMarker(type, item.lat, item.lon, detailedName);
                        };
                        
                        // Hover effect
                        div.addEventListener('mouseover', () => div.style.background = 'rgba(255,255,255,0.1)');
                        div.addEventListener('mouseout', () => div.style.background = 'transparent');
                        
                        suggestionsBox.appendChild(div);
                    });
                    suggestionsBox.style.display = 'block';
                } else {
                    // Fallback for custom or unmapped addresses
                    const div = document.createElement('div');
                    div.className = 'p-2 cursor-pointer border-bottom border-warning border-opacity-50 text-warning suggestion-item';
                    div.style.fontSize = '0.9rem';
                    div.style.cursor = 'pointer';
                    div.style.background = 'rgba(255,193,7,0.1)';
                    
                    div.innerHTML = `<i class="bi bi-pin-map-fill me-2"></i><strong>Address not found on map</strong><br><small style="font-size:0.75rem;">Click to use "${query}" and manually drop a pin on the map.</small>`;
                    
                    div.onclick = () => {
                        input.value = query;
                        // Use center of current map view as fallback location
                        let centerLat = START_LAT;
                        let centerLng = START_LNG;
                        if (dashboardMap) {
                            const center = dashboardMap.getCenter();
                            centerLat = center.lat;
                            centerLng = center.lng;
                        }
                        
                        document.getElementById(latId).value = centerLat;
                        document.getElementById(lngId).value = centerLng;
                        suggestionsBox.style.display = 'none';
                        
                        updateMapMarker(type, centerLat, centerLng, query);
                        if (typeof showNotification === 'function') {
                            showNotification('Pin Dropped', 'Please drag the map marker to your exact location.', 'warning');
                        }
                    };
                    
                    div.addEventListener('mouseover', () => div.style.background = 'rgba(255,193,7,0.2)');
                    div.addEventListener('mouseout', () => div.style.background = 'rgba(255,193,7,0.1)');
                    
                    suggestionsBox.appendChild(div);
                    suggestionsBox.style.display = 'block';
                }
            } catch (err) {
                console.error('Geocoding error:', err);
            }
        }, 500); // 500ms debounce
    });

    // Close suggestions on outside click
    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.style.display = 'none';
        }
    });
}

// Map Rendering Logic
function updateMapMarker(type, lat, lng, name) {
    if (type === 'pickup') {
        if (pickupMarker) dashboardMap.removeLayer(pickupMarker);
        pickupMarker = L.marker([lat, lng], { icon: pickupIcon, draggable: true }).bindPopup(`<b>Pickup:</b> ${name}`).addTo(dashboardMap);
        
        pickupMarker.on('dragend', async function(event) {
            const position = event.target.getLatLng();
            document.getElementById('source_lat').value = position.lat;
            document.getElementById('source_lng').value = position.lng;
            
            try {
                const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${position.lat}&lon=${position.lng}&zoom=18&addressdetails=1`);
                const data = await res.json();
                const addressParts = data.display_name.split(',');
                const address = addressParts.slice(0, 3).join(',').trim();
                
                document.getElementById('pickup_input').value = address;
                event.target.setPopupContent(`<b>Pickup:</b> ${address}`).openPopup();
                checkAndDrawRoute();
            } catch(e) { console.error(e); }
        });
    } else {
        if (dropMarker) dashboardMap.removeLayer(dropMarker);
        dropMarker = L.marker([lat, lng], { icon: dropIcon, draggable: true }).bindPopup(`<b>Drop:</b> ${name}`).addTo(dashboardMap);
        
        dropMarker.on('dragend', async function(event) {
            const position = event.target.getLatLng();
            document.getElementById('dest_lat').value = position.lat;
            document.getElementById('dest_lng').value = position.lng;
            
            try {
                const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${position.lat}&lon=${position.lng}&zoom=18&addressdetails=1`);
                const data = await res.json();
                const addressParts = data.display_name.split(',');
                const address = addressParts.slice(0, 3).join(',').trim();
                
                document.getElementById('drop_input').value = address;
                event.target.setPopupContent(`<b>Drop:</b> ${address}`).openPopup();
                checkAndDrawRoute();
            } catch(e) { console.error(e); }
        });
    }

    checkAndDrawRoute();
}

async function checkAndDrawRoute() {
    const lat1 = document.getElementById('source_lat').value;
    const lng1 = document.getElementById('source_lng').value;
    const lat2 = document.getElementById('dest_lat').value;
    const lng2 = document.getElementById('dest_lng').value;

    if (lat1 && lng1 && lat2 && lng2) {
        // Both points available, draw route
        try {
            const res = await fetch(`https://router.project-osrm.org/route/v1/driving/${lng1},${lat1};${lng2},${lat2}?overview=full&geometries=geojson`);
            const data = await res.json();

            if (data.routes && data.routes.length > 0) {
                const route = data.routes[0];
                const coords = route.geometry.coordinates.map(c => [c[1], c[0]]); // Leaflet uses [lat, lng]

                if (routeLine) dashboardMap.removeLayer(routeLine);
                
                routeLine = L.polyline(coords, {
                    color: '#06b6d4',
                    weight: 5,
                    opacity: 0.9,
                    dashArray: '10, 10',
                    className: 'animated-route-line',
                    lineJoin: 'round'
                }).addTo(dashboardMap);

                // Fit map to show full route with padding
                dashboardMap.fitBounds(routeLine.getBounds(), { padding: [50, 50] });

                // Update Stats Widget
                const distanceKm = (route.distance / 1000).toFixed(1);
                const timeMins = Math.round(route.duration / 60);
                
                document.getElementById('routeDistance').innerText = distanceKm + ' km';
                document.getElementById('routeTime').innerText = timeMins + ' mins';
                document.getElementById('routeStatsWidget').style.display = 'block';
                
            }
        } catch (err) {
            console.error('Routing error:', err);
        }
    } else if (lat1 && lng1) {
        // Only pickup
        dashboardMap.flyTo([lat1, lng1], 17);
    } else if (lat2 && lng2) {
        // Only drop
        dashboardMap.flyTo([lat2, lng2], 17);
    }
}

// Current Location (GPS)
function useCurrentLocation() {
    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser.");
        return;
    }

    const input = document.getElementById('pickup_input');
    input.value = "Fetching current location...";

    navigator.geolocation.getCurrentPosition(async (pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;

        try {
            const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`);
            const data = await res.json();
            
            const addressParts = data.display_name.split(',');
            const address = addressParts.slice(0, 3).join(',').trim();
            
            input.value = address;
            document.getElementById('source_lat').value = lat;
            document.getElementById('source_lng').value = lng;
            
            updateMapMarker('pickup', lat, lng, address);
            
            if(typeof showNotification === 'function') {
                showNotification('Location Found', 'GPS coordinates fetched successfully.', 'success');
            }
        } catch (err) {
            const fallbackAddress = "Current Location (" + lat.toFixed(4) + ", " + lng.toFixed(4) + ")";
            input.value = fallbackAddress;
            document.getElementById('source_lat').value = lat;
            document.getElementById('source_lng').value = lng;
            updateMapMarker('pickup', lat, lng, fallbackAddress);
        }
    }, (err) => {
        input.value = "";
        alert("Unable to fetch location. Please allow permissions.");
    }, {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
    });
}
