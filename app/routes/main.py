from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app.models import Offer, Ticket, User, db
from flask_login import login_required, current_user
import os
import qrcode
from io import BytesIO
from flask import session
from pprint import pprint
import base64
import stripe
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import UpdateProfileForm, ChangePasswordForm, ResetPasswordRequestForm, ResetPasswordForm
from flask_mail import Message
from app import mail

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
        panier[str(offre_id)]['stripe_price_id']=offres[offre_id].stripe_price_id
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
        print(offres[item].stripe_price_id)

    #session.clear()
    return render_template('panier.html', panier=panier, total=total, offres=offres)

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


@main_bp.route('/remove_from_panier/<int:offre_id>', methods=['POST'])
def remove_from_panier(offre_id):
    panier = session.get('panier', {})
    del panier[str(offre_id)]
    session['panier'] = panier

    # Rediriger vers la page du panier
    return redirect(url_for('main.panier'))

# @main_bp.route('/remove_from_panier/<int:offre_id>', methods=['POST'])
# def remove_from_panier(offre_id):
#     panier = session.get('panier', {})
#     if str(offre_id) in panier:
#         del panier[str(offre_id)]
#     session['panier'] = panier
#     total_items = sum(item['quantite'] for item in panier.values())
#     response = {
#         'success': True,
#         'total_items': total_items
#     }
#     return jsonify(response), 200

###################################################################################################
###################################################################################################

######################## -----  Booking & Payment  ----- ##########################################


# @main_bp.route('/purchase', methods=['GET', 'POST'])
# @login_required
# def purchase():
#     """
# Gère le processus d'achat pour les utilisateurs.

# Cette fonction permet aux utilisateurs d'initier un paiement via Stripe,
# de générer des QR codes et de créer des tickets basés sur les offres dans leur panier.

# Méthodes :
#     GET : Affiche le formulaire d'achat et initie le paiement.
#     POST : Gère les requêtes de paiement (si implémenté).

# Returns:
#     Redirect vers la page de paiement Stripe ou affiche une erreur si le panier est vide.

# Raises:
#     Exception : En cas d'erreur lors de la création de la session de paiement.
# """
        
#     # Récupérer le panier
#     panier = get_panier()
#     if not panier:
#         return "Votre panier est vide."

#     # Récupérer l'offre depuis le panier
#     offer_id = list(panier.keys())[0]
#     offer_details = panier[offer_id]
#     quantity = offer_details['quantite'] 
#     price = offer_details['stripe_price_id']

#     # Récupérer l'offre
#     offer = Offer.query.get_or_404(offer_id)

#     # Créer la session de paiement Stripe
#     try:
#         checkout_session = stripe.checkout.Session.create(
#             line_items=[
#                 {
#                     'price': price,  # Remplacer par le bon Price ID
#                     'quantity': quantity,
#                 },
#             ],
#             mode='payment',
#             success_url=url_for('main.success', _external=True)+ '?session_id={CHECKOUT_SESSION_ID}',
#             cancel_url=url_for('main.cancel', _external=True)
#         )
#     except Exception as e:
#         return str(e)

#     # Rediriger vers la page de paiement Stripe
#     return redirect(checkout_session.url, code=303)

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

    # Créer les éléments de la ligne pour chaque offre dans le panier
    line_items = []
    for offer_id, offer_details in panier.items():
        quantity = offer_details['quantite']
        price = offer_details['stripe_price_id']
        line_items.append({
            'price': price,
            'quantity': quantity,
        })

    # Vérifier s'il y a des items à acheter
    if not line_items:
        return "Votre panier est vide."

    # Créer la session de paiement Stripe
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url=url_for('main.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
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
    # recuperer l'ID de l'utilisateur connecté dans la session
    user_id = current_user.id

    # Si l'utilisateur est connecté, récupérez ses informations de la base de données
    if user_id:
        user = User.query.get(user_id)  # Récupérer l'utilisateur de la base de données
        if user:
            return render_template('profile.html', user=user)
        else:
            return "Utilisateur non trouvé", 404
    else:
        return "Veuillez vous connecter pour accéder à votre profil", 401
    

@main_bp.route('/edit-profile', methods=['GET', 'POST'])
def update_profile():
    user_id = current_user.id

    if not user_id:
        return "Veuillez vous connecter pour accéder à cette page", 401

    user = User.query.get(user_id)

    if not user:
        return "Utilisateur non trouvé", 404

    form = UpdateProfileForm(obj=user)

    if form.validate_on_submit():
        user.firstname = form.firstname.data
        user.lastname = form.lastname.data
        user.email = form.email.data
        db.session.commit()
        flash("Profil mis à jour avec succès")
        return redirect(url_for('main.profile'))

    return render_template('edit_profile.html', user=user, form=form)


@main_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    user_id = current_user.id
    user = User.query.get(user_id)

    if not user:
        return "Utilisateur non trouvé", 404

    form = ChangePasswordForm()

    if form.validate_on_submit():
        # Vérification et mise à jour du mot de passe
        if check_password_hash(user.password_hash, form.current_password.data):
            user.password_hash = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash("Mot de passe mis à jour avec succès.")
            return redirect(url_for('main.profile'))
        else:
            flash("Le mot de passe actuel est incorrect.")

    return render_template('change_password.html', user=user, form=form)


@main_bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Créer un token de réinitialisation
            token = user.get_reset_password_token()  # Assurez-vous d'implémenter cette méthode dans votre modèle User
            send_reset_email(user.email, token)
            flash('Un email de réinitialisation a été envoyé.', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('Aucun utilisateur trouvé avec cette adresse e-mail.', 'danger')
    
    return render_template('reset_password_request.html', form=form)

def send_reset_email(email, token):
    msg = Message('Réinitialisation du mot de passe',
                  sender='olympic.studi@gmail.com',
                  recipients=[email])
    msg.body = f'''Pour réinitialiser votre mot de passe, visitez le lien suivant :
{url_for('main.reset_password', token=token, _external=True)}
Si vous n'avez pas demandé de réinitialisation, ignorez cet email.
'''
    mail.send(msg)


@main_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_reset_password_token(token)  # Implémentez cette méthode pour vérifier le token
    if not user:
        flash('Le lien de réinitialisation est invalide ou a expiré.', 'danger')
        return redirect(url_for('auth.login'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.new_password.data)
        db.session.commit()
        flash('Votre mot de passe a été mis à jour.', 'success')
        return redirect(url_for('main.home'))

    return render_template('reset_password.html', form=form, token=token)


@main_bp.route('/test-email')
def test_email():
    msg = Message('Test Email', recipients=['destinataire@example.com'])
    msg.body = 'Ceci est un e-mail de test.'
    mail.send(msg)
    return 'E-mail envoyé!'


@main_bp.route('/conditions')
def conditions():
    return render_template('conditions.html', update_date="15 octobre 2024", support_email="olympic.studi@gmail.com")

@main_bp.route('/add/<int:a>/<int:b>')
def add(a, b):
    return str(a+b)

