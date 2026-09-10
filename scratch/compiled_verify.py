def render_func(context, session, request):
    result = []
    result.append('<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>Secure Scanner | TravelFusion AI</title>\n    <!-- Google Fonts -->\n    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Share+Tech+Mono&display=swap" rel="stylesheet">\n    <!-- Bootstrap 5 -->\n    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">\n    <!-- Bootstrap Icons -->\n    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">\n    <style>\n        :root {\n            --bg-color: #050914;\n            --panel-bg: rgba(13, 20, 38, 0.85);\n            --neon-green: #10b981;\n            --neon-red: #ef4444;\n            --neon-blue: #0ea5e9;\n        }\n        body {\n            background-color: var(--bg-color);\n            background-image: \n                radial-gradient(circle at 50% 0%, rgba(14, 165, 233, 0.1) 0%, transparent 50%),\n                linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),\n                linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);\n            background-size: 100% 100%, 30px 30px, 30px 30px;\n            color: #fff;\n            font-family: \'Outfit\', sans-serif;\n            min-height: 100vh;\n            margin: 0;\n            padding: 20px 10px;\n            overflow-x: hidden;\n            overflow-y: auto;\n        }\n        \n        /* SCANNING SCREEN */\n        #scanning-screen {\n            display: flex;\n            flex-direction: column;\n            align-items: center;\n            justify-content: center;\n            position: fixed;\n            top: 0; left: 0; width: 100%; height: 100%;\n            background: var(--bg-color);\n            z-index: 10;\n        }\n        .scanner-box {\n            position: relative;\n            width: 200px;\n            height: 200px;\n            border: 2px solid rgba(14, 165, 233, 0.3);\n            border-radius: 20px;\n            overflow: hidden;\n            box-shadow: 0 0 30px rgba(14, 165, 233, 0.1) inset;\n            margin-bottom: 2rem;\n        }\n        .scanner-box::before, .scanner-box::after {\n            content: \'\'; position: absolute; width: 20px; height: 20px; border-color: var(--neon-blue); border-style: solid;\n        }\n        .scanner-box::before { top: 0; left: 0; border-width: 3px 0 0 3px; border-top-left-radius: 15px; }\n        .scanner-box::after { bottom: 0; right: 0; border-width: 0 3px 3px 0; border-bottom-right-radius: 15px; }\n        \n        .scan-line {\n            position: absolute;\n            top: 0;\n            left: 0;\n            width: 100%;\n            height: 4px;\n            background: var(--neon-blue);\n            box-shadow: 0 0 20px var(--neon-blue), 0 0 40px var(--neon-blue);\n            animation: scan 1.5s ease-in-out infinite alternate;\n        }\n        @keyframes scan {\n            0% { top: 5%; }\n            100% { top: 95%; }\n        }\n        .scan-text {\n            font-family: \'Share Tech Mono\', monospace;\n            font-size: 1.2rem;\n            color: var(--neon-blue);\n            letter-spacing: 4px;\n            animation: pulse 1s infinite;\n        }\n        \n        /* RESULT SCREEN / MOBILE BOARDING PASS */\n        #result-screen {\n            display: none;\n            width: 100%;\n            max-width: 500px;\n            margin: 0 auto;\n            animation: slideUp 0.5s ease-out;\n            padding-bottom: 40px;\n        }\n        @keyframes slideUp {\n            from { opacity: 0; transform: translateY(30px); }\n            to { opacity: 1; transform: translateY(0); }\n        }\n        \n        .boarding-pass {\n            background: linear-gradient(145deg, rgba(16,25,50,0.95), rgba(5,9,26,0.98));\n            border: 1px solid rgba(59,130,246,0.4);\n            box-shadow: 0 10px 40px rgba(0,0,0,0.5);\n            border-radius: 20px;\n            overflow: hidden;\n            position: relative;\n        }\n        .bp-header {\n            background: linear-gradient(90deg, #3b82f6, #10b981, #f59e0b);\n            height: 6px;\n            width: 100%;\n        }\n        .bp-header.invalid {\n            background: linear-gradient(90deg, #ef4444, #f97316);\n        }\n        .bp-watermark {\n            position: absolute;\n            top: 50%;\n            left: 50%;\n            transform: translate(-50%, -50%) rotate(-25deg);\n            font-size: 5rem;\n            font-weight: 900;\n            color: rgba(255,255,255,0.02);\n            white-space: nowrap;\n            pointer-events: none;\n            z-index: 0;\n        }\n        .bp-content {\n            padding: 2rem;\n            position: relative;\n            z-index: 2;\n        }\n        .data-grid {\n            display: grid;\n            gap: 1.2rem;\n        }\n        .data-item {\n            background: rgba(255,255,255,0.03);\n            border: 1px solid rgba(255,255,255,0.05);\n            padding: 1rem;\n            border-radius: 12px;\n        }\n        .data-label {\n            font-size: 0.7rem;\n            text-transform: uppercase;\n            letter-spacing: 2px;\n            color: #94a3b8;\n            margin-bottom: 6px;\n        }\n        .data-val {\n            font-size: 1.1rem;\n            font-weight: 700;\n            color: #fff;\n        }\n    </style>\n</head>\n<body>\n\n    <!-- SCANNING ANIMATION -->\n    <div id="scanning-screen">\n        <div class="scanner-box">\n            <i class="bi bi-qr-code" style="font-size: 8rem; color: rgba(255,255,255,0.1); position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);"></i>\n            <div class="scan-line"></div>\n        </div>\n        <div class="scan-text">VERIFYING DIGITAL TICKET...</div>\n    </div>\n\n    <!-- MOBILE BOARDING PASS DISPLAY -->\n    <div id="result-screen">\n        ')
    if valid:
        result.append('\n        <div class="boarding-pass mt-4">\n            <div class="bp-header"></div>\n            <div class="bp-watermark">VERIFIED TICKET</div>\n            <div class="bp-content">\n                <div class="d-flex justify-content-between align-items-center mb-4">\n                    <div>\n                        <div class="text-muted" style="font-size:0.75rem;letter-spacing:2px;">TRAVELFUSION AI</div>\n                        <h4 class="text-white mb-0 mt-1 fw-bold">E-BOARDING PASS</h4>\n                    </div>\n                    <div class="badge bg-success bg-opacity-25 text-success border border-success border-opacity-50 px-3 py-2" style="border-radius:8px;">\n                        <i class="bi bi-patch-check-fill me-1"></i>VERIFIED\n                    </div>\n                </div>\n\n                <div class="d-flex justify-content-between align-items-center mb-4 pb-4" style="border-bottom: 1px dashed rgba(255,255,255,0.15);">\n                    <div>\n                        <p class="data-label mb-1">DEPARTURE</p>\n                        <h3 class="text-white fw-bold mb-0">')
        try:
            val = booking.source.split(',')[0]
            result.append(str(val) if val is not None else '')
        except Exception as e:
            result.append(f'<!-- Template Expr Error on booking.source.split(\',\')[0]: {e} -->')
        result.append('</h3>\n                    </div>\n                    ')
        if train:
            result.append('\n                    <i class="bi bi-train-front-fill fs-1 mx-3" style="color: #10b981; filter: drop-shadow(0 0 10px rgba(16,185,129,0.5));"></i>\n                    ')
        elif bus:
            result.append('\n                    <i class="bi bi-bus-front-fill fs-1 mx-3" style="color: #f59e0b; filter: drop-shadow(0 0 10px rgba(245,158,11,0.5));"></i>\n                    ')
        elif flight:
            result.append('\n                    <i class="bi bi-airplane-fill fs-1 mx-3" style="color: #3b82f6; filter: drop-shadow(0 0 10px rgba(59,130,246,0.5));"></i>\n                    ')
        elif ride:
            result.append('\n                    <i class="bi bi-car-front-fill fs-1 mx-3" style="color: #a855f7; filter: drop-shadow(0 0 10px rgba(168,85,247,0.5));"></i>\n                    ')
        else:
            result.append('\n                    <i class="bi bi-ticket-detailed-fill fs-1 mx-3" style="color: #94a3b8; filter: drop-shadow(0 0 10px rgba(148,163,184,0.5));"></i>\n                    ')
        result.append('\n                    <div class="text-end">\n                        <p class="data-label mb-1">ARRIVAL</p>\n                        <h3 class="text-white fw-bold mb-0">')
        try:
            val = booking.destination.split(',')[0]
            result.append(str(val) if val is not None else '')
        except Exception as e:
            result.append(f'<!-- Template Expr Error on booking.destination.split(\',\')[0]: {e} -->')
        result.append('</h3>\n                    </div>\n                </div>\n\n                <div class="data-grid mb-4">\n                    <div class="data-item">\n                        <div class="data-label">Passenger Name</div>\n                        <div class="data-val text-uppercase">')
        try:
            val = booking.passenger_name
            result.append(str(val) if val is not None else '')
        except Exception as e:
            result.append(f'<!-- Template Expr Error on booking.passenger_name: {e} -->')
        result.append('</div>\n                    </div>\n                    <div class="row g-3 m-0">\n                        <div class="col-6 p-0 pe-2">\n                            <div class="data-item h-100">\n                                <div class="data-label">Date</div>\n                                <div class="data-val">')
        try:
            val = booking.travel_date
            result.append(str(val) if val is not None else '')
        except Exception as e:
            result.append(f'<!-- Template Expr Error on booking.travel_date: {e} -->')
        result.append('</div>\n                            </div>\n                        </div>\n                        <div class="col-6 p-0 ps-2">\n                            <div class="data-item h-100">\n                                <div class="data-label">Booking PNR</div>\n                                <div class="data-val text-info">TF-')
        try:
            val = booking.id
            result.append(str(val) if val is not None else '')
        except Exception as e:
            result.append(f'<!-- Template Expr Error on booking.id: {e} -->')
        result.append('</div>\n                            </div>\n                        </div>\n                    </div>\n                </div>\n\n                <div class="p-3 mb-4 rounded-3" style="background: rgba(16,185,129,0.05); border-left: 3px solid #10b981;">\n                    <h6 class="text-white mb-3" style="font-size:0.85rem;"><i class="bi bi-info-circle-fill me-2"></i>Transit Confirmation Details</h6>\n                    \n                    ')
        if train:
            result.append('\n                    <div class="d-flex justify-content-between mb-2"><span class="text-muted small">Train No</span> <span class="text-white fw-bold font-monospace">')
            try:
                val = train.train_number
                result.append(str(val) if val is not None else '')
            except Exception as e:
                result.append(f'<!-- Template Expr Error on train.train_number: {e} -->')
            result.append('</span></div>\n                    <div class="d-flex justify-content-between mb-2"><span class="text-muted small">Coach & Seat</span> <span class="text-white fw-bold">')
            try:
                val = train.coach_number
                result.append(str(val) if val is not None else '')
            except Exception as e:
                result.append(f'<!-- Template Expr Error on train.coach_number: {e} -->')
            result.append(' - ')
            try:
                val = train.seat_number
                result.append(str(val) if val is not None else '')
            except Exception as e:
                result.append(f'<!-- Template Expr Error on train.seat_number: {e} -->')
            result.append('</span></div>\n                    <div class="d-flex justify-content-between"><span class="text-muted small">Departure Time</span> <span class="text-warning fw-bold">')
            try:
                val = str(train.departure_time)[:16].replace('T', ' ')
                result.append(str(val) if val is not None else '')
            except Exception as e:
                result.append(f'<!-- Template Expr Error on str(train.departure_time)[:16].replace(\'T\', \' \'): {e} -->')
            result.append('</span></div>\n                    ')
        result.append('\n                    \n                    ')
        if flight:
            result.append('\n                    <div class="d-flex justify-content-between mb-2"><span class="text-muted small">Flight No</span> <span class="text-white fw-bold font-monospace">')
            try:
                val = flight.flight_number
                result.append(str(val) if val is not None else '')
            except Exception as e:
                result.append(f'<!-- Template Expr Error on flight.flight_number: {e} -->')
            result.append('</span></div>\n                    <div class="d-flex justify-content-between mb-2"><span class="text-muted small">Gate & Seat</span> <span class="text-white fw-bold">')
            try:
                val = flight.gate
                result.append(str(val) if val is not None else '')
            except Exception as e:
                result.append(f'<!-- Template Expr Error on flight.gate: {e} -->')
            result.append(' / ')
            try:
                val = flight.seat_number
                result.append(str(val) if val is not None else '')
            except Exception as e:
                result.append(f'<!-- Template Expr Error on flight.seat_number: {e} -->')
            result.append('</span></div>\n                    <div class="d-flex justify-content-between"><span class="text-muted small">Boarding Time</span> <span class="text-warning fw-bold">')
            try:
                val = str(flight.departure_time)[:16].replace('T', ' ')
                result.append(str(val) if val is not None else '')
            except Exception as e:
                result.append(f'<!-- Template Expr Error on str(flight.departure_time)[:16].replace(\'T\', \' \'): {e} -->')
            result.append('</span></div>\n                    ')
        result.append('\n                    \n                    ')
        if bus:
            result.append('\n                    <div class="d-flex justify-content-between mb-2"><span class="text-muted small">Bus Operator</span> <span class="text-white fw-bold">')
            try:
                val = bus.operator_name
                result.append(str(val) if val is not None else '')
            except Exception as e:
                result.append(f'<!-- Template Expr Error on bus.operator_name: {e} -->')
            result.append('</span></div>\n                    <div class="d-flex justify-content-between mb-2"><span class="text-muted small">Seat No</span> <span class="text-white fw-bold font-monospace">')
            try:
                val = bus.seat_number
                result.append(str(val) if val is not None else '')
            except Exception as e:
                result.append(f'<!-- Template Expr Error on bus.seat_number: {e} -->')
            result.append('</span></div>\n                    <div class="d-flex justify-content-between"><span class="text-muted small">Departure Time</span> <span class="text-warning fw-bold">')
            try:
                val = str(bus.departure_time)[:16].replace('T', ' ')
                result.append(str(val) if val is not None else '')
            except Exception as e:
                result.append(f'<!-- Template Expr Error on str(bus.departure_time)[:16].replace(\'T\', \' \'): {e} -->')
            result.append('</span></div>\n                    ')
        result.append('\n                    \n                    ')
        if ride:
            result.append('\n                    <div class="d-flex justify-content-between mb-2"><span class="text-muted small">Vehicle</span> <span class="text-white fw-bold">')
            try:
                val = ride.vehicle_type.upper()
                result.append(str(val) if val is not None else '')
            except Exception as e:
                result.append(f'<!-- Template Expr Error on ride.vehicle_type.upper(): {e} -->')
            result.append(' Ride</span></div>\n                    <div class="d-flex justify-content-between mb-2"><span class="text-muted small">Status</span> <span class="text-success fw-bold">Confirmed</span></div>\n                    <div class="d-flex justify-content-between"><span class="text-muted small">Fare Paid</span> <span class="text-warning fw-bold">₹')
            try:
                val = ride.fare
                result.append(str(val) if val is not None else '')
            except Exception as e:
                result.append(f'<!-- Template Expr Error on ride.fare: {e} -->')
            result.append('</span></div>\n                    ')
        result.append('\n                </div>\n\n                <div class="text-center pt-3 mt-4" style="border-top: 2px dashed rgba(255,255,255,0.15);">\n                    <div class="d-inline-block p-2 bg-white rounded-3 shadow-sm mb-3">\n                        <div id="real-qrcode" style="width: 140px; height: 140px;"></div>\n                    </div>\n                    <div class="text-muted" style="font-family: \'Share Tech Mono\', monospace; letter-spacing: 3px;">SCAN TO VALIDATE</div>\n                </div>\n            </div>\n        </div>\n        ')
    else:
        result.append('\n        <div class="boarding-pass mt-4" style="border-color: rgba(239,68,68,0.4);">\n            <div class="bp-header invalid"></div>\n            <div class="bp-watermark" style="color: rgba(239,68,68,0.03);">REJECTED</div>\n            <div class="bp-content text-center">\n                <i class="bi bi-shield-fill-x text-danger mb-3" style="font-size: 4rem;"></i>\n                <h3 class="mb-1 fw-bold text-danger" style="letter-spacing: 1px;">ACCESS DENIED</h3>\n                <div class="badge bg-danger bg-opacity-25 text-danger border border-danger border-opacity-50 px-3 py-1 mt-2 mb-4" style="letter-spacing: 2px;">INVALID QR CODE</div>\n                \n                <div class="data-item text-center">\n                    <span class="data-label text-danger">SECURITY ALERT</span>\n                    <span class="data-val d-block mt-2" style="font-size: 0.85rem; font-family: \'Outfit\', sans-serif; font-weight: normal; color: #cbd5e1; line-height: 1.5;">\n                        This ticket reference does not exist in the secure database or the signature has been tampered with.\n                    </span>\n                </div>\n            </div>\n        </div>\n        ')
    result.append('\n    </div>\n\n    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>\n    <script>\n        document.addEventListener("DOMContentLoaded", function() {\n            // Setup real QR Code\n            const qrContainer = document.getElementById(\'real-qrcode\');\n            if (qrContainer) {\n                let hostIp = window.location.hostname;\n                let port = window.location.port ? \':\' + window.location.port : \'\';\n                new QRCode(qrContainer, {\n                    text: `http://${hostIp}${port}/verify/TF-')
    try:
        val = booking.id if booking else 'INVALID'
        result.append(str(val) if val is not None else '')
    except Exception as e:
        result.append(f'<!-- Template Expr Error on booking.id if booking else \'INVALID\': {e} -->')
    result.append('`,\n                    width: 104,\n                    height: 104,\n                    colorDark: "#000000",\n                    colorLight: "#ffffff",\n                    correctLevel: QRCode.CorrectLevel.H\n                });\n            }\n\n            // Simulate scanning delay for dramatic effect\n            setTimeout(() => {\n                document.getElementById(\'scanning-screen\').style.opacity = \'0\';\n                setTimeout(() => {\n                    document.getElementById(\'scanning-screen\').style.display = \'none\';\n                    document.getElementById(\'result-screen\').style.display = \'block\';\n                }, 300); // fade out duration\n            }, 1800); // 1.8 seconds scan time\n        });\n    </script>\n</body>\n</html>\n')
    return ''.join(result)