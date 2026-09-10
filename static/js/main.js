// TravelFusion AI Shared Javascript Utilities

// 1. Unified Fetch API Wrapper
async function fetchAPI(url, method = 'GET', body = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
    };
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            const errText = await response.text();
            throw new Error(errText || `HTTP error ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`API Call failed on ${url}:`, error);
        showNotification('System Error', error.message || 'Action failed.', 'danger');
        throw error;
    }
}

// 2. Premium Toast Notification Overlay System (iOS-style Banner)
function showNotification(title, message, type = 'info') {
    // Check if container exists, else create it
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.style.position = 'fixed';
        container.style.top = '15px';
        container.style.left = '50%';
        container.style.transform = 'translateX(-50%)';
        container.style.width = '90%';
        container.style.maxWidth = '360px';
        container.style.zIndex = '99999';
        container.style.display = 'flex';
        container.style.flexDirection = 'column';
        container.style.gap = '10px';
        document.body.appendChild(container);
    }
    
    const notification = document.createElement('div');
    // Mobile OS style notification card design
    notification.style.background = 'rgba(20, 20, 25, 0.88)';
    notification.style.backdropFilter = 'blur(20px) saturate(180%)';
    notification.style.webkitBackdropFilter = 'blur(20px) saturate(180%)';
    notification.style.border = '1px solid rgba(255, 255, 255, 0.1)';
    notification.style.borderRadius = '18px';
    notification.style.padding = '12px 16px';
    notification.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.5)';
    notification.style.transition = 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)';
    notification.style.transform = 'translateY(-20px)';
    notification.style.opacity = '0';
    
    // Choose indicator color
    const colors = {
        success: 'var(--success-green, #10b981)',
        danger: 'var(--danger-red, #ef4444)',
        warning: 'var(--warning-yellow, #f59e0b)',
        info: 'var(--accent-blue, #0ea5e9)'
    };
    const accentColor = colors[type] || colors.info;
    
    // Icon selection
    const icons = {
        success: 'bi-check-circle-fill text-success',
        danger: 'bi-exclamation-triangle-fill text-danger',
        warning: 'bi-exclamation-circle-fill text-warning',
        info: 'bi-info-circle-fill text-info'
    };
    const icon = icons[type] || icons.info;
    
    notification.innerHTML = `
        <div class="d-flex align-items-center mb-1 text-muted" style="font-size: 0.72rem; letter-spacing: 0.5px;">
            <i class="bi bi-compass-fill me-1" style="color: ${accentColor}; font-size: 0.8rem;"></i>
            <span class="fw-semibold text-light text-uppercase">TravelFusion</span>
            <span class="mx-1">•</span>
            <span>now</span>
            <button type="button" class="btn-close btn-close-white ms-auto" style="font-size: 0.6rem; opacity: 0.5; box-shadow: none;" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
        <div class="d-flex align-items-start mt-1">
            <i class="bi ${icon} fs-5 me-2 mt-0.5"></i>
            <div class="flex-grow-1">
                <h6 class="mb-0 fw-bold text-white" style="font-size: 0.9rem;">${title}</h6>
                <p class="mb-0 text-secondary" style="font-size: 0.8rem; line-height: 1.35;">${message}</p>
            </div>
        </div>
    `;
    
    container.appendChild(notification);
    
    // Trigger entry animation
    requestAnimationFrame(() => {
        notification.style.transform = 'translateY(0)';
        notification.style.opacity = '1';
    });
    
    // Play system notification chime sound
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === 'suspended') {
            audioCtx.resume();
        }
        
        if (title.includes('SOS')) {
            // SOS Alarm - plays a single continuous beep that lasts until the notification goes away
            try {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(880, audioCtx.currentTime); // High pitch alert
                gain.gain.setValueAtTime(0.35, audioCtx.currentTime); // 35% volume
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                
                // Stop the tone immediately when the notification card is dismissed or removed
                const monitorInterval = setInterval(() => {
                    if (!notification.parentElement) {
                        clearInterval(monitorInterval);
                        try {
                            osc.stop();
                            audioCtx.close();
                        } catch(e){}
                    }
                }, 100);
            } catch(e){}
        } else {
            // Standard notification sound
            const osc = audioCtx.createOscillator();
            const gainNode = audioCtx.createGain();
            osc.type = 'sine';
            if (type === 'danger') {
                // SOS double low-high alert
                osc.frequency.setValueAtTime(587.33, audioCtx.currentTime); // D5
                osc.frequency.setValueAtTime(659.25, audioCtx.currentTime + 0.1); // E5
                gainNode.gain.setValueAtTime(0.04, audioCtx.currentTime);
            } else {
                // Friendly double chirp
                osc.frequency.setValueAtTime(783.99, audioCtx.currentTime); // G5
                osc.frequency.setValueAtTime(1046.50, audioCtx.currentTime + 0.08); // C6
                gainNode.gain.setValueAtTime(0.03, audioCtx.currentTime);
            }
            osc.connect(gainNode);
            gainNode.connect(audioCtx.destination);
            osc.start();
            setTimeout(() => {
                osc.stop();
                audioCtx.close();
            }, 300);
        }
    } catch(e) {}
    
    // Mobile Vibrate Feedback (Haptics)
    if (navigator.vibrate) {
        if (type === 'danger') {
            navigator.vibrate([100, 50, 100]);
        } else if (type === 'warning') {
            navigator.vibrate([80]);
        } else {
            navigator.vibrate([40]);
        }
    }
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                notification.remove();
            }, 400);
        }
    }, 5000);
}

// 3. Global Custom Confirm Modal
function showCustomConfirm(title, message, onConfirm) {
    const modalId = 'custom-confirm-modal';
    let modalEl = document.getElementById(modalId);
    if (!modalEl) {
        modalEl = document.createElement('div');
        modalEl.id = modalId;
        modalEl.className = 'modal fade';
        modalEl.setAttribute('tabindex', '-1');
        modalEl.setAttribute('aria-hidden', 'true');
        modalEl.style.zIndex = '1055';
        document.body.appendChild(modalEl);
    }

    modalEl.innerHTML = `
        <div class="modal-dialog modal-dialog-centered" style="max-width: 400px;">
            <div class="modal-content border border-secondary border-opacity-25 shadow-lg" style="background: #090f1d; color: white; border-radius: 16px; backdrop-filter: blur(20px);">
                <div class="modal-header border-bottom border-secondary border-opacity-25 py-2">
                    <h6 class="modal-title m-0 text-info"><i class="bi bi-question-circle-fill me-2"></i>${title}</h6>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close" style="font-size: 0.75rem;"></button>
                </div>
                <div class="modal-body text-center py-4">
                    <p class="mb-0 text-white" style="font-size: 0.95rem;">${message}</p>
                </div>
                <div class="modal-footer border-top border-secondary border-opacity-25 py-2 d-flex justify-content-between">
                    <button type="button" class="btn btn-outline-secondary px-3 py-1 btn-sm" data-bs-dismiss="modal" style="border-radius: 8px;">Cancel</button>
                    <button type="button" class="btn btn-info text-white px-3 py-1 btn-sm" id="custom-confirm-btn" style="border-radius: 8px;">Confirm</button>
                </div>
            </div>
        </div>
    `;

    const bsModal = new bootstrap.Modal(modalEl);
    
    const confirmBtn = document.getElementById('custom-confirm-btn');
    confirmBtn.onclick = function() {
        bsModal.hide();
        onConfirm();
    };

    bsModal.show();
}

// 4. Emergency SOS Location Dispatch
function triggerEmergencySOS(bookingId = null) {
    showCustomConfirm(
        'Trigger Emergency SOS',
        'WARNING: You are triggering an emergency SOS. This will immediately alert authorities and notify your emergency contacts with your current location. Do you wish to proceed?',
        function() {
            // Fallback default coordinates (Bangalore)
            let lat = 12.9716;
            let lng = 77.5946;
            
            const sendSOS = (latitude, longitude) => {
                fetchAPI('/api/emergency/sos', 'POST', {
                    booking_id: bookingId,
                    latitude: latitude,
                    longitude: longitude
                }).then(response => {
                    if (response.success) {
                        showNotification('SOS Sent Successfully', `Alerted: ${response.notified_contacts.join(', ')}`, 'success');
                        // Play distress sound indicator (soft, short chime)
                        try {
                            const context = new (window.AudioContext || window.webkitAudioContext)();
                            const osc = context.createOscillator();
                            const gainNode = context.createGain();
                            
                            osc.type = 'sine'; // Soft sine wave
                            osc.frequency.setValueAtTime(523.25, context.currentTime); // Gentle C5 chime
                            
                            gainNode.gain.setValueAtTime(0.08, context.currentTime); // Low volume (8%)
                            
                            osc.connect(gainNode);
                            gainNode.connect(context.destination);
                            
                            osc.start();
                            setTimeout(() => {
                                osc.stop();
                            }, 200); // 200ms duration (quick and mild)
                        } catch (e) {
                            console.log("Audio alert blocked by browser permissions.");
                        }
                    }
                }).catch(err => {
                    console.error("SOS Dispatch failed:", err);
                });
            };
            
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (pos) => {
                        sendSOS(pos.coords.latitude, pos.coords.longitude);
                    },
                    (err) => {
                        console.warn("Geolocation denied or blocked. Sending default simulated location coordinates...");
                        sendSOS(lat, lng);
                    },
                    { timeout: 3000 }
                );
            } else {
                sendSOS(lat, lng);
            }
        }
    );
}

// 6. Global Premium Theme Selector Logic
function setGlobalTheme(themeName) {
    // Save to localStorage
    localStorage.setItem('global-theme', themeName);
    
    // Apply class to body
    const body = document.body;
    body.className = body.className.replace(/\btheme-\S+/g, '');
    if (themeName !== 'dark') {
        body.classList.add('theme-' + themeName);
    }
    
    // Highlight active button on landing page if panel exists
    document.querySelectorAll('.theme-option-btn').forEach(btn => {
        btn.classList.remove('active');
        btn.style.borderColor = 'var(--border-color)';
    });
    
    const activeBtn = document.getElementById('theme-opt-' + themeName);
    if (activeBtn) {
        activeBtn.classList.add('active');
        activeBtn.style.borderColor = 'var(--accent-blue)';
    }
}

