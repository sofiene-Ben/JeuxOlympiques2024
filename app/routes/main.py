from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import Offer, Ticket, db
from flask_login import login_required, current_user
import os
import qrcode
from io import BytesIO
from flask import session
from pprint import pprint

main_bp = Blueprint('main', __name__)

# Ajouter une offre au panier
def add_to_panier(offre_id, quantite):
    panier = session.get('panier', {})
    
    if str(offre_id) in panier:
        
        panier[str(offre_id)]['quantite'] += int(quantite)
        
    else:
        offres = {offre.id: offre for offre in Offer.query.all()}  # Remplacez `Offre` par le nom de votre modèle
    
        panier[str(offre_id)] = {'quantite': int(quantite)}
        panier[str(offre_id)]['name']=offres[offre_id].name
        panier[str(offre_id)]['price']=offres[offre_id].price
    session['panier'] = panier
# Récupérer le panier
def get_panier():
    return session.get('panier', {})

# Calculer le total du panier
def calculer_total(panier, offres):
    total = 0
    for offre_id, item in panier.items():
        if int(offre_id) in list(offres.keys()):  # Vérifiez si l'offre existe
            total += item['quantite'] * offres[int(offre_id)].price
        else:
            print(f"Avertissement : L'offre avec l'ID {offre_id} n'existe pas dans la base de données.")
    return total

# Supprimer une offre du panier
def remove_from_panier(offre_id):
    panier = session.get('panier', {})
    if offre_id in panier:
        del panier[offre_id]
        session['panier'] = panier

@main_bp.route('/')
def home():
    return render_template('home.html')

@main_bp.route('/offers')
def offers():
    offers = Offer.query.all()  # Récupérer toutes les offres
    return render_template('offres.html',offers=offers)

@main_bp.route('/add_to_cart/<int:offer_id>', methods=['POST'])
@login_required
def add_to_cart(offer_id):
    add_to_panier(offer_id,1)
    # Ajouter l'offre au panier de l'utilisateur (à implémenter)
    print('Offre ajoutée au panier!', 'success')
    return redirect(url_for('main.offers'))

@main_bp.route('/details_offre/<int:offer_id>')
def details_offre(offer_id):
    # Rechercher l'offre dans la base de données avec offer_id
    offer = Offer.query.get_or_404(offer_id)
    return render_template('details_offre.html', offre=offer)

@main_bp.route('/purchase', methods=['GET', 'POST'])
@login_required
def purchase():
    # Implémenter la logique d'achat (mock paiement)
    if request.method == 'POST':
        # Simuler le paiement
        # Générer les clés
        key1 = os.urandom(16).hex()
        key2 = os.urandom(16).hex()
        final_key = key1 + key2
        # Générer le QR code
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5
        )
        qr.add_data(final_key)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buf = BytesIO()
        img.save(buf)
        qr_code = buf.getvalue()
        # Créer le ticket
        # Récupérer l'offre depuis le panier (simplifié)
        offer_id = request.form.get('offer_id')
        offer = Offer.query.get_or_404(offer_id)
        ticket = Ticket(
            user_id=current_user.id,
            offer_id=offer.id,
            payment_status='Paid',
            key1=key1,
            key2=key2,
            final_key=final_key,
            qr_code=qr_code
        )
        db.session.add(ticket)
        db.session.commit()
        flash('Achat réussi! Votre e-ticket est généré.', 'success')
        return redirect(url_for('main.home'))
    offers = Offer.query.all()
    return render_template('purchase.html', offers=offers)

@main_bp.route('/profile')
def profile():
    # logiques du profil
    return render_template('profile.html')


@main_bp.route('/panier')
def panier():
    
    offres = {offre.id: offre for offre in Offer.query.all()}  # Remplacez `Offre` par le nom de votre modèle
    print(offres)
    panier = get_panier()
    #offres = {offre.id: offre for offre in Offer.query.all()}  # Charger toutes les offres
    
    total = calculer_total(panier, offres)
    print(panier)
    for item in offres:
        print(offres[item].name)
    #session.clear()
    return render_template('panier.html', panier=panier, total=total)
    
@main_bp.route('/update_panier/<int:offre_id>', methods=['POST'])
def update_panier(offre_id):
    # Logique de mise à jour du panier
    return "Panier mis à jour"    

@main_bp.route('/remove_from_panier/<int:offre_id>', methods=['POST'])
def remove_from_panier(offre_id):
    # Logique pour supprimer l'offre du panier
    return "Offre supprimée du panier"