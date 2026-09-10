// TravelFusion AI Live Navigation Map Simulation

var trackingInterval = null;
let currentTrackingMap = null;

// Initialize Live Map with Route Legs
function initTrackingMap(mapId, legs, startLat, startLng) {
    const hasLeaflet = typeof L !== 'undefined';
    const container = document.getElementById(mapId);
    
    if (!container) return null;
    
    // Properly destroy previous Leaflet map if it exists
    if (currentTrackingMap) {
        currentTrackingMap.remove();
        currentTrackingMap = null;
    }
    container.innerHTML = '';
    
    if (hasLeaflet) {
        try {
            // Create Leaflet Map
            const map = L.map(mapId, {
                center: [startLat || legs[0].start_coords[0], startLng || legs[0].start_coords[1]],
                zoom: 12,
                zoomControl: true,
                attributionControl: false
            });
            currentTrackingMap = map;
            
            // Set Google Maps Street View tiles for realistic look
            L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
                maxZoom: 20
            }).addTo(map);
            
            // Draw route lines
            const polylinePoints = [];
            
            // Pin markers
            // Start
            L.marker(legs[0].start_coords, {
                icon: L.divIcon({
                    className: 'custom-pin-start',
                    html: '<div style="background-color: var(--success-green); width: 14px; height: 14px; border-radius:50%; border: 3px solid #fff; box-shadow: 0 0 10px rgba(16,185,129,0.8);"></div>',
                    iconSize: [14, 14]
                })
            }).addTo(map).bindPopup(`<b>Start Point</b><br>${legs[0].source}`);
            
            polylinePoints.push(legs[0].start_coords);
            
            // Add transitions & endpoints
            legs.forEach((leg, idx) => {
                polylinePoints.push(leg.end_coords);
                
                const isLast = idx === legs.length - 1;
                const label = isLast ? `<b>Final Destination</b><br>${leg.destination}` : `<b>Transfer Station (${leg.destination})</b><br>Arrived via ${leg.mode.toUpperCase()}`;
                
                let iconHtml = '';
                if (isLast) {
                    iconHtml = `<div style="background-color: #ef4444; width: 32px; height: 32px; border-radius:50%; border: 2px solid #fff; box-shadow: 0 0 15px #ef4444; display:flex; align-items:center; justify-content:center;">
                                    <i class="bi bi-flag-fill text-white" style="font-size:14px;"></i>
                                </div>`;
                } else {
                    let iconClass = 'bi-geo-alt-fill';
                    let isEmoji = false;
                    let emojiChar = '';
                    if (leg.mode === 'bike') iconClass = 'fa-solid fa-motorcycle';
                    else if (leg.mode === 'auto') { isEmoji = true; emojiChar = '🛺'; }
                    else if (leg.mode === 'cab') iconClass = 'bi-car-front-fill';
                    else if (leg.mode === 'bus') iconClass = 'bi-bus-front-fill';
                    else if (leg.mode === 'train') iconClass = 'bi-train-front-fill';
                    else if (leg.mode === 'flight') iconClass = 'bi-airplane-fill';
                    
                    const isFa = iconClass.startsWith('fa-');
                    const fullIconClass = isFa ? iconClass : `bi ${iconClass}`;
                    const innerHtml = isEmoji ? `<span style="font-size: 14px; line-height: 1;">${emojiChar}</span>` : `<i class="${fullIconClass} text-white" style="font-size:12px;"></i>`;
                    iconHtml = `<div style="background-color: #2563eb; width: 28px; height: 28px; border-radius:50%; border: 2px solid #fff; box-shadow: 0 0 10px rgba(37,99,235,0.6); display:flex; align-items:center; justify-content:center;">
                                    ${innerHtml}
                                </div>`;
                }
                
                L.marker(leg.end_coords, {
                    icon: L.divIcon({
                        className: 'custom-pin-stop',
                        html: iconHtml,
                        iconSize: isLast ? [32, 32] : [28, 28]
                    })
                }).addTo(map).bindPopup(label);
            });
            
            // Add Moving Traveler icon (Default matched to mode)
            let defaultIconHtml = '<i class="bi bi-geo-alt-fill text-white" style="font-size:14px;"></i>';
            let defaultBg = '#2563eb';
            if (legs && legs.length > 0) {
                const firstMode = legs[0].mode;
                if (firstMode === 'bike') { defaultIconHtml = '<span style="font-size:18px;line-height:1;">🏍️</span>'; defaultBg = '#06b6d4'; }
                else if (firstMode === 'auto') { defaultIconHtml = '<span style="font-size:18px;line-height:1;">🛺</span>'; defaultBg = '#10b981'; }
                else if (firstMode === 'cab') { defaultIconHtml = '<span style="font-size:18px;line-height:1;">🚗</span>'; defaultBg = '#f59e0b'; }
                else if (firstMode === 'bus') { defaultIconHtml = '<i class="bi bi-bus-front-fill text-white" style="font-size:14px;"></i>'; defaultBg = '#3b82f6'; }
                else if (firstMode === 'train') { defaultIconHtml = '<i class="bi bi-train-front-fill text-white" style="font-size:14px;"></i>'; defaultBg = '#ef4444'; }
                else if (firstMode === 'flight') { defaultIconHtml = '<i class="bi bi-airplane-fill text-white" style="font-size:14px;"></i>'; defaultBg = '#a855f7'; }
            }
            const travelerIcon = L.divIcon({
                className: 'custom-traveler-pin',
                html: `<div class="pulse-danger" style="background-color: ${defaultBg}; width: 32px; height: 32px; border-radius:50%; border: 2px solid #fff; box-shadow: 0 0 15px ${defaultBg}; display:flex; align-items:center; justify-content:center;">
                           ${defaultIconHtml}
                       </div>`,
                iconSize: [32, 32]
            });
            
            const movingMarker = L.marker([startLat || legs[0].start_coords[0], startLng || legs[0].start_coords[1]], {
                icon: travelerIcon
            }).addTo(map);
            
            const mapObj = {
                map: map,
                marker: movingMarker,
                type: 'leaflet',
                legsData: legs,
                geoPaths: {} // store coord arrays per leg
            };

            // Fetch Real Roads asynchronously from OSRM
            const fetchRealRoads = async () => {
                let allBounds = L.latLngBounds();
                for (let leg of legs) {
                    try {
                        const url = `http://router.project-osrm.org/route/v1/driving/${leg.start_coords[1]},${leg.start_coords[0]};${leg.end_coords[1]},${leg.end_coords[0]}?geometries=geojson&overview=full`;
                        const res = await fetch(url);
                        const data = await res.json();
                        
                        if (data.code === 'Ok') {
                            const coords = data.routes[0].geometry.coordinates; // [lng, lat]
                            mapObj.geoPaths[leg.leg_type] = coords.map(c => [c[1], c[0]]); // Leaflet uses [lat, lng]
                            
                            // Draw exact road path
                            const roadPath = L.geoJSON(data.routes[0].geometry, {
                                style: { color: '#3b82f6', weight: 6, opacity: 0.8 }
                            }).addTo(map);
                            allBounds.extend(roadPath.getBounds());
                        } else {
                            mapObj.geoPaths[leg.leg_type] = [leg.start_coords, leg.end_coords];
                            allBounds.extend([leg.start_coords, leg.end_coords]);
                        }
                    } catch(e) {
                        mapObj.geoPaths[leg.leg_type] = [leg.start_coords, leg.end_coords];
                        allBounds.extend([leg.start_coords, leg.end_coords]);
                    }
                }
                if (allBounds.isValid()) {
                    map.fitBounds(allBounds, { padding: [50, 50] });
                }
            };
            fetchRealRoads();
            
            return mapObj;
        } catch (err) {
            console.warn("Leaflet map compilation failed. Initializing SVG simulation fallback.", err);
        }
    }
    
    // SVG Vector Canvas fallback when Leaflet is blocked or failed to load
    return initSVGSimulation(container, legs);
}

// SVG Vector Fallback Renderer
function initSVGSimulation(container, legs) {
    container.style.position = 'relative';
    container.style.background = '#0f172a';
    container.style.display = 'flex';
    container.style.alignItems = 'center';
    container.style.justifyContent = 'center';
    
    try {
        const safeSplit = (str, fallback) => {
            if (!str) return fallback;
            return String(str).split(',')[0];
        };

    let svgHtml = '';
    
    if (legs.length === 1) {
        const sourceName = safeSplit(legs[0].source, 'Origin');
        const destName = safeSplit(legs[0].destination, 'Destination');
        svgHtml = `
            <svg width="100%" height="100%" viewBox="0 0 800 400" style="max-height: 100%;">
                <defs>
                    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                        <feGaussianBlur stdDeviation="5" result="blur" />
                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                </defs>
                <path id="svg-route-path" d="M 100,200 L 700,200" fill="none" stroke="#3b82f6" stroke-width="6" stroke-dasharray="8,8" opacity="0.6"/>
                <circle cx="100" cy="200" r="10" fill="#10b981" stroke="#fff" stroke-width="3" filter="url(#glow)"/>
                <text x="100" y="230" fill="#fff" font-size="12" text-anchor="middle">${sourceName}</text>
                
                <circle cx="700" cy="200" r="10" fill="#ef4444" stroke="#fff" stroke-width="3" filter="url(#glow)"/>
                <text x="700" y="230" fill="#fff" font-size="12" text-anchor="middle">${destName}</text>
                
                <circle id="svg-traveler" cx="100" cy="200" r="12" fill="#2563eb" stroke="#fff" stroke-width="4" filter="url(#glow)">
                    <animate attributeName="r" values="12;15;12" dur="1.5s" repeatCount="indefinite"/>
                </circle>
            </svg>
        `;
    } else {
        let middlePins = '';
        const numLegs = legs.length;
        const destIndex = numLegs - 1;
        
        const sourceName = safeSplit(legs[0].source, 'Origin');
        const finalDestName = safeSplit(legs[destIndex].destination, 'Destination');
        
        if (numLegs === 2) {
            const midDest1 = safeSplit(legs[0].destination, 'Stop');
            middlePins = `
                <!-- Middle pin 1 -->
                <circle cx="400" cy="140" r="8" fill="#3b82f6" stroke="#fff" stroke-width="2"/>
                <text x="400" y="120" fill="#94a3b8" font-size="10" text-anchor="middle">${midDest1}</text>
            `;
        } else if (numLegs >= 3) {
            const midDest1 = safeSplit(legs[0].destination, 'Stop');
            const midDest2 = safeSplit(legs[1].destination, 'Stop');
            middlePins = `
                <!-- Middle pin 1 -->
                <circle cx="280" cy="140" r="8" fill="#3b82f6" stroke="#fff" stroke-width="2"/>
                <text x="280" y="120" fill="#94a3b8" font-size="10" text-anchor="middle">${midDest1}</text>
                
                <!-- Middle pin 2 -->
                <circle cx="510" cy="235" r="8" fill="#3b82f6" stroke="#fff" stroke-width="2"/>
                <text x="510" y="260" fill="#94a3b8" font-size="10" text-anchor="middle">${midDest2}</text>
            `;
        }

        svgHtml = `
            <svg width="100%" height="100%" viewBox="0 0 800 400" style="max-height: 100%;">
                <defs>
                    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                        <feGaussianBlur stdDeviation="5" result="blur" />
                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                </defs>
                <path id="svg-route-path" d="M 100,200 Q 250,100 400,200 T 700,200" fill="none" stroke="#3b82f6" stroke-width="6" stroke-dasharray="8,8" opacity="0.6"/>
                <circle cx="100" cy="200" r="10" fill="#10b981" stroke="#fff" stroke-width="3" filter="url(#glow)"/>
                <text x="100" y="230" fill="#fff" font-size="12" text-anchor="middle">${sourceName}</text>
                
                ${middlePins}
                
                <circle cx="700" cy="200" r="10" fill="#ef4444" stroke="#fff" stroke-width="3" filter="url(#glow)"/>
                <text x="700" y="230" fill="#fff" font-size="12" text-anchor="middle">${finalDestName}</text>
                
                <circle id="svg-traveler" cx="100" cy="200" r="12" fill="#2563eb" stroke="#fff" stroke-width="4" filter="url(#glow)">
                    <animate attributeName="r" values="12;15;12" dur="1.5s" repeatCount="indefinite"/>
                </circle>
            </svg>
        `;
    }
    
        container.innerHTML = svgHtml;
        
        return {
            type: 'svg',
            element: document.getElementById('svg-traveler'),
            path: document.getElementById('svg-route-path'),
            legsData: legs
        };
    } catch(err) {
        console.error("SVG generation failed:", err);
        container.innerHTML = '<div style="color:white;text-align:center;">Tracking Map Unavailable</div>';
        return { type: 'fallback', legsData: legs };
    }
}

// Live tracking poller
function startLiveJourneyTracking(bookingId, mapInstance) {
    function getBearing(lat1, lng1, lat2, lng2) {
        let dLng = (lng2 - lng1) * Math.PI / 180;
        lat1 = lat1 * Math.PI / 180;
        lat2 = lat2 * Math.PI / 180;
        let y = Math.sin(dLng) * Math.cos(lat2);
        let x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLng);
        let brng = Math.atan2(y, x) * 180 / Math.PI;
        return (brng + 360) % 360;
    }

    const updatePosition = () => {
        fetch(`/api/tracking/${bookingId}`)
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    console.warn("Tracking data missing. Simulating fallback.");
                    data = {
                        status: 'in_transit',
                        current_leg: mapInstance.legsData && mapInstance.legsData.length > 0 ? mapInstance.legsData[0].leg_type : 'first_mile',
                        current_latitude: mapInstance.legsData && mapInstance.legsData.length > 0 ? mapInstance.legsData[0].start_coords[0] : 12.9716,
                        current_longitude: mapInstance.legsData && mapInstance.legsData.length > 0 ? mapInstance.legsData[0].start_coords[1] : 77.5946,
                        eta_minutes: 15
                    };
                }
                
                // If the dynamic leg or status from API does not match the rendered leg/status on the page, reload the page once!
                const legMismatch = data.current_leg && window.renderedLeg && data.current_leg !== window.renderedLeg;
                const statusMismatch = (data.status === 'in_transit' && window.renderedStatus !== 'in_transit') || 
                                       (data.status === 'driver_completed' && window.renderedStatus !== 'driver_completed') || 
                                       (data.status === 'completed' && window.renderedStatus !== 'completed');
                
                // Bypass reload checks if the trip is already marked completed either in window or backend to prevent loop traps
                if (data.status === 'completed' || window.renderedStatus === 'completed') {
                    // Do nothing, final state is already achieved
                } else if (legMismatch || statusMismatch) {
                    clearInterval(trackingInterval);
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                    return;
                }
                
                // Map backend tracking state to local timeline UI steps if local ride page
                if (typeof updateLocalTimelineUI === 'function') {
                    let localStep = 'searching';
                    if (data.status === 'driver_assigned') {
                        if (typeof mapInstance.approachProgress !== 'undefined' && mapInstance.approachProgress >= 1) {
                            localStep = 'arrived';
                        } else {
                            localStep = 'onway';
                        }
                    } else if (data.status === 'boarding' || data.status === 'pending') {
                        localStep = 'assigned';
                    } else if (data.status === 'in_transit') {
                        localStep = 'transit';
                    } else if (data.status === 'completed') {
                        localStep = 'completed';
                    }
                    updateLocalTimelineUI(localStep);
                }

                // Update tracker markers
                if (mapInstance.type === 'leaflet') {
                    // Update icon dynamically based on vehicle type
                    let innerHtml = '<i class="bi bi-geo-alt-fill text-white" style="font-size:16px;"></i>';
                    let bgColor = 'var(--royal-blue)';
                    
                    const activeLegInfo = mapInstance.legsData ? mapInstance.legsData.find(l => l.leg_type === data.current_leg || (l.leg_type === 'direct' && data.current_leg === 'local') || (l.leg_type === 'local' && data.current_leg === 'direct')) : null;
                    if (activeLegInfo) {
                        const m = activeLegInfo.mode;
                        if (m === 'bike') { innerHtml = '<span style="font-size: 18px; line-height: 1;">🏍️</span>'; bgColor = '#06b6d4'; }
                        else if (m === 'auto') { innerHtml = '<span style="font-size: 18px; line-height: 1;">🛺</span>'; bgColor = '#10b981'; }
                        else if (m === 'cab') { innerHtml = '<span style="font-size: 18px; line-height: 1;">🚗</span>'; bgColor = '#f59e0b'; }
                        else if (m === 'bus') { innerHtml = '<i class="bi bi-bus-front-fill text-white" style="font-size:16px;"></i>'; bgColor = '#3b82f6'; }
                        else if (m === 'train') { innerHtml = '<i class="bi bi-train-front-fill text-white" style="font-size:16px;"></i>'; bgColor = '#ef4444'; }
                        else if (m === 'flight') { innerHtml = '<i class="bi bi-airplane-fill text-white" style="font-size:16px;"></i>'; bgColor = '#a855f7'; }
                    }
                    const newIcon = L.divIcon({
                        className: 'custom-traveler-pin',
                        html: `<div class="pulse-danger" style="background-color: ${bgColor}; width: 32px; height: 32px; border-radius:50%; border: 2px solid #fff; box-shadow: 0 0 15px ${bgColor}; display:flex; align-items:center; justify-content:center; transition: all 0.3s ease;">
                                   ${innerHtml}
                               </div>`,
                        iconSize: [32, 32]
                    });
                    mapInstance.marker.setIcon(newIcon);
                    
                    // Handle Driver Approach or In-Transit Interpolation
                    if (data.status === 'driver_assigned' && data.driver_latitude) {
                        if (typeof mapInstance.approachProgress === 'undefined' || mapInstance.currentLegState !== 'driver_approach') {
                            mapInstance.approachProgress = 0;
                            mapInstance.currentLegState = 'driver_approach';
                            mapInstance.marker.setLatLng([data.driver_latitude, data.driver_longitude]);
                        }
                        
                        const eta_mins = Math.max(1, data.eta_minutes);
                        
                        // Driver approach takes 30 seconds (10 steps of 3 seconds)
                        mapInstance.approachProgress += 0.1;
                        if (mapInstance.approachProgress > 1) mapInstance.approachProgress = 1;
                        
                        let lat = data.driver_latitude + (data.current_latitude - data.driver_latitude) * mapInstance.approachProgress;
                        let lng = data.driver_longitude + (data.current_longitude - data.driver_longitude) * mapInstance.approachProgress;
                        
                        mapInstance.marker.setLatLng([lat, lng]);
                        
                        // Calculate bearing
                        mapInstance.currentBearing = getBearing(data.driver_latitude, data.driver_longitude, data.current_latitude, data.current_longitude);

                        if (mapInstance.map && !mapInstance.map.getBounds().contains([lat, lng])) {
                            mapInstance.map.panTo([lat, lng], { animate: true, duration: 1.5 });
                        }
                        
                        if (mapInstance.approachProgress >= 1 && !mapInstance.approachNotified) {
                            mapInstance.approachNotified = true;
                            if (typeof Swal !== 'undefined') {
                                Swal.fire({
                                    title: 'Driver Arrived!',
                                    text: 'Your driver has reached the location.',
                                    icon: 'success',
                                    timer: 3000,
                                    showConfirmButton: false
                                });
                            }
                        }
                        
                        // Show a fast fake ETA counting down for approach
                        data.eta_minutes = Math.max(0, Math.ceil(5 * (1 - mapInstance.approachProgress)));
                        
                    } else if (data.status === 'arrived_at_pickup' || data.status === 'arrived') {
                        mapInstance.marker.setLatLng([data.current_latitude, data.current_longitude]);
                        if (mapInstance.map && !mapInstance.map.getBounds().contains([data.current_latitude, data.current_longitude])) {
                            mapInstance.map.panTo([data.current_latitude, data.current_longitude]);
                        }
                        data.eta_minutes = 0;
                        
                    } else if (activeLegInfo && (mapInstance.geoPaths[data.current_leg] || mapInstance.geoPaths['direct'] || mapInstance.geoPaths['local'])) {
                        // In Transit
                        const coords = mapInstance.geoPaths[data.current_leg] || mapInstance.geoPaths['direct'] || mapInstance.geoPaths['local'];
                        if (coords.length > 0) {
                            if (typeof mapInstance.simProgress === 'undefined' || mapInstance.currentLegState !== data.current_leg) {
                                mapInstance.simProgress = 0;
                                mapInstance.currentLegState = data.current_leg;
                                mapInstance.autoCompleted = false;
                            }
                            
                            const eta_mins = Math.max(1, data.eta_minutes);
                            
                            // ALL rides now move based on real ETA time
                            const increment = 1.0 / (eta_mins * 20);
                            
                            mapInstance.simProgress += increment;
                            if (mapInstance.simProgress >= 1) {
                                mapInstance.simProgress = 1;
                                
                                // Automatically trigger completion when ETA finishes naturally
                                if (!mapInstance.autoCompleted) {
                                    mapInstance.autoCompleted = true;
                                    let endpoint = `/api/tracking/${bookingId}/complete_self_transit`;
                                    if (data.current_leg === 'first_mile') {
                                        endpoint = `/api/tracking/${bookingId}/complete_first_mile`;
                                    } else if (data.current_leg === 'long_distance') {
                                        endpoint = `/api/tracking/${bookingId}/complete_main_transit`;
                                    } else if (data.current_leg === 'last_mile') {
                                        endpoint = `/api/tracking/${bookingId}/complete_last_mile`;
                                    }
                                    fetch(endpoint, { method: 'POST' })
                                        .catch(err => console.error("Auto-complete failed", err));
                                }
                            }
                            
                            const exactIndex = mapInstance.simProgress * (coords.length - 1);
                            const idx1 = Math.floor(exactIndex);
                            const idx2 = Math.min(Math.ceil(exactIndex), coords.length - 1);
                            const fraction = exactIndex - idx1;
                            
                            const targetCoord1 = coords[idx1];
                            const targetCoord2 = coords[idx2];
                            
                            // LERP interpolation for smooth movement
                            const currentLat = targetCoord1[0] + (targetCoord2[0] - targetCoord1[0]) * fraction;
                            const currentLng = targetCoord1[1] + (targetCoord2[1] - targetCoord1[1]) * fraction;
                            
                            const iconEl = mapInstance.marker.getElement();
                            if (iconEl) {
                                iconEl.style.transition = 'transform 3.0s linear';
                            }
                            
                            mapInstance.marker.setLatLng([currentLat, currentLng]);
                            
                            // Only pan if the vehicle leaves the visible area; do not force zoom!
                            if (mapInstance.map && !mapInstance.map.getBounds().contains([currentLat, currentLng])) {
                                mapInstance.map.panTo([currentLat, currentLng], { animate: true, duration: 1.5 });
                            }
                            
                            const newBearing = getBearing(targetCoord1[0], targetCoord1[1], targetCoord2[0], targetCoord2[1]);
                            if (iconEl && Math.abs(newBearing - mapInstance.currentBearing) > 5) {
                                const innerDiv = iconEl.querySelector('.pulse-danger');
                                if (innerDiv) innerDiv.style.transform = `rotate(${newBearing}deg)`;
                            }
                            mapInstance.currentBearing = newBearing;
                            
                            // Override UI ETA with dynamically calculated remaining time
                            data.eta_minutes = Math.max(0, Math.ceil(eta_mins * (1 - mapInstance.simProgress)));
                        }
                    } else {
                        mapInstance.marker.setLatLng([data.current_latitude, data.current_longitude]);
                        if (mapInstance.map && !mapInstance.map.getBounds().contains([data.current_latitude, data.current_longitude])) {
                            mapInstance.map.panTo([data.current_latitude, data.current_longitude]);
                        }
                    }
                    
                    // Update Marker Icon Dynamically
                    if (data.leg_info && data.leg_info.mode) {
                        const mode = data.leg_info.mode.toLowerCase();
                        let iconClass = 'bi-car-front-fill';
                        let bgClass = 'bg-primary';
                        let isEmoji = false;
                        let emojiChar = '';
                        
                        if (mode === 'bike') { iconClass = 'fa-solid fa-motorcycle'; bgClass = 'bg-success'; }
                        else if (mode === 'auto') { isEmoji = true; emojiChar = '🛺'; bgClass = 'bg-warning'; }
                        if (mode.includes('walk') || mode.includes('personal')) { iconClass = 'bi-person-walking'; bgClass = 'bg-success'; }
                        else if (mode.includes('bike')) { iconClass = 'fa-solid fa-motorcycle'; bgClass = 'bg-info'; }
                        else if (mode.includes('auto')) { isEmoji = true; emojiChar = '🛺'; bgClass = 'bg-success'; }
                        else if (mode.includes('bus')) { iconClass = 'bi-bus-front-fill'; bgClass = 'bg-warning text-dark'; }
                        else if (mode.includes('train')) { iconClass = 'bi-train-front-fill'; bgClass = 'bg-danger'; }
                        
                        const fontIconClass = iconClass.startsWith('bi-') ? `bi ${iconClass}` : iconClass;
                        const bearing = mapInstance.currentBearing || 0;
                        
                        if (mapInstance.currentIconMode !== mode) {
                            mapInstance.currentIconMode = mode;
                            const innerHtml = isEmoji ? `<span style="font-size: 14px; line-height: 1;">${emojiChar}</span>` : `<i class="${fontIconClass} text-white" style="font-size:14px;"></i>`;
                            const newIcon = L.divIcon({
                                className: 'custom-traveler-pin',
                                html: `<div class="pulse-danger ${bgClass}" style="width: 32px; height: 32px; border-radius:50%; border: 2px solid #fff; box-shadow: 0 0 15px rgba(255,255,255,0.5); display:flex; align-items:center; justify-content:center; transform: rotate(${bearing}deg); transition: transform 0.5s ease;">
                                           ${innerHtml}
                                       </div>`,
                                iconSize: [32, 32]
                            });
                            mapInstance.marker.setIcon(newIcon);
                        }
                    }
                } else if (mapInstance.type === 'svg') {
                    // Interpolate traveler position along SVG curve based on leg progression
                    const traveler = mapInstance.element;
                    const path = mapInstance.path;
                    const pathLength = path.getTotalLength();
                    
                    let progress = 0.1; // Default
                    if (data.current_leg === 'first_mile') progress = 0.2;
                    else if (data.current_leg === 'long_distance') progress = 0.55;
                    else if (data.current_leg === 'last_mile') progress = 0.85;
                    else if (data.current_leg === 'completed') progress = 1.0;
                    
                    // Animate SVG circle position
                    const point = path.getPointAtLength(pathLength * progress);
                    traveler.setAttribute('cx', point.x);
                    traveler.setAttribute('cy', point.y);
                }
                
                // Update ETA text
                const etaEl = document.getElementById('tracking-eta');
                if (etaEl) {
                    if (data.status === 'completed') {
                        etaEl.innerText = 'Arrived';
                    } else if (data.status === 'boarding' || data.status === 'driver_assigned' || data.status === 'pending') {
                        if (data.status === 'driver_assigned' && typeof mapInstance.approachProgress !== 'undefined' && mapInstance.approachProgress >= 1) {
                            etaEl.innerHTML = '<span style="font-size: 0.5em; color: #10b981;">DRIVER ARRIVED</span>';
                        } else {
                            if (data.eta_minutes && data.eta_minutes > 0) {
                                etaEl.innerText = data.eta_minutes + ' mins';
                            } else {
                                etaEl.innerHTML = '<span style="font-size: 0.5em; color: #10b981;">ARRIVING SOON</span>';
                            }
                        }
                    } else if (data.status === 'arrived_at_pickup' || data.status === 'arrived') {
                        etaEl.innerHTML = '<span style="font-size: 0.5em; color: #10b981;">DRIVER ARRIVED</span>';
                    } else {
                        if (data.eta_minutes <= 0) {
                            etaEl.innerHTML = '<span style="font-size: 0.5em; color: #10b981;">ARRIVING</span>';
                        } else {
                            etaEl.innerText = data.eta_minutes + ' mins';
                        }
                    }
                }
                
                // Trigger Dynamic Drop-off Modal if available
                if (typeof checkDynamicDropoff === 'function') {
                    checkDynamicDropoff(data.eta_minutes, data.current_leg);
                }
                
                if (data.status === 'completed') {
                    clearInterval(trackingInterval);
                    if (typeof triggerConfetti === 'function') {
                        triggerConfetti();
                    }
                    // Stay on the tracking page to show 'Arrived'
                }

                const legLabel = document.getElementById('tracking-current-leg');
                if (legLabel) {
                    const legNames = {
                        'first_mile': 'First Mile',
                        'long_distance': 'Long Distance',
                        'last_mile': 'Last Mile',
                        'completed': 'Journey Completed'
                    };
                    legLabel.innerText = legNames[data.current_leg] || data.current_leg;
                }
                
                const statusLabel = document.getElementById('tracking-status');
                if (statusLabel) {
                    statusLabel.className = `badge badge-glass ${data.status === 'completed' ? 'badge-glass-success' : 'badge-glass-primary'}`;
                    statusLabel.innerText = data.status.replace('_', ' ');
                }
                
                // Update timeline UI status
                updateTimelineUI(data.current_leg, data.status);
                
                // If trip completed, stop interval
                if (data.current_leg === 'completed' || data.booking_status === 'completed') {
                    clearInterval(trackingInterval);
                    
                    if (!window.journeyCompletedAlertShown) {
                        window.journeyCompletedAlertShown = true;
                        showNotification('Journey Completed!', 'You have safely arrived at your final destination.', 'success');
                    }
                    
                    // Hide SOS trigger button
                    const sosBtn = document.getElementById('sos-trigger-btn');
                    if (sosBtn) sosBtn.style.display = 'none';
                    
                    // Auto reload after 1.5s to render the Jinja "Journey Completed" and rating cards
                    // Check if h3 text contains "Journey Completed!" to see if page is already in completed view state
                    const hasCompletedHeader = Array.from(document.querySelectorAll('h3')).some(h => h.innerText && h.innerText.includes('Journey Completed!'));
                    if (!hasCompletedHeader) {
                        setTimeout(() => {
                            window.location.reload();
                        }, 1500);
                    }
                }
            })
            .catch(err => console.error("Error polling tracking details:", err));
    };
    
    // Perform initial fetch
    updatePosition();
    
    // Poll every 3 seconds to animate transitions smoothly
    trackingInterval = setInterval(updatePosition, 3000);
}

// Sync timeline css classes based on route progress
function updateTimelineUI(currentLeg, status) {
    const legs = ['first_mile', 'long_distance', 'last_mile'];
    const activeIdx = currentLeg === 'completed' ? 3 : legs.indexOf(currentLeg);
    
    legs.forEach((leg, idx) => {
        const item = document.getElementById(`leg-${leg}`);
        if (!item) return;
        
        const dot = item.querySelector('.phase-dot');
        const line = item.querySelector('.phase-line');
        const badge = item.querySelector('.phase-badge');
        const actionBtn = document.getElementById(`action-${leg}`);
        const icon = item.querySelector('i');
        
        if (idx < activeIdx || currentLeg === 'completed') {
            item.style.opacity = '1';
            if (dot) { dot.style.background = 'rgba(16,185,129,0.1)'; dot.style.border = '2px solid #10b981'; dot.classList.remove('pulse-cyan'); }
            if (line) { line.style.background = '#10b981'; }
            if (badge) { badge.style.display = 'inline-block'; badge.className = 'badge phase-badge bg-success'; badge.innerText = 'COMPLETED'; }
            if (icon) { 
                icon.classList.remove('text-muted', 'text-accent-blue'); 
                icon.classList.add('text-success'); 
                if (!dot.querySelector('.tick-badge')) {
                    dot.style.position = 'relative';
                    dot.insertAdjacentHTML('beforeend', '<i class="bi bi-check-circle-fill text-success tick-badge" style="position:absolute; bottom:-5px; right:-5px; font-size:14px; background:#101520; border-radius:50%;"></i>');
                }
            }
            if (actionBtn) actionBtn.style.display = 'none';
        } else if (idx === activeIdx) {
            item.style.opacity = '1';
            if (dot) { dot.style.background = 'rgba(59,130,246,0.2)'; dot.style.border = '2px solid #3b82f6'; dot.classList.add('pulse-cyan'); }
            if (line) { line.style.background = 'repeating-linear-gradient(to bottom, #3b82f6 0, #3b82f6 5px, transparent 5px, transparent 10px)'; }
            if (badge) {
                badge.style.display = 'inline-block';
                if (status === 'driver_assigned' || status === 'arrived_at_pickup') {
                    badge.className = 'badge phase-badge bg-info text-dark'; badge.innerText = status === 'driver_assigned' ? 'ON WAY' : 'ARRIVED';
                } else if (status === 'in_transit') {
                    badge.className = 'badge phase-badge bg-primary'; badge.innerText = 'IN TRANSIT';
                } else {
                    badge.className = 'badge phase-badge bg-primary'; badge.innerText = 'ACTIVE';
                }
            }
            if (icon) { icon.classList.remove('text-muted'); icon.classList.add('text-accent-blue'); }
            if (actionBtn) actionBtn.style.display = 'block';
        } else {
            item.style.opacity = '0.5';
            if (dot) { dot.style.background = 'rgba(255,255,255,0.05)'; dot.style.border = '2px dashed rgba(255,255,255,0.2)'; dot.classList.remove('pulse-cyan'); }
            if (line) { line.style.background = 'repeating-linear-gradient(to bottom, rgba(255,255,255,0.1) 0, rgba(255,255,255,0.1) 5px, transparent 5px, transparent 10px)'; }
            if (badge) badge.style.display = 'none';
            if (actionBtn) actionBtn.style.display = 'none';
        }
    });
    
    const completedLeg = document.getElementById('leg-completed');
    if (completedLeg && currentLeg === 'completed') {
        completedLeg.style.opacity = '1';
        const dot = completedLeg.querySelector('.phase-dot');
        if (dot) { dot.style.background = 'rgba(16,185,129,0.1)'; dot.style.border = '2px solid #10b981'; }
        const icon = completedLeg.querySelector('i');
        if (icon) { icon.className = 'bi bi-geo-fill text-success'; }
    }
}
