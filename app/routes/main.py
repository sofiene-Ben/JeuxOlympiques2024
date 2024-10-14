from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app.models import Offer, Ticket, db
from flask_login import login_required, current_user
import os
import qrcode
from io import BytesIO
from flask import session
from pprint import pprint
import base64
import stripe

stripe.api_key = 'sk_test_51Q9MqRP78S9tzF5jAVOMzkwNFuYEdOKE7dKEe5OMehFgmh4bSEDMThoX9OFsN3bfnSIHwknpuzN9VgKTbufEhims00Wsn2WJXQ'

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


# Vider le panier
def clear_panier():
    # Vérifie si le panier existe dans la session
    if 'panier' in session:
        # Supprime le panier de la session
        session.pop('panier', None)


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

######################## -----  Home  ----- ##########################################
@main_bp.route('/')
def home():
    return render_template('home.html')

########################################################################################
########################################################################################

######################## -----  Offers  ----- ##########################################
@main_bp.route('/offers')
def offers():
    offers = Offer.query.all()  # Récupérer toutes les offres
    return render_template('offres.html',offers=offers)

@main_bp.route('/details_offre/<int:offer_id>')
def details_offre(offer_id):
    # Rechercher l'offre dans la base de données avec offer_id
    offer = Offer.query.get_or_404(offer_id)
    return render_template('details_offre.html', offre=offer)

######################################################################################
######################################################################################

######################## -----  Cart  ----- ##########################################
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

# @main_bp.route('/add_to_cart/<int:offer_id>', methods=['POST'])
# def add_to_cart(offer_id):
#     add_to_panier(offer_id,1)
#     # Ajouter l'offre au panier de l'utilisateur (à implémenter)
#     print('Offre ajoutée au panier!', 'success')
#     return {'success': True, 'message': 'Offre ajoutée au panier!'}

# ############ test add cart

@main_bp.route('/add_to_cart/<int:offer_id>', methods=['POST'])
def add_to_cart(offer_id):
    add_to_panier(offer_id, 1)  # Ajouter l'offre au panier de l'utilisateur
    response = {
        'success': True,
        'message': 'Offre ajoutée au panier !'
    }
    return jsonify(response), 200






# @main_bp.route('/update_panier/<int:offre_id>', methods=['POST'])
# def update_panier(offre_id):
#     panier = session.get('panier', {})
#     btn = request.form.get('quantite',1)
   
#     if btn=="+":
#         if str(offre_id) in panier:
#             panier[str(offre_id)]['quantite'] += 1
#     else:
#         if str(offre_id) in panier:
#             if panier[str(offre_id)]['quantite'] > 1:
#                 panier[str(offre_id)]['quantite'] -= 1
#             else:
#                 del panier[str(offre_id)]
#     session['panier'] = panier
#     # Logique de mise à jour du panier
#     return redirect(url_for('main.panier'))   

# ############ test update cart api

@main_bp.route('/update_panier/<int:offre_id>', methods=['POST'])
def update_panier(offre_id):
    panier = session.get('panier', {})
    offres = {offre.id: offre for offre in Offer.query.all()}  # Remplacez `Offre` par le nom de votre modèle
    action = request.form.get('action')  # Utilisez 'action' au lieu de 'quantite'
    
    if action == "+":
        if str(offre_id) in panier:
            panier[str(offre_id)]['quantite'] += 1
        else:
            # Si l'article n'est pas dans le panier, vous pouvez l'ajouter ici
            # Exemple : panier[str(offre_id)] = {'quantite': 1, 'prix': prix_de_l_offre}
            pass
    elif action == "-":
        if str(offre_id) in panier:
            if panier[str(offre_id)]['quantite'] > 1:
                panier[str(offre_id)]['quantite'] -= 1
            else:
                del panier[str(offre_id)]
    else:
        return jsonify({'success': False, 'message': 'Action inconnue.'}), 400

    # Mettez à jour le panier dans la session
    session['panier'] = panier

    total_par_offre = calculer_total(panier, offres)
    
    # Renvoie une réponse JSON indiquant le succès de l'opération
    return jsonify({'success': True, 'message': 'Quantité mise à jour avec succès.', 'total': total_par_offre, 'newQuantity': panier.get(str(offre_id), {}).get('quantite', 0)})


# @main_bp.route('/remove_from_panier/<int:offre_id>', methods=['POST'])
# def remove_from_panier(offre_id):
#     panier = session.get('panier', {})
#     del panier[str(offre_id)]
#     session['panier'] = panier

#     # Rediriger vers la page du panier
#     return redirect(url_for('main.panier'))

@main_bp.route('/remove_from_panier/<int:offre_id>', methods=['POST'])
def remove_from_panier(offre_id):
    panier = session.get('panier', {})
    if str(offre_id) in panier:
        del panier[str(offre_id)]
    session['panier'] = panier
    total_items = sum(item['quantite'] for item in panier.values())
    response = {
        'success': True,
        'total_items': total_items
    }
    return jsonify(response), 200

###################################################################################################
###################################################################################################

######################## -----  Booking & Payment  ----- ##########################################


@main_bp.route('/purchase', methods=['GET', 'POST'])
@login_required
def purchase():
    """
Gère le processus d'achat pour les utilisateurs.

Cette fonction permet aux utilisateurs d'initier un paiement via Stripe,
de générer des QR codes et de créer des tickets basés sur les offres dans leur panier.

Méthodes :
    GET : Affiche le formulaire d'achat et initie le paiement.
    POST : Gère les requêtes de paiement (si implémenté).

Returns:
    Redirect vers la page de paiement Stripe ou affiche une erreur si le panier est vide.

Raises:
    Exception : En cas d'erreur lors de la création de la session de paiement.
"""
        
    # Récupérer le panier
    panier = get_panier()
    if not panier:
        return "Votre panier est vide."

    # Récupérer l'offre depuis le panier
    offer_id = list(panier.keys())[0]
    offer_details = panier[offer_id]
    quantity = offer_details['quantite'] 

    # Récupérer l'offre
    offer = Offer.query.get_or_404(offer_id)

    # Créer la session de paiement Stripe
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': 'price_1Q9MsCP78S9tzF5jaml3JRCV',  # Remplacer par le bon Price ID
                    'quantity': quantity,
                },
            ],
            mode='payment',
            success_url=url_for('main.success', _external=True)+ '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('main.cancel', _external=True)
        )
    except Exception as e:
        return str(e)

    # Rediriger vers la page de paiement Stripe
    return redirect(checkout_session.url, code=303)



@main_bp.route('/success')
@login_required
def success():
    # Vérifier que la session de paiement est réussie
    session_id = request.args.get('session_id')
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status != 'paid':
            return "Le paiement n'a pas été validé."
    except Exception as e:
        return str(e)

  # 3. Récupérer le panier actuel de l'utilisateur
    panier = get_panier()
    if not panier:
        # Si le panier est vide ou déjà traité, afficher un message
        return "Le panier est vide ou a déjà été traité."

    for offer_id, offer_details in panier.items():
        quantity = offer_details['quantite']  # Quantité de l'offre
        offer = Offer.query.get_or_404(offer_id)  # Récupérer l'offre depuis la base de données

        for _ in range(quantity):

            # 5. Générer les clés et le QR code pour chaque ticket
            key1 = current_user.key
            key2 = os.urandom(16).hex()
            final_key = key1 + key2
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

            # 6. Créer un ticket pour chaque unité de l'offre
            ticket = Ticket(
                user_id=current_user.id,
                offer_id=offer.id,
                payment_status='Paid',
                key1=key1,
                key2=key2,
                final_key=final_key,
                qr_code=qr_code
            )
            db.session.add(ticket)  # Ajouter le ticket à la session de base de données

    # 7. Vider le panier de l'utilisateur après avoir créé tous les tickets
    clear_panier()
    db.session.commit()  # Enregistrer les modifications en base de données
    
    # 8. Afficher un message de succès
    print('Achat réussi! Vos e-tickets sont générés.', 'success')
    return render_template('success.html')

@main_bp.route('/cancel')
def cancel():
    return render_template('cancel.html')


@main_bp.route('/ticket')
@login_required
def ticket():
    # Récupération de tous les tickets de l'utilisateur actuel
    offers = Offer.query.all()
    tickets = Ticket.query.filter_by(user_id=current_user.id).all()
    # Préparer les données encodées pour chaque ticket
    ticket_data = []
    for ticket in tickets:
        if ticket.qr_code:

            offer = Offer.query.get(ticket.offer_id)

            # Encodage des données en Base64
            encoded_data = base64.b64encode(ticket.qr_code).decode('utf-8')
            ticket_data.append({
                'id': ticket.id,
                'date': ticket.created_at,
                'offer_name': offer.name if offer else "Offre inconnue",
                'encoded_data': encoded_data,
                # Ajoute d'autres informations si nécessaire (par ex. date, type de ticket, etc.)
                # 'event': ticket.event_name  # Exemple d'une autre info à afficher
            })

    return render_template('ticket.html', image_data=ticket_data, offers=offers)

###############################################################################################
###############################################################################################
 
######################## -----  User Settings  ----- ##########################################
@main_bp.route('/profile')
def profile():
    # logiques du profil
    return render_template('profile.html')