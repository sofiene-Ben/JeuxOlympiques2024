# app/routes/cart.py
from flask import Blueprint, session, redirect, url_for

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    return render_template('cart.html', cart=cart)

@cart_bp.route('/add_to_cart/<int:offer_id>', methods=['POST'])
def add_to_cart(offer_id):
    cart = session.get('cart', [])
    cart.append(offer_id)  # Ajoutez l'ID de l'offre au panier
    session['cart'] = cart
    return redirect(url_for('cart.view_cart'))
