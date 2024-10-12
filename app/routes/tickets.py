# app/routes/tickets.py
from flask import Blueprint, render_template
import qrcode
from io import BytesIO
import base64

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/generate_ticket/<int:offer_id>')
def generate_ticket(offer_id):
    # Logique pour générer un e-ticket
    ticket_info = f"Ticket pour l'offre {offer_id}"
    
    # Génération du QR code
    qr = qrcode.make(ticket_info)
    buffered = BytesIO()
    qr.save(buffered, format="PNG")
    qr_image = base64.b64encode(buffered.getvalue()).decode()

    return render_template('ticket.html', qr_image=qr_image)
