// TravelFusion AI Driver Ride Simulation

let requestPoller = null;

function initDriverDashboard() {
    const onlineSwitch = document.getElementById('driver-online-switch');
    if (onlineSwitch) {
        onlineSwitch.addEventListener('change', function() {
            const isOnline = this.checked ? 1 : 0;
            updateOnlineStatus(isOnline);
        });
    }
    
    // Initial status check
    const statusVal = document.getElementById('driver-status-val');
    if (statusVal && statusVal.innerText.includes('ONLINE')) {
        startRequestPolling();
    }
}

function updateOnlineStatus(isOnline) {
    fetchAPI('/api/driver/toggle_online', 'POST', { online: isOnline })
        .then(res => {
            if (res.success) {
                const statusBadge = document.getElementById('driver-status-badge');
                if (statusBadge) {
                    if (isOnline) {
                        statusBadge.className = 'badge badge-glass badge-glass-success';
                        statusBadge.innerHTML = '<i class="bi bi-circle-fill me-1"></i> ONLINE';
                        startRequestPolling();
                    } else {
                        statusBadge.className = 'badge badge-glass badge-glass-danger';
                        statusBadge.innerHTML = '<i class="bi bi-circle-fill me-1"></i> OFFLINE';
                        stopRequestPolling();
                    }
                }
                showNotification('Status Updated', `You are now ${isOnline ? 'Online' : 'Offline'}.`, isOnline ? 'success' : 'warning');
            }
        });
}

function startRequestPolling() {
    if (requestPoller) clearInterval(requestPoller);
    
    const checkRequests = () => {
        fetch('/api/driver/check_requests')
            .then(res => res.json())
            .then(data => {
                if (data.has_request) {
                    clearInterval(requestPoller); // Stop polling when request is open
                    showRideRequestOverlay(data.ride);
                }
            })
            .catch(err => console.error("Error checking ride jobs:", err));
    };
    
    // Poll every 4 seconds
    requestPoller = setInterval(checkRequests, 4000);
    checkRequests(); // Instant check
}

function stopRequestPolling() {
    if (requestPoller) {
        clearInterval(requestPoller);
        requestPoller = null;
    }
}

// Display incoming job overlay
function showRideRequestOverlay(ride) {
    // Play alert tone
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(523.25, audioCtx.currentTime); // C5
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        setTimeout(() => osc.stop(), 500);
    } catch (e) {
        console.log("Audio request alert blocked.");
    }
    
    const overlay = document.createElement('div');
    overlay.id = 'ride-request-overlay';
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100vw';
    overlay.style.height = '100vh';
    overlay.style.backgroundColor = 'rgba(9, 15, 29, 0.9)';
    overlay.style.zIndex = '10000';
    overlay.style.display = 'flex';
    overlay.style.alignItems = 'center';
    overlay.style.justifyContent = 'center';
    
    overlay.innerHTML = `
        <div class="glass-card p-4 text-center fade-in-up" style="max-width: 420px; border: 2px solid var(--accent-blue);">
            <div class="pulse-danger mx-auto mb-3" style="width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background-color: rgba(37,99,235,0.15);">
                <i class="bi bi-bell-fill text-primary fs-3 animate-bounce"></i>
            </div>
            <h4 class="text-white fw-bold mb-1">New Ride Request!</h4>
            <span class="badge badge-glass badge-glass-primary mb-3">${ride.vehicle_type.toUpperCase()} LEG</span>
            
            <div class="text-start bg-dark p-3 rounded mb-4" style="background-color: rgba(255,255,255,0.02) !important; border: 1px solid var(--border-color);">
                <div class="mb-2 d-flex justify-content-between align-items-center">
                    <div>
                        <small class="text-muted d-block">PASSENGER</small>
                        <strong class="text-white">${ride.rider_name}</strong>
                    </div>
                    ${(() => {
                        let phoneVal = ride.rider_phone;
                        if (!phoneVal || phoneVal === 'None' || phoneVal === 'N/A' || phoneVal.startsWith('+910000')) {
                            phoneVal = '+919012345678';
                        }
                        return `
                        <a href="tel:${phoneVal}" class="badge bg-dark text-decoration-none">
                            <i class="bi bi-telephone-fill text-success me-1"></i>${phoneVal}
                        </a>`;
                    })()}
                </div>
                <div class="mb-2"><small class="text-muted d-block">PICKUP</small><strong class="text-white" style="font-size:0.9rem;">${ride.source}</strong></div>
                <div class="mb-2"><small class="text-muted d-block">DROP</small><strong class="text-white" style="font-size:0.9rem;">${ride.destination}</strong></div>
                <div><small class="text-muted d-block">ESTIMATED FARE</small><strong class="text-success fs-5">INR ${ride.fare}</strong></div>
            </div>
            
            <div class="d-flex gap-3">
                <button class="btn btn-glass flex-grow-1" onclick="respondToRide(${ride.booking_id}, 'reject')">Decline</button>
                <button class="btn btn-glow flex-grow-1" onclick="respondToRide(${ride.booking_id}, 'accept')">Accept Ride</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
}


function respondToRide(bookingId, action) {
    showCustomConfirm(
        'Confirm Action',
        `Are you sure you want to ${action} this ride request?`,
        function() {
            const overlay = document.getElementById('ride-request-overlay');
            if (overlay) overlay.remove();
            
            fetchAPI('/api/driver/respond_request', 'POST', { booking_id: bookingId, action: action })
                .then(res => {
                    if (action === 'accept') {
                        showNotification('Ride Accepted', 'Plotting route details. Pick up the passenger.', 'success');
                        // Reload dashboard to show active trip
                        setTimeout(() => { window.location.reload(); }, 1500);
                    } else {
                        showNotification('Ride Declined', 'Request returned to queue.', 'warning');
                        startRequestPolling();
                    }
                });
        }
    );
}

function updateTripLifecycle(bookingId, action, otpInput = null) {
    const proceed = () => {
        fetchAPI('/api/driver/trip/update', 'POST', { booking_id: bookingId, action: action, otp: otpInput })
            .then(res => {
                if (res.success) {
                    if (action === 'start') {
                        showNotification('Trip Started', 'Passenger trip is in transit. Drive carefully.', 'info');
                        // Fix: dynamically update UI instead of just reloading
                        const otpBox = document.querySelector('.input-group.mb-2');
                        const mapLockedBanner = document.getElementById('map-locked-banner');
                        if (otpBox) otpBox.style.display = 'none';
                        if (mapLockedBanner) mapLockedBanner.style.display = 'none';
                        
                        // Show "Complete Ride" button immediately!
                        const btnCompleteRed = document.createElement('button');
                        btnCompleteRed.className = 'btn btn-glow-danger w-100 py-2 fw-700 mt-2';
                        btnCompleteRed.innerHTML = '<i class="bi bi-check-circle-fill me-2"></i>Complete Ride';
                        btnCompleteRed.onclick = () => updateTripLifecycle(bookingId, 'complete');
                        
                        // Append to the container holding the original otpBox
                        if (otpBox && otpBox.parentNode) {
                            otpBox.parentNode.appendChild(btnCompleteRed);
                            // Also hide the hint text
                            const hintText = otpBox.nextElementSibling;
                            if (hintText && hintText.tagName === 'SMALL') hintText.style.display = 'none';
                        }
                        
                        // RESTORE OLD GREEN BUTTON IN THE MAP
                        const btnComplete = document.createElement('button');
                        btnComplete.className = 'btn btn-sm btn-success w-100 mt-2 fw-bold';
                        btnComplete.id = 'btn-complete-ride';
                        btnComplete.innerHTML = '<i class="bi bi-check-circle-fill me-1"></i>Complete Ride';
                        btnComplete.onclick = () => updateTripLifecycle(bookingId, 'complete');
                        
                        const mapOverlay = document.getElementById('driver-map-overlay');
                        if (mapOverlay) {
                            const lockDiv = mapOverlay.querySelector('.text-center') || mapOverlay.querySelector('div[style*="#f59e0b"]');
                            if (lockDiv) {
                                lockDiv.replaceWith(btnComplete);
                            } else {
                                mapOverlay.appendChild(btnComplete);
                            }
                        } else {
                            const container = document.querySelector('.card-body');
                            if (container) container.appendChild(btnComplete);
                        }
                        
                        // Start map animation directly so user sees it move immediately
                        try {
                            const lockPopup = document.querySelector('.leaflet-popup');
                            if (lockPopup) lockPopup.remove();
                            
                            if (typeof window.globalTrackingMapObj !== 'undefined' && typeof window.globalTrackingLegsData !== 'undefined' && window.globalTrackingLegsData && window.globalTrackingLegsData.length > 0) {
                                const mapObj = window.globalTrackingMapObj;
                                const legsData = window.globalTrackingLegsData;
                                const leg = legsData[0];
                                const startLat = leg.start_coords[0];
                                const startLng = leg.start_coords[1];
                                const endLat = leg.end_coords[0];
                                const endLng = leg.end_coords[1];
                                
                                let progress = 0;
                                const totalSteps = 120;
                                const animInterval = setInterval(() => {
                                    progress += 1;
                                    if (progress > totalSteps) { clearInterval(animInterval); return; }
                                    const path = (mapObj.geoPaths && mapObj.geoPaths[leg.leg_type]) ? mapObj.geoPaths[leg.leg_type] : [[startLat, startLng], [endLat, endLng]];
                                    const pct = progress / totalSteps;
                                    const totalSeg = path.length - 1;
                                    const ei = pct * totalSeg;
                                    const lo = Math.floor(ei), hi = Math.min(Math.ceil(ei), totalSeg);
                                    const sp = ei - lo;
                                    const p1 = path[lo], p2 = path[hi];
                                    if (p1 && p2 && mapObj.marker) {
                                        mapObj.marker.setLatLng([p1[0]+(p2[0]-p1[0])*sp, p1[1]+(p2[1]-p1[1])*sp]);
                                    }
                                    const etaEl = document.getElementById('driver-eta');
                                    if (etaEl) etaEl.innerText = Math.max(0, Math.round((leg.eta_mins || 15)*(1-pct)));
                                }, 1000);
                                
                                // Change map center
                                mapObj.map.setView([startLat, startLng], 14);
                            }
                        } catch (e) {
                            console.error("Animation start failed:", e);
                        }
                    } else if (action === 'complete') {
                        showNotification('Trip Completed!', 'Fare credits added to your driver wallet.', 'success');
                        setTimeout(() => { window.location.reload(); }, 1500);
                    }
                } else {
                    showNotification('Error', res.error || 'Invalid OTP or Action Failed', 'danger');
                }
            })
            .catch(err => {
                showNotification('Server Error', 'Failed to connect: ' + err.message, 'danger');
                console.error('updateTripLifecycle error:', err);
            });
    };

    if (action === 'complete') {
        showCustomConfirm(
            'Complete Ride',
            'Are you sure you want to complete this ride?',
            proceed
        );
    } else {
        proceed();
    }
}
