import urllib.parse
import datetime
import smtplib
import email.utils as email_utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import config
import os

def generate_html_ticket(details, booking_id):
    passengers = details.get('passengers', [])
    if passengers:
        name = ", ".join([p.get('name', 'Passenger') for p in passengers])
    else:
        name = details.get('passenger_name', 'Passenger')
        
    src = details.get('source', 'Source').split(',')[0]
    dst = details.get('destination', 'Destination').split(',')[0]
    date = details.get('date', 'N/A')
    fare = details.get('fare', '0')
    mode = details.get('mode', 'flight').lower()
    operator = details.get('operator', 'TravelFusion Select')
    seat = details.get('seat', 'AUTO')
    gate = details.get('gate', 'TBD')
    
    if mode == 'train':
        icon = '🚆'
        ticket_type = 'TRAIN E-TICKET'
    elif mode == 'bus':
        icon = '🚌'
        ticket_type = 'BUS BOARDING PASS'
    elif mode == 'ride':
        icon = '🚕'
        ticket_type = 'CAB RECEIPT'
    else:
        icon = '✈️'
        ticket_type = 'FLIGHT BOARDING PASS'
        
    passengers_count = len(passengers) if passengers else 1
    
    # Format time if present in date string
    formatted_time = "08:30 AM"
    if "T" in date:
        try:
            dt_obj = datetime.datetime.fromisoformat(date)
            formatted_time = dt_obj.strftime("%I:%M %p")
        except:
            formatted_time = date[11:16]
            
    html_content = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background: #e2e8f0; display: flex; justify-content: center; padding: 40px; }}
  .ticket {{ width: 850px; background: #fff; border-radius: 16px; display: flex; box-shadow: 0 15px 35px rgba(0,0,0,0.1); overflow: hidden; position: relative; }}
  .left {{ flex: 0 0 580px; padding: 35px; border-right: 2px dashed #cbd5e1; position: relative; }}
  .right {{ flex: 1; padding: 35px; background: #f8fafc; display: flex; flex-direction: column; align-items: center; justify-content: space-between; position: relative; }}
  .right::before, .right::after {{ content: ''; position: absolute; left: -15px; width: 30px; height: 30px; background: #e2e8f0; border-radius: 50%; box-shadow: inset 0 2px 4px rgba(0,0,0,0.05); }}
  .right::before {{ top: -15px; }} .right::after {{ bottom: -15px; }}
  
  .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid #f1f5f9; padding-bottom: 15px; margin-bottom: 25px; }}
  .brand-logo {{ font-size: 28px; font-weight: 900; color: #0f172a; letter-spacing: -1px; margin: 0; display: flex; align-items: center; gap: 8px; }}
  .brand-logo span {{ color: #3b82f6; }}
  .status-badge {{ background: #10b981; color: white; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; letter-spacing: 1px; }}
  
  .pnr-box {{ text-align: right; }}
  .pnr-title {{ font-size: 10px; color: #64748b; font-weight: bold; letter-spacing: 2px; margin-bottom: 2px; }}
  .pnr-val {{ font-size: 22px; font-weight: 900; color: #0f172a; letter-spacing: 1px; }}
  
  .row-data {{ display: flex; justify-content: space-between; margin-bottom: 25px; }}
  .label {{ font-size: 10px; color: #64748b; font-weight: bold; letter-spacing: 1px; margin-bottom: 5px; text-transform: uppercase; }}
  .val {{ font-size: 15px; font-weight: 700; color: #0f172a; }}
  
  .route-box {{ background: linear-gradient(135deg, #f8fafc, #f1f5f9); border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 30px; }}
  .city-code {{ font-size: 36px; font-weight: 900; color: #0f172a; line-height: 1.1; }}
  .city-name {{ font-size: 13px; color: #475569; margin-top: 5px; font-weight: 500; }}
  .city-time {{ font-size: 15px; color: #3b82f6; font-weight: 800; margin-top: 8px; }}
  
  .icon-wrapper {{ width: 30%; text-align: center; position: relative; }}
  .icon-symbol {{ font-size: 28px; color: #3b82f6; background: #fff; padding: 0 10px; position: relative; z-index: 2; }}
  .route-line {{ border-bottom: 2px dashed #cbd5e1; width: 100%; position: absolute; top: 50%; left: 0; z-index: 1; }}
  
  .qr-box {{ width: 130px; height: 130px; background: #fff; border: 1px solid #e2e8f0; padding: 10px; border-radius: 10px; margin: 15px 0; }}
  .barcode {{ width: 100%; height: 50px; background: repeating-linear-gradient(90deg, #0f172a 0, #0f172a 3px, transparent 3px, transparent 6px, #0f172a 6px, #0f172a 8px, transparent 8px, transparent 12px); opacity: 0.8; margin-top: auto; }}
  
  .btn-download {{ margin-top: 35px; padding: 14px 28px; background: #3b82f6; color: white; border: none; border-radius: 10px; font-size: 16px; font-weight: bold; cursor: pointer; display: flex; align-items: center; gap: 10px; transition: 0.2s; box-shadow: 0 4px 12px rgba(59,130,246,0.3); }}
  .btn-download:hover {{ background: #2563eb; transform: translateY(-2px); box-shadow: 0 6px 16px rgba(59,130,246,0.4); }}
</style></head><body>
<div style="display: flex; flex-direction: column; align-items: center;">
<div class="ticket" id="ticket-element">
  <div class="left">
    <div class="header">
      <div>
        <h2 class="brand-logo">TravelFusion<span>AI</span></h2>
        <div style="margin-top: 8px;"><span class="status-badge">✔ CONFIRMED</span></div>
      </div>
      <div class="pnr-box">
        <div class="pnr-title">BOOKING REF</div>
        <div class="pnr-val">TF-{booking_id}</div>
      </div>
    </div>
    
    <div class="route-box">
      <div style="width: 35%;">
        <div class="label">ORIGIN</div>
        <div class="city-code">{src[:3].upper()}</div>
        <div class="city-name">{src}</div>
        <div class="city-time">{formatted_time}</div>
      </div>
      <div class="icon-wrapper">
        <div class="route-line"></div>
        <span class="icon-symbol">{icon}</span>
        <div style="font-size: 10px; color: #64748b; font-weight: bold; margin-top: 8px; letter-spacing: 1px;">DIRECT</div>
      </div>
      <div style="width: 35%; text-align: right;">
        <div class="label">DESTINATION</div>
        <div class="city-code">{dst[:3].upper()}</div>
        <div class="city-name">{dst}</div>
        <div class="city-time">08:30 PM</div>
      </div>
    </div>
    
    <div class="row-data">
      <div style="width: 45%;">
        <div class="label">PASSENGER NAME</div>
        <div class="val" style="font-size: 17px;">{name}</div>
      </div>
      <div style="width: 25%;">
        <div class="label">DATE</div>
        <div class="val">{date[:10] if 'T' in date else date}</div>
      </div>
      <div style="width: 30%;">
        <div class="label">NO. OF TICKETS</div>
        <div class="val">{passengers_count} Passengers</div>
      </div>
    </div>
    
    <div class="row-data" style="border-top: 1px solid #f1f5f9; padding-top: 20px; margin-bottom: 0;">
      <div style="width: 45%;">
        <div class="label">OPERATOR</div>
        <div class="val">{operator}</div>
      </div>
      <div style="width: 25%;">
        <div class="label">AMOUNT PAID</div>
        <div class="val" style="color: #10b981; font-size: 18px;">₹{fare}</div>
      </div>
      <div style="width: 30%;">
        <div class="label">SEAT / GATE</div>
        <div class="val" style="color: #3b82f6;">Seat {seat} • Gate {gate}</div>
      </div>
    </div>
  </div>
  
  <div class="right">
    <div style="text-align: center; width: 100%;">
      <h3 style="margin: 0 0 15px 0; font-size: 17px; font-weight: 900; color: #0f172a; letter-spacing: -0.5px;">{ticket_type}</h3>
      <div class="qr-box" style="margin: 0 auto 20px auto;">
        <img src="https://api.qrserver.com/v1/create-qr-code/?size=110x110&data=TF-{booking_id}" alt="QR Code" width="110" height="110">
      </div>
      <div class="label">TICKET ID</div>
      <div class="val" style="margin-bottom: 15px;">TF-{booking_id}</div>
      <div class="label">PASSENGER</div>
      <div class="val" style="font-size: 13px;">{name}</div>
    </div>
    <div class="barcode"></div>
  </div>
</div>
<button class="btn-download" onclick="downloadPDF()">
    <svg width="22" height="22" fill="currentColor" viewBox="0 0 16 16"><path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/><path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/></svg>
    Download PDF E-Ticket
</button>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
<script>
function downloadPDF() {{
    const el = document.getElementById('ticket-element');
    const opt = {{
        margin: 0.2,
        filename: 'TravelFusion_ETicket_TF-{booking_id}.pdf',
        image: {{ type: 'jpeg', quality: 0.98 }},
        html2canvas: {{ scale: 2, useCORS: true }},
        jsPDF: {{ unit: 'in', format: 'letter', orientation: 'landscape' }}
    }};
    html2pdf().set(opt).from(el).save();
}}
</script>
</body></html>"""
    return html_content.encode('utf-8')

class NotificationService:
    @staticmethod
    def send_email_ticket(booking_id, email, details):
        """
        Sends a real HTML email containing the ticket details using smtplib.
        Configure SMTP_EMAIL and SMTP_PASSWORD in config.py.
        Falls back to console logging if SMTP is not configured.
        """
        sender_email = getattr(config, 'SMTP_EMAIL', '')
        sender_password = getattr(config, 'SMTP_PASSWORD', '')
        smtp_host = getattr(config, 'SMTP_HOST', 'smtp.gmail.com')
        smtp_port = getattr(config, 'SMTP_PORT', 587)
        
        passengers = details.get('passengers', [])
        if passengers:
            passenger_name = ", ".join([p.get('name', 'Passenger') for p in passengers])
        else:
            passenger_name = details.get('passenger_name', 'Passenger')
            
        source = details.get('source', 'Source')
        destination = details.get('destination', 'Destination')
        date = details.get('date', datetime.date.today().isoformat())
        fare = details.get('fare', 0)
        
        operator = details.get('operator', 'TravelFusion Select')
        seat = details.get('seat', 'AUTO')
        gate = details.get('gate', 'TBD')
        
        mode = details.get('mode', 'flight').lower()
        if mode == 'train':
            icon = '🚆'
            subject = f"🚆 Train Ticket Confirmed: PNR TF-{int(booking_id):05d} | TravelFusion"
        elif mode == 'bus':
            icon = '🚌'
            subject = f"🚌 Bus Ticket Confirmed: Ticket TF-{int(booking_id):05d} | TravelFusion"
        elif mode == 'ride':
            icon = '🚕'
            subject = f"🚕 Cab Receipt: Ride TF-{int(booking_id):05d} | TravelFusion"
        else:
            icon = '✈️'
            subject = f"✈️ E-Ticket Itinerary: Flight PNR TF-{int(booking_id):05d} | TravelFusion"
        
        passengers_count = len(passengers) if passengers else 1
        
        # Format time if present in date string
        formatted_time = "08:30 AM"
        if "T" in date:
            try:
                dt_obj = datetime.datetime.fromisoformat(date)
                formatted_time = dt_obj.strftime("%I:%M %p")
            except:
                formatted_time = date[11:16]

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #050914; padding: 20px; margin: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #0f172a; border: 1px solid #1e293b; border-radius: 16px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.5); }}
            
            .header {{ 
                background: linear-gradient(135deg, #1e293b, #0f172a); 
                padding: 30px; 
                border-bottom: 1px dashed rgba(255,255,255,0.1); 
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            .header-top {{ display: flex; align-items: center; gap: 15px; margin-bottom: 15px; }}
            .icon-box {{ background: linear-gradient(135deg, #3b82f6, #8b5cf6); border-radius: 14px; padding: 15px; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4); display: inline-block; font-size: 24px; line-height: 1; }}
            .header-logo {{ font-size: 28px; font-weight: 900; letter-spacing: -1px; margin: 0; color: #ffffff; }}
            .header-logo span {{ color: #3b82f6; }}
            .header-sub {{ color: #94a3b8; font-size: 10px; letter-spacing: 3px; font-weight: 800; text-transform: uppercase; margin-bottom: 5px; }}
            .badge-row {{ display: flex; align-items: center; gap: 10px; justify-content: center; }}
            .badge {{ background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid rgba(16,185,129,0.3); font-size: 10px; padding: 4px 8px; border-radius: 4px; font-weight: bold; }}
            
            .ticket-card {{ margin: 0; background: rgba(15, 23, 42, 0.8); padding: 30px; position: relative; z-index: 10; }}
            .booking-ref {{ text-align: center; color: #cbd5e1; font-size: 12px; margin-bottom: 30px; letter-spacing: 1px; }}
            .booking-ref strong {{ color: #fff; font-size: 24px; letter-spacing: 2px; text-shadow: 0 0 10px rgba(255,255,255,0.2); display: block; margin-top: 5px; }}
            
            .divider {{ border-top: 1px dashed #334155; margin: 25px 0; }}
            .detail-label {{ color: #64748b; font-size: 10px; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; margin-bottom: 5px; }}
            .detail-val {{ color: #e2e8f0; font-size: 16px; font-weight: bold; }}
            
            .route {{ background: linear-gradient(to right, rgba(15,23,42,0.8), rgba(30,58,138,0.3), rgba(15,23,42,0.8)); border: 1px solid rgba(59,130,246,0.2); border-radius: 12px; padding: 25px; margin-bottom: 25px; display: flex; align-items: center; justify-content: space-between; box-shadow: inset 0 0 20px rgba(0,0,0,0.5); }}
            .city {{ text-align: center; width: 35%; }}
            .city-code {{ font-size: 28px; font-weight: 900; color: #f8fafc; line-height: 1; }}
            .city-name {{ font-size: 13px; color: #94a3b8; margin-top: 5px; }}
            .city-time {{ font-size: 16px; font-weight: 800; color: #38bdf8; margin-top: 8px; letter-spacing: 1px; }}
            
            .plane {{ color: #38bdf8; font-size: 28px; position: relative; filter: drop-shadow(0 0 10px rgba(56,189,248,0.5)); text-align: center; width: 30%; }}
            .plane-label {{ font-size: 10px; color: #64748b; font-weight: bold; letter-spacing: 2px; margin-bottom: 5px; }}
            .line-wrap {{ display: flex; align-items: center; justify-content: center; }}
            .line-left {{ height: 2px; width: 40px; background: linear-gradient(to right, transparent, rgba(56, 189, 248, 0.5)); }}
            .line-right {{ height: 2px; width: 40px; background: linear-gradient(to left, transparent, rgba(56, 189, 248, 0.5)); }}
        </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div style="text-align: center; margin-bottom: 15px;">
                        <div class="icon-box">{icon}</div>
                    </div>
                    <div style="text-align: center;">
                        <div class="header-sub">E-Ticket Itinerary Receipt</div>
                        <h1 class="header-logo">TravelFusion<span>AI</span></h1>
                        <div class="badge-row" style="margin-top: 10px;">
                            <span class="badge">CONFIRMED</span>
                            <span style="color: #64748b; font-size: 12px;">•</span>
                            <span style="color: #e2e8f0; font-size: 12px; font-weight: 600; letter-spacing: 1px;">PREMIUM CLASS</span>
                        </div>
                    </div>
                </div>
                
                <div class="ticket-card">
                    <div class="booking-ref">BOOKING REF<br><strong>TF-{int(booking_id):05d}</strong></div>
                    
                    <div class="route">
                        <div class="city">
                            <div class="city-code">{source[:3].upper()}</div>
                            <div class="city-name">{source.split(',')[0]}</div>
                            <div class="city-time">{formatted_time}</div>
                        </div>
                        <div class="plane">
                            <div class="plane-label">DIRECT</div>
                            <div class="line-wrap">
                                <div class="line-left"></div>
                                <div style="margin: 0 10px;">{icon}</div>
                                <div class="line-right"></div>
                            </div>
                        </div>
                        <div class="city">
                            <div class="city-code">{destination[:3].upper()}</div>
                            <div class="city-name">{destination.split(',')[0]}</div>
                            <div class="city-time">08:30 PM</div>
                        </div>
                    </div>
                    
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding-bottom: 20px; width: 40%;">
                                <div class="detail-label">PASSENGER</div>
                                <div class="detail-val">{passenger_name}</div>
                            </td>
                            <td style="padding-bottom: 20px; width: 30%;">
                                <div class="detail-label">NO. OF TICKETS</div>
                                <div class="detail-val">{passengers_count} <span style="font-size: 12px; color: #94a3b8; font-weight: normal;">Pass</span></div>
                            </td>
                            <td style="padding-bottom: 20px; width: 30%;">
                                <div class="detail-label">DATE</div>
                                <div class="detail-val">{date[:10] if 'T' in date else date}</div>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding-bottom: 10px;">
                                <div class="detail-label">OPERATOR</div>
                                <div class="detail-val">{operator}</div>
                            </td>
                            <td style="padding-bottom: 10px;" colspan="2">
                                <div class="detail-label">SEAT / GATE</div>
                                <div class="detail-val" style="color: #38bdf8;">Seat {seat} • Gate {gate}</div>
                            </td>
                        </tr>
                    </table>
                    
                    <div class="divider"></div>
                    <div style="text-align: center;">
                        <div class="detail-label">AMOUNT PAID</div>
                        <div class="detail-val" style="color: #10b981; font-size: 24px;">₹{fare}</div>
                    </div>
                    
                    <p style="text-align: center; font-size: 13px; color: #94a3b8; margin-top: 25px; background: rgba(59,130,246,0.1); padding: 10px; border-radius: 8px; border: 1px solid rgba(59,130,246,0.2);">
                        📎 Your full E-Ticket Boarding Pass is attached as a file.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Attempt real email delivery
        if sender_email and sender_password and email:
            try:
                msg = MIMEMultipart('mixed')
                msg['Subject'] = subject
                msg['From'] = f"TravelFusion AI <{sender_email}>"
                msg['To'] = email
                msg['Reply-To'] = sender_email
                msg['Date'] = email_utils.formatdate(localtime=True)
                msg['Message-ID'] = email_utils.make_msgid(domain='travelfusion.ai')
                
                alt = MIMEMultipart('alternative')
                
                # Plain text fallback (Crucial for bypassing Spam filters)
                text_body = f"TravelFusion AI - Booking Confirmed!\nBooking ID: TF-BK-{booking_id}\nPassenger: {passenger_name}\nRoute: {source} -> {destination}\nDate: {date}\nFare: INR {fare}\n\nView your E-Ticket on the TravelFusion dashboard."
                alt.attach(MIMEText(text_body, 'plain'))
                
                # Attach HTML body
                alt.attach(MIMEText(html_body, 'html'))
                
                msg.attach(alt)
                
                # Generate and Attach HTML Ticket
                try:
                    html_ticket_bytes = generate_html_ticket(details, booking_id)
                    part = MIMEApplication(html_ticket_bytes, Name=f"TravelFusion_Boarding_Pass_{booking_id}.html")
                    part['Content-Disposition'] = f'attachment; filename="TravelFusion_Boarding_Pass_{booking_id}.html"'
                    msg.attach(part)
                except Exception as e:
                    print("HTML Attachment failed:", e)
                
                # Connect and send
                server = smtplib.SMTP(smtp_host, smtp_port)
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, email, msg.as_string())
                server.quit()
                
                print(f"\n{'='*50}")
                print(f"[EMAIL SENT SUCCESSFULLY] to: {email}")
                print(f"Subject: {subject}")
                print(f"{'='*50}\n")
                return {"success": True, "method": "smtp", "message": f"Email sent to {email}"}
                
            except Exception as e:
                print(f"\n{'='*50}")
                print(f"[EMAIL SEND FAILED] to: {email}")
                print(f"Error: {e}")
                print(f"{'='*50}\n")
                return {"success": False, "method": "smtp", "message": f"Email failed: {str(e)}"}
        else:
            # Fallback: Console log if SMTP not configured
            print(f"\n{'='*50}")
            print(f"[EMAIL NOT CONFIGURED] SMTP credentials not set in config.py")
            print(f"Would have sent to: {email}")
            print(f"Subject: {subject}")
            print(f"{'='*50}\n")
            return {"success": False, "method": "not_configured", "message": "SMTP not configured in config.py"}

    @staticmethod
    def send_sos_email(alert_id, email, traveler_name, emergency_type, lat, lng, booking_info=""):
        """
        Sends a real SOS alert email to emergency contacts.
        """
        sender_email = getattr(config, 'SMTP_EMAIL', '')
        sender_password = getattr(config, 'SMTP_PASSWORD', '')
        smtp_host = getattr(config, 'SMTP_HOST', 'smtp.gmail.com')
        smtp_port = getattr(config, 'SMTP_PORT', 587)
        
        gmaps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
        type_text = emergency_type.upper().replace('_', ' ')
        
        subject = f"🚨 EMERGENCY SOS ALERT - {traveler_name}"
        
        html_body = f"""
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 30px;">
            <div style="max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #1e293b, #0f172a); border: 2px solid #ef4444; border-radius: 16px; padding: 30px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <span style="font-size: 48px;">🚨</span>
                    <h1 style="color: #ef4444; margin: 10px 0;">EMERGENCY SOS ALERT</h1>
                </div>
                
                <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
                    <table style="width: 100%; color: #cbd5e1; font-size: 15px;">
                        <tr><td style="padding: 8px 0; color: #94a3b8;">👤 Person</td><td style="padding: 8px 0; color: #f8fafc; font-weight: 700;">{traveler_name}</td></tr>
                        <tr><td style="padding: 8px 0; color: #94a3b8;">⚠️ Type</td><td style="padding: 8px 0; color: #ef4444; font-weight: 700;">{type_text}</td></tr>
                        {f'<tr><td style="padding: 8px 0; color: #94a3b8;">🔖 Trip</td><td style="padding: 8px 0; color: #f8fafc;">{booking_info}</td></tr>' if booking_info else ''}
                    </table>
                </div>
                
                <div style="text-align: center; margin-bottom: 20px;">
                    <a href="{gmaps_link}" style="display: inline-block; background: #ef4444; color: white; text-decoration: none; padding: 15px 30px; border-radius: 10px; font-weight: 700; font-size: 16px;">📍 VIEW LIVE LOCATION ON MAP</a>
                </div>
                
                <p style="color: #94a3b8; text-align: center; font-size: 13px;">Please contact them or local authorities immediately!</p>
                
                <div style="text-align: center; color: #475569; font-size: 12px; border-top: 1px solid #1e293b; padding-top: 15px; margin-top: 20px;">
                    <p>TravelFusion AI Emergency System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        if sender_email and sender_password and email:
            try:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = f"TravelFusion SOS <{sender_email}>"
                msg['To'] = email
                msg.attach(MIMEText(html_body, 'html'))
                
                server = smtplib.SMTP(smtp_host, smtp_port)
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, email, msg.as_string())
                server.quit()
                
                print(f"[SOS EMAIL SENT] to: {email}")
                return {"success": True, "method": "smtp"}
            except Exception as e:
                print(f"[SOS EMAIL FAILED] to: {email} | Error: {e}")
                return {"success": False, "method": "smtp", "message": str(e)}
        else:
            print(f"[SOS EMAIL NOT CONFIGURED] Would have sent to: {email}")
            return {"success": False, "method": "not_configured"}
